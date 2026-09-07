from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from .dgs_semantic_mapper import DGSSemanticMapper


# ============================================================================
# CONFIGURATION
# ============================================================================

DEFAULT_LANGUAGE = "dgs"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class LexiconCandidate:
    concept: str
    gloss: str | None
    file_path: str
    status: str
    confidence: float
    source: str | None
    data: dict[str, Any]


@dataclass
class ResolvedSign:
    element_id: str
    source_unit: int

    requested_concept: str
    requested_gloss: str | None
    semantic_role: str

    resolved_concept: str | None
    resolved_gloss: str | None

    status: str
    confidence: float

    sign_data: dict[str, Any] | None

    resolution_method: str
    usable_for_animation: bool

    warnings: list[str] = field(
        default_factory=list
    )


# ============================================================================
# RESOLVER
# ============================================================================

class DGSLexiconResolver:
    """
    Resolves DGS-oriented semantic elements against the local DGS lexicon.

    Input:

        DGS Semantic Mapper output

    Output:

        Resolved signs backed by JSON files in:

            data/signs/dgs/

    Important:

        This resolver does NOT claim that a prototype JSON is an official
        DGS sign.

        It preserves:
            - status
            - confidence
            - source
            - raw sign definition

    Resolution priority:

        1. exact concept
        2. exact gloss / filename
        3. normalized concept
        4. semantic-role-compatible concept
        5. no match

    The raw JSON is preserved so later motion/handshape compilers can use
    the complete sign definition.
    """

    def __init__(
        self,
        semantic_mapper: DGSSemanticMapper | None = None,
        lexicon_root: str | Path | None = None,
    ) -> None:

        self.semantic_mapper = (
            semantic_mapper
            or DGSSemanticMapper()
        )

        if lexicon_root is None:

            # From:
            # backend/translation/dgs_lexicon_resolver.py
            #
            # go to project root, then:
            # data/signs/dgs

            project_root = (
                Path(__file__)
                .resolve()
                .parents[2]
            )

            lexicon_root = (
                project_root
                / "data"
                / "signs"
                / DEFAULT_LANGUAGE
            )

        self.lexicon_root = Path(
            lexicon_root
        )

        self._lexicon_cache: list[
            LexiconCandidate
        ] | None = None

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def resolve(
        self,
        dgs_mapping_or_source: (
            str
            | dict[str, Any]
        ),
    ) -> dict[str, Any]:
        """
        Accept:

            raw lyrics

        OR:

            DGSSemanticMapper output.
        """

        if isinstance(
            dgs_mapping_or_source,
            str,
        ):

            mapping = (
                self.semantic_mapper.analyze(
                    dgs_mapping_or_source
                )
            )

        elif isinstance(
            dgs_mapping_or_source,
            dict,
        ):

            mapping = (
                dgs_mapping_or_source
            )

        else:

            raise TypeError(
                "dgs_mapping_or_source must be "
                "a string or dictionary"
            )

        lexicon = self._load_lexicon()

        resolved_signs: list[
            ResolvedSign
        ] = []

        for unit in mapping.get(
            "units",
            [],
        ):

            for element in unit.get(
                "elements",
                [],
            ):

                resolved = (
                    self._resolve_element(
                        unit,
                        element,
                        lexicon,
                    )
                )

                resolved_signs.append(
                    resolved
                )

        song_plan = (
            self._build_song_plan(
                mapping,
                resolved_signs,
            )
        )

        return {
            "status": self._determine_status(
                resolved_signs,
                mapping,
            ),
            "source_language": mapping.get(
                "source_language"
            ),
            "target_language": (
                mapping.get(
                    "target_language",
                    "DGS",
                )
            ),
            "target_language_name": mapping.get(
                "target_language_name"
            ),
            "resolved_signs": [
                asdict(sign)
                for sign
                in resolved_signs
            ],
            "song_plan": song_plan,
            "lexicon": {
                "root": str(
                    self.lexicon_root
                ),
                "file_count": len(
                    lexicon
                ),
            },
            "resolution_policy": {
                "prototype_signs_allowed": True,
                "prototype_signs_marked_as_prototype": True,
                "official_dgs_claimed": False,
                "raw_sign_definition_preserved": True,
            },
            "metadata": {
                "unit_count": len(
                    mapping.get(
                        "units",
                        [],
                    )
                ),
                "element_count": sum(
                    len(
                        unit.get(
                            "elements",
                            [],
                        )
                    )
                    for unit
                    in mapping.get(
                        "units",
                        [],
                    )
                ),
                "resolved_count": sum(
                    1
                    for sign
                    in resolved_signs
                    if sign.resolved_concept
                    is not None
                ),
                "unresolved_count": sum(
                    1
                    for sign
                    in resolved_signs
                    if sign.resolved_concept
                    is None
                ),
                "animation_usable_count": sum(
                    1
                    for sign
                    in resolved_signs
                    if sign.usable_for_animation
                ),
            },
        }

    # ------------------------------------------------------------------
    # LOAD LEXICON
    # ------------------------------------------------------------------

    def _load_lexicon(
        self,
    ) -> list[LexiconCandidate]:

        if self._lexicon_cache is not None:
            return self._lexicon_cache

        if not self.lexicon_root.exists():

            self._lexicon_cache = []

            return self._lexicon_cache

        candidates: list[
            LexiconCandidate
        ] = []

        for json_path in sorted(
            self.lexicon_root.glob(
                "*.json"
            )
        ):

            try:

                with json_path.open(
                    "r",
                    encoding="utf-8",
                ) as file:

                    data = json.load(
                        file
                    )

            except (
                OSError,
                json.JSONDecodeError,
            ):

                # Ignore invalid files here.
                # The resolver will expose the actual valid files.
                continue

            if not isinstance(
                data,
                dict,
            ):
                continue

            concept = str(
                data.get(
                    "concept",
                    json_path.stem,
                )
            ).strip()

            gloss = data.get(
                "gloss"
            )

            if gloss is not None:
                gloss = str(
                    gloss
                ).strip()

            status = str(
                data.get(
                    "status",
                    "unknown",
                )
            )

            source = data.get(
                "source"
            )

            if source is not None:
                source = str(
                    source
                )

            confidence = (
                self._extract_confidence(
                    data
                )
            )

            candidates.append(
                LexiconCandidate(
                    concept=concept,
                    gloss=gloss,
                    file_path=str(
                        json_path
                    ),
                    status=status,
                    confidence=confidence,
                    source=source,
                    data=data,
                )
            )

        self._lexicon_cache = (
            candidates
        )

        return candidates

    # ------------------------------------------------------------------
    # RESOLVE ELEMENT
    # ------------------------------------------------------------------

    def _resolve_element(
        self,
        unit: dict[str, Any],
        element: dict[str, Any],
        lexicon: list[LexiconCandidate],
    ) -> ResolvedSign:

        element_id = str(
            element.get(
                "element_id",
                "",
            )
        )

        source_unit = int(
            element.get(
                "source_unit",
                unit.get(
                    "unit_id",
                    -1,
                ),
            )
        )

        requested_concept = str(
            element.get(
                "source_concept",
                "",
            )
        )

        requested_gloss = (
            element.get(
                "gloss_candidate"
            )
        )

        if requested_gloss is not None:
            requested_gloss = str(
                requested_gloss
            )

        semantic_role = str(
            element.get(
                "semantic_role",
                "",
            )
        )

        candidate, method = (
            self._find_best_candidate(
                requested_concept,
                requested_gloss,
                semantic_role,
                lexicon,
            )
        )

        warnings: list[str] = []

        if candidate is None:

            warnings.append(
                "No matching local DGS "
                "lexicon entry was found."
            )

            return ResolvedSign(
                element_id=element_id,
                source_unit=source_unit,
                requested_concept=(
                    requested_concept
                ),
                requested_gloss=(
                    requested_gloss
                ),
                semantic_role=semantic_role,
                resolved_concept=None,
                resolved_gloss=None,
                status="unresolved",
                confidence=0.0,
                sign_data=None,
                resolution_method="none",
                usable_for_animation=False,
                warnings=warnings,
            )

        # --------------------------------------------------------------
        # PRESERVE PROTOTYPE STATUS
        # --------------------------------------------------------------

        status = candidate.status

        if (
            status.lower()
            in {
                "prototype",
                "experimental",
                "draft",
            }
        ):

            warnings.append(
                "Resolved sign is marked "
                f"'{status}' and is not "
                "being treated as an official "
                "DGS resource."
            )

        # --------------------------------------------------------------
        # CONFIDENCE COMBINATION
        # --------------------------------------------------------------

        requested_confidence = (
            self._safe_float(
                element.get(
                    "confidence",
                    0.0,
                )
            )
        )

        resolved_confidence = (
            self._combine_confidence(
                requested_confidence,
                candidate.confidence,
            )
        )

        # --------------------------------------------------------------
        # ANIMATION USABILITY
        # --------------------------------------------------------------

        usable = (
            self._is_animation_usable(
                candidate
            )
        )

        if not usable:

            warnings.append(
                "The resolved definition does "
                "not contain enough validated "
                "motion/hand information for "
                "automatic animation."
            )

        return ResolvedSign(
            element_id=element_id,
            source_unit=source_unit,
            requested_concept=(
                requested_concept
            ),
            requested_gloss=(
                requested_gloss
            ),
            semantic_role=semantic_role,
            resolved_concept=(
                candidate.concept
            ),
            resolved_gloss=(
                candidate.gloss
            ),
            status=status,
            confidence=resolved_confidence,
            sign_data=candidate.data,
            resolution_method=method,
            usable_for_animation=usable,
            warnings=warnings,
        )

    # ------------------------------------------------------------------
    # BEST MATCH
    # ------------------------------------------------------------------

        # ------------------------------------------------------------------
    # SEMANTIC ALIASES
    # ------------------------------------------------------------------

    @staticmethod
    def _semantic_aliases(
        concept: str,
    ) -> set[str]:

        aliases = {
            "first_person": {
                "me",
                "i",
            },
            "second_person": {
                "you",
            },
            "signer": {
                "me",
                "i",
            },
            "addressee": {
                "you",
            },
        }

        return {
            DGSLexiconResolver._normalize(
                value
            )
            for value in aliases.get(
                DGSLexiconResolver._normalize(
                    concept
                ),
                set(),
            )
        }

    def _find_best_candidate(
        self,
        requested_concept: str,
        requested_gloss: str | None,
        semantic_role: str,
        lexicon: list[LexiconCandidate],
    ) -> tuple[
        LexiconCandidate | None,
        str,
    ]:

        normalized_concept = (
            self._normalize(
                requested_concept
            )
        )

        normalized_gloss = (
            self._normalize(
                requested_gloss
            )
            if requested_gloss
            else ""
        )

        normalized_role = (
            self._normalize(
                semantic_role
            )
        )

                # --------------------------------------------------------------
        # 2. SEMANTIC ALIAS
        # --------------------------------------------------------------

        aliases = self._semantic_aliases(
            requested_concept
        )

        for candidate in lexicon:

            candidate_concept = (
                self._normalize(
                    candidate.concept
                )
            )

            if candidate_concept in aliases:

                return (
                    candidate,
                    "semantic_alias",
                )

        # --------------------------------------------------------------
        # 1. EXACT CONCEPT
        # --------------------------------------------------------------

        for candidate in lexicon:

            if self._normalize(
                candidate.concept
            ) == normalized_concept:

                return (
                    candidate,
                    "exact_concept",
                )

        # --------------------------------------------------------------
        # 2. EXACT GLOSS
        # --------------------------------------------------------------

        if normalized_gloss:

            for candidate in lexicon:

                if (
                    candidate.gloss
                    and
                    self._normalize(
                        candidate.gloss
                    )
                    == normalized_gloss
                ):

                    return (
                        candidate,
                        "exact_gloss",
                    )

                if (
                    self._normalize(
                        Path(
                            candidate.file_path
                        ).stem
                    )
                    == normalized_gloss
                ):

                    return (
                        candidate,
                        "filename_gloss",
                    )

        # --------------------------------------------------------------
        # 3. NORMALIZED CONCEPT
        # --------------------------------------------------------------

        for candidate in lexicon:

            candidate_concept = (
                self._normalize(
                    candidate.concept
                )
            )

            if (
                normalized_concept
                and
                (
                    normalized_concept
                    in candidate_concept
                    or
                    candidate_concept
                    in normalized_concept
                )
            ):

                return (
                    candidate,
                    "normalized_concept",
                )

        # --------------------------------------------------------------
        # 4. ROLE-BASED MATCH
        # --------------------------------------------------------------

        role_candidates = (
            self._role_compatible_concepts(
                normalized_role
            )
        )

        for candidate in lexicon:

            candidate_normalized = (
                self._normalize(
                    candidate.concept
                )
            )

            if candidate_normalized in (
                role_candidates
            ):

                return (
                    candidate,
                    "semantic_role",
                )

        return (
            None,
            "none",
        )

    # ------------------------------------------------------------------
    # ROLE COMPATIBILITY
    # ------------------------------------------------------------------

    @staticmethod
    def _role_compatible_concepts(
        role: str,
    ) -> set[str]:

        mapping = {
            "need_toward_person": {
                "need",
            },
            "predicate": {
                "need",
                "find",
                "live",
                "feel",
                "love",
            },
            "unsuccessful_search": {
                "find",
            },
            "positive_state": {
                "positive",
                "alive",
                "happy",
                "light",
            },
            "negative_state": {
                "negative",
                "sad",
                "alone",
                "broken",
            },
            "intense_affection": {
                "love",
                "affection",
            },
            "affection_toward_person": {
                "love",
                "affection",
            },
            "emotional_dependency": {
                "depend",
                "dependency",
                "need",
            },
            "positive_importance": {
                "important",
                "importance",
                "light",
            },
        }

        return {
            DGSLexiconResolver._normalize(
                concept
            )
            for concept
            in mapping.get(
                role,
                set(),
            )
        }

    # ------------------------------------------------------------------
    # CONFIDENCE
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_confidence(
        data: dict[str, Any],
    ) -> float:

        value = data.get(
            "confidence"
        )

        if value is None:

            metadata = data.get(
                "metadata"
            )

            if isinstance(
                metadata,
                dict,
            ):

                value = metadata.get(
                    "confidence"
                )

        return (
            DGSLexiconResolver._safe_float(
                value
            )
        )

    @staticmethod
    def _combine_confidence(
        source_confidence: float,
        lexicon_confidence: float,
    ) -> float:

        if (
            source_confidence <= 0
            and lexicon_confidence <= 0
        ):

            return 0.0

        if source_confidence <= 0:
            return round(
                lexicon_confidence,
                4,
            )

        if lexicon_confidence <= 0:
            return round(
                source_confidence,
                4,
            )

        # Geometric mean prevents a high confidence in one layer
        # from completely hiding very low confidence in the other.
        combined = (
            source_confidence
            * lexicon_confidence
        ) ** 0.5

        return round(
            min(
                combined,
                1.0,
            ),
            4,
        )

    # ------------------------------------------------------------------
    # ANIMATION VALIDATION
    # ------------------------------------------------------------------

    @staticmethod
    def _is_animation_usable(
        candidate: LexiconCandidate,
    ) -> bool:

        data = candidate.data

        status = candidate.status.lower()

        if status in {
            "unresolved",
            "invalid",
        }:
            return False

        # Prototype definitions may still be sent through the
        # animation pipeline, but only if they contain actual
        # motion/hand/location information.
        hand_shape = data.get(
            "hand_shape"
        )

        orientation = data.get(
            "orientation"
        )

        location = data.get(
            "location"
        )

        movement = data.get(
            "movement"
        )

        has_component = any(
            component
            for component
            in (
                hand_shape,
                orientation,
                location,
                movement,
            )
        )

        return bool(
            has_component
        )

    # ------------------------------------------------------------------
    # SONG PLAN
    # ------------------------------------------------------------------

    @staticmethod
    def _build_song_plan(
        mapping: dict[str, Any],
        resolved_signs: list[ResolvedSign],
    ) -> dict[str, Any]:

        return {
            "target_language": "DGS",
            "unit_order": [
                unit.get(
                    "unit_id"
                )
                for unit
                in mapping.get(
                    "units",
                    [],
                )
            ],
            "resolved_sequence": [
                {
                    "element_id": sign.element_id,
                    "unit": sign.source_unit,
                    "gloss": sign.resolved_gloss,
                    "concept": sign.resolved_concept,
                    "status": sign.status,
                    "confidence": sign.confidence,
                }
                for sign
                in resolved_signs
                if sign.resolved_concept
                is not None
            ],
            "unresolved_elements": [
                sign.element_id
                for sign in resolved_signs
                if sign.resolved_concept
                is None
            ],
            "prototype_elements": [
                sign.element_id
                for sign in resolved_signs
                if sign.status.lower()
                == "prototype"
            ],
            "animation_ready_elements": [
                sign.element_id
                for sign in resolved_signs
                if sign.usable_for_animation
            ],
        }

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_status(
        resolved_signs: list[ResolvedSign],
        mapping: dict[str, Any],
    ) -> str:

        if not mapping.get(
            "units"
        ):

            return "no_mapping"

        if not resolved_signs:

            return "no_signs"

        resolved_count = sum(
            1
            for sign
            in resolved_signs
            if sign.resolved_concept
            is not None
        )

        if resolved_count == len(
            resolved_signs
        ):

            return "resolved"

        if resolved_count > 0:

            return "partially_resolved"

        return "unresolved"

    # ------------------------------------------------------------------
    # NORMALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize(
        value: str | None,
    ) -> str:

        if value is None:
            return ""

        value = str(
            value
        ).lower().strip()

        value = re.sub(
            r"[^a-z0-9äöüßà-ÿ]+",
            "_",
            value,
        )

        value = re.sub(
            r"_+",
            "_",
            value,
        )

        return value.strip(
            "_"
        )

    # ------------------------------------------------------------------
    # SAFE FLOAT
    # ------------------------------------------------------------------

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float:

        try:

            result = float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

        return max(
            0.0,
            min(
                result,
                1.0,
            ),
        )


# ============================================================================
# DEBUG OUTPUT
# ============================================================================


def _print_result(
    result: dict[str, Any],
) -> None:

    print("\n" + "=" * 72)
    print(
        "SIGNMUSIC DGS LEXICON RESOLVER"
    )
    print("=" * 72)

    print(
        f"Status: "
        f"{result['status']}"
    )

    print(
        f"Source language: "
        f"{result['source_language']}"
    )

    print(
        f"Target language: "
        f"{result['target_language']}"
    )

    print(
        f"Lexicon files: "
        f"{result['lexicon']['file_count']}"
    )

    print(
        "\nResolved signs:"
    )

    for sign in result[
        "resolved_signs"
    ]:

        print(
            f"\n  Element: "
            f"{sign['element_id']}"
        )

        print(
            f"    Source unit: "
            f"{sign['source_unit']}"
        )

        print(
            f"    Requested concept: "
            f"{sign['requested_concept']}"
        )

        print(
            f"    Requested gloss: "
            f"{sign['requested_gloss']}"
        )

        print(
            f"    Semantic role: "
            f"{sign['semantic_role']}"
        )

        print(
            f"    Resolved concept: "
            f"{sign['resolved_concept']}"
        )

        print(
            f"    Resolved gloss: "
            f"{sign['resolved_gloss']}"
        )

        print(
            f"    Status: "
            f"{sign['status']}"
        )

        print(
            f"    Confidence: "
            f"{sign['confidence']}"
        )

        print(
            f"    Method: "
            f"{sign['resolution_method']}"
        )

        print(
            f"    Animation usable: "
            f"{sign['usable_for_animation']}"
        )

        for warning in sign[
            "warnings"
        ]:

            print(
                f"    WARNING: "
                f"{warning}"
            )

    print(
        "\nSong plan:"
    )

    song_plan = result[
        "song_plan"
    ]

    print(
        f"  Resolved sequence: "
        f"{len(song_plan['resolved_sequence'])}"
    )

    print(
        f"  Unresolved: "
        f"{song_plan['unresolved_elements']}"
    )

    print(
        f"  Prototype: "
        f"{song_plan['prototype_elements']}"
    )

    print(
        f"  Animation ready: "
        f"{song_plan['animation_ready_elements']}"
    )

    print(
        "\nMetadata:"
    )

    for key, value in result[
        "metadata"
    ].items():

        print(
            f"  {key}: {value}"
        )


# ============================================================================
# TEST
# ============================================================================


def main() -> None:

    resolver = (
        DGSLexiconResolver()
    )

    lyrics = """I need you
I cannot find you
I still need you"""

    result = resolver.resolve(
        lyrics
    )

    _print_result(
        result
    )


if __name__ == "__main__":
    main()