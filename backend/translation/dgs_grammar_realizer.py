from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from .dgs_semantic_mapper import DGSSemanticMapper
from .dgs_lexicon_resolver import DGSLexiconResolver


@dataclass
class GrammarElement:
    element_id: str
    unit_id: int
    order: int

    role: str

    requested_concept: str
    requested_gloss: str | None

    resolved_concept: str | None
    resolved_gloss: str | None

    status: str
    confidence: float

    negated: bool = False
    modality: str | None = None

    discourse: list[str] = field(default_factory=list)
    non_manual: list[str] = field(default_factory=list)

    animation_ready: bool = False

    warnings: list[str] = field(default_factory=list)


class DGSGrammarRealizer:
    """
    Construye una secuencia DGS intermedia y ordenada.

    IMPORTANTE:
    Esto NO pretende ser una traducción gramatical DGS validada.

    Es una capa intermedia entre:

        DGS Semantic Mapper
                ↓
        DGS Lexicon Resolver
                ↓
        DGS Grammar Realizer
                ↓
        Motion / Avatar

    Los elementos sin entrada léxica permanecen visibles.
    Nunca se inventa una seña para rellenar un hueco.

    Esta capa también conserva información gramatical importante
    aunque el mapper la entregue a nivel de unidad o aunque haya
    que recuperarla del texto fuente.
    """

    ROLE_PRIORITY = {
        "time": 10,
        "temporal": 10,

        "agent": 20,
        "first_person": 20,
        "subject": 20,

        "target": 30,
        "second_person": 30,
        "object": 30,

        "predicate": 40,
        "event": 40,
        "need_toward_person": 40,
        "unsuccessful_search": 40,

        "state": 50,
        "result": 50,

        "negation": 90,
        "modality": 91,
        "persistence": 92,
    }

    def __init__(
        self,
        semantic_mapper: DGSSemanticMapper | None = None,
        lexicon_resolver: DGSLexiconResolver | None = None,
    ) -> None:

        self.semantic_mapper = (
            semantic_mapper or DGSSemanticMapper()
        )

        self.lexicon_resolver = (
            lexicon_resolver
            or DGSLexiconResolver(
                semantic_mapper=self.semantic_mapper
            )
        )

    # ==================================================================
    # PUBLIC API
    # ==================================================================

    def realize_from_lyrics(
        self,
        lyrics: str,
    ) -> dict[str, Any]:

        mapping = self.semantic_mapper.analyze(
            lyrics
        )

        resolution = self.lexicon_resolver.resolve(
            mapping
        )

        return self.realize(
            mapping,
            resolution,
        )

    def realize(
        self,
        mapping: dict[str, Any],
        resolution: dict[str, Any],
    ) -> dict[str, Any]:

        resolved_by_id = {
            str(item["element_id"]): item
            for item in resolution.get(
                "resolved_signs",
                [],
            )
        }

        units: list[dict[str, Any]] = []

        for unit_index, unit in enumerate(
            mapping.get(
                "units",
                [],
            )
        ):

            unit_id = int(
                unit.get(
                    "unit_id",
                    unit_index,
                )
            )

            planned = self._build_elements(
                unit=unit,
                unit_id=unit_id,
                resolved_by_id=resolved_by_id,
                mapping=mapping,
            )

            planned = self._deduplicate_lexical_signs(
                planned
            )

            planned.sort(
                key=lambda item: (
                    self.ROLE_PRIORITY.get(
                        self._normalize(
                            item.role
                        ),
                        70,
                    ),
                    item.element_id,
                )
            )

            for order, item in enumerate(
                planned
            ):
                item.order = order

            sequence = [
                asdict(item)
                for item in planned
            ]

            unit_non_manual = sorted(
                {
                    marker
                    for item in planned
                    for marker in item.non_manual
                }
            )

            units.append(
                {
                    "unit_id": unit_id,

                    "source_text": self._get_source_text(
                        unit
                    ),

                    "sequence": sequence,

                    "gloss_sequence": [
                        self._display_gloss(item)
                        for item in planned
                    ],

                    "resolved_gloss_sequence": [
                        self._display_gloss(item)
                        for item in planned
                        if (
                            item.resolved_concept
                            is not None
                        )
                    ],

                    "non_manual": unit_non_manual,

                    "fully_resolved": (
                        bool(planned)
                        and all(
                            item.resolved_concept
                            is not None
                            for item in planned
                            if (
                                item.status
                                != "grammatical_marker"
                            )
                        )
                    ),

                    "animation_ready": (
                        bool(planned)
                        and all(
                            item.animation_ready
                            for item in planned
                        )
                    ),

                    "grammar": self._build_unit_grammar_summary(
                        planned
                    ),
                }
            )

        result = {
            "status": self._determine_status(
                units
            ),

            "source_language": mapping.get(
                "source_language"
            ),

            "target_language": mapping.get(
                "target_language",
                "DGS",
            ),

            "units": units,

            "sequence": [
                element
                for unit in units
                for element in unit["sequence"]
            ],

            "gloss_sequence": [
                gloss
                for unit in units
                for gloss in unit["gloss_sequence"]
            ],

            "resolved_gloss_sequence": [
                gloss
                for unit in units
                for gloss in unit[
                    "resolved_gloss_sequence"
                ]
            ],

            "animation_ready_sequence": [
                element
                for unit in units
                for element in unit["sequence"]
                if (
                    element["animation_ready"]
                )
            ],

            "non_manual_sequence": [
                {
                    "unit_id": unit["unit_id"],
                    "markers": unit["non_manual"],
                }
                for unit in units
                if unit["non_manual"]
            ],

            "metadata": {
                "unit_count": len(units),

                "element_count": sum(
                    len(unit["sequence"])
                    for unit in units
                ),

                "resolved_count": sum(
                    1
                    for unit in units
                    for element in unit["sequence"]
                    if (
                        element["resolved_concept"]
                        is not None
                    )
                ),

                "unresolved_count": sum(
                    1
                    for unit in units
                    for element in unit["sequence"]
                    if (
                        element["resolved_concept"]
                        is None
                        and element["status"]
                        != "grammatical_marker"
                    )
                ),

                "units_with_negation": sum(
                    1
                    for unit in units
                    if "negative_polarity"
                    in unit["non_manual"]
                ),

                "units_with_inability": sum(
                    1
                    for unit in units
                    if "inability"
                    in unit["non_manual"]
                ),

                "units_with_continuative": sum(
                    1
                    for unit in units
                    if "continuative"
                    in unit["non_manual"]
                ),

                "grammar_validation_complete": False,

                "official_dgs_claimed": False,

                "motion_generation_complete": False,
            },

            "notes": [
                "Intermediate DGS-oriented grammar plan.",
                "Not a validated DGS translation.",
                "Unresolved lexical concepts are preserved.",
                "No missing sign is silently invented.",
                "Unit-level grammatical information is preserved.",
                "Source-text fallback is used when explicit metadata "
                "is unavailable.",
            ],
        }

        return result

    # ==================================================================
    # BUILD ELEMENTS
    # ==================================================================

    def _build_elements(
        self,
        unit: dict[str, Any],
        unit_id: int,
        resolved_by_id: dict[str, dict[str, Any]],
        mapping: dict[str, Any],
    ) -> list[GrammarElement]:

        result: list[GrammarElement] = []

        grammar_info = self._extract_unit_grammar(
            unit=unit,
            mapping=mapping,
        )

        unit_negated = grammar_info["negated"]
        unit_modality = grammar_info["modality"]
        unit_non_manual = set(
            grammar_info["non_manual"]
        )

        # --------------------------------------------------------------
        # Build semantic / lexical elements
        # --------------------------------------------------------------

        for element in unit.get(
            "elements",
            [],
        ):

            if not isinstance(
                element,
                dict,
            ):
                continue

            element_id = str(
                element.get(
                    "element_id",
                    "",
                )
            )

            resolved = resolved_by_id.get(
                element_id,
                {},
            )

            requested_concept = str(
                element.get(
                    "source_concept",
                    "",
                )
            )

            requested_gloss = element.get(
                "gloss_candidate"
            )

            if requested_gloss is not None:
                requested_gloss = str(
                    requested_gloss
                )

            role = str(
                element.get(
                    "semantic_role",
                    element.get(
                        "role",
                        "",
                    ),
                )
            )

            resolved_concept = resolved.get(
                "resolved_concept"
            )

            resolved_gloss = resolved.get(
                "resolved_gloss"
            )

            status = str(
                resolved.get(
                    "status",
                    "unresolved",
                )
            )

            confidence = self._safe_float(
                resolved.get(
                    "confidence",
                    element.get(
                        "confidence",
                        0.0,
                    ),
                )
            )

            warnings = list(
                resolved.get(
                    "warnings",
                    [],
                )
            )

            if (
                resolved_concept is None
            ):

                warnings.append(
                    "Concept remains unresolved "
                    "because no local DGS lexicon "
                    "entry exists."
                )

            element_negated = bool(
                element.get(
                    "negated",
                    False,
                )
            )

            negated = (
                element_negated
                or unit_negated
            )

            element_modality = element.get(
                "modality"
            )

            modality = (
                str(element_modality)
                if element_modality is not None
                else unit_modality
            )

            non_manual = set(
                self._build_non_manual(
                    element
                )
            )

            non_manual.update(
                unit_non_manual
            )

            # ----------------------------------------------------------
            # Role-specific grammatical markers
            # ----------------------------------------------------------

            normalized_role = self._normalize(
                role
            )

            normalized_concept = self._normalize(
                requested_concept
            )

            if normalized_role in {
                "negation",
                "negative",
            }:

                negated = True

                non_manual.add(
                    "negative_polarity"
                )

            if (
                normalized_role
                in {
                    "persistence",
                    "continuative",
                }
                or normalized_concept
                in {
                    "still",
                    "continuative",
                }
            ):

                non_manual.add(
                    "continuative"
                )

            if (
                normalized_role
                in {
                    "inability",
                    "modal_inability",
                }
                or (
                    modality
                    and
                    "inabil"
                    in modality.lower()
                )
            ):

                non_manual.add(
                    "inability"
                )

            result.append(
                GrammarElement(
                    element_id=element_id,

                    unit_id=unit_id,

                    order=0,

                    role=role,

                    requested_concept=(
                        requested_concept
                    ),

                    requested_gloss=(
                        requested_gloss
                    ),

                    resolved_concept=(
                        resolved_concept
                    ),

                    resolved_gloss=(
                        resolved_gloss
                    ),

                    status=status,

                    confidence=confidence,

                    negated=negated,

                    modality=modality,

                    discourse=self._build_discourse(
                        element
                    ),

                    non_manual=sorted(
                        non_manual
                    ),

                    animation_ready=bool(
                        resolved.get(
                            "usable_for_animation",
                            False,
                        )
                    ),

                    warnings=warnings,
                )
            )

        # --------------------------------------------------------------
        # Add SIGNER grammatical marker.
        #
        # This is NOT a lexical ME sign.
        # It represents the semantic agent in the motion layer.
        # --------------------------------------------------------------

        if grammar_info["subject"] == "first_person":

            already_has_agent = any(
                (
                    self._normalize(
                        element.requested_concept
                    )
                    in {
                        "first_person",
                        "signer",
                        "me",
                    }
                )
                or
                (
                    self._normalize(
                        element.role
                    )
                    in {
                        "agent",
                        "subject",
                    }
                )
                for element in result
            )

            if not already_has_agent:

                result.insert(
                    0,
                    GrammarElement(
                        element_id=(
                            f"U{unit_id}_SIGNER"
                        ),

                        unit_id=unit_id,

                        order=0,

                        role="agent",

                        requested_concept=(
                            "first_person"
                        ),

                        requested_gloss="SIGNER",

                        resolved_concept=None,

                        resolved_gloss="SIGNER",

                        status="grammatical_marker",

                        confidence=1.0,

                        negated=False,

                        modality=None,

                        discourse=[],

                        non_manual=[],

                        animation_ready=True,

                        warnings=[
                            "SIGNER is a grammatical "
                            "participant marker, not "
                            "a lexical DGS sign."
                        ],
                    )
                )

        return result

    # ==================================================================
    # EXTRACT UNIT GRAMMAR
    # ==================================================================

    def _extract_unit_grammar(
        self,
        unit: dict[str, Any],
        mapping: dict[str, Any],
    ) -> dict[str, Any]:

        sources: list[dict[str, Any]] = []

        # --------------------------------------------------------------
        # Unit itself
        # --------------------------------------------------------------

        sources.append(
            unit
        )

        # --------------------------------------------------------------
        # Nested grammar structures
        # --------------------------------------------------------------

        for key in (
            "grammar_plan",
            "grammar",
            "linguistic_plan",
            "dgs_grammar",
            "grammar_structure",
            "grammar_metadata",
        ):

            value = unit.get(
                key
            )

            if isinstance(
                value,
                dict,
            ):

                sources.append(
                    value
                )

        # --------------------------------------------------------------
        # Mapper-level structures
        # --------------------------------------------------------------

        if isinstance(
            mapping,
            dict,
        ):

            for key in (
                "grammar_plan",
                "grammar",
                "linguistic_plan",
                "dgs_grammar",
            ):

                value = mapping.get(
                    key
                )

                if not isinstance(
                    value,
                    dict,
                ):
                    continue

                unit_id_string = str(
                    unit.get(
                        "unit_id",
                        "",
                    )
                )

                # Some structures are:
                #
                # grammar_plan = {
                #     "0": {...},
                #     "1": {...}
                # }

                nested_unit = value.get(
                    unit_id_string
                )

                if isinstance(
                    nested_unit,
                    dict,
                ):

                    sources.append(
                        nested_unit
                    )

                else:

                    sources.append(
                        value
                    )

        negated = False
        modality: str | None = None
        subject: str | None = None

        # --------------------------------------------------------------
        # Explicit metadata
        # --------------------------------------------------------------

        for source in sources:

            if not isinstance(
                source,
                dict,
            ):
                continue

            for key in (
                "negated",
                "negation",
                "negative",
                "is_negated",
            ):

                value = source.get(
                    key
                )

                if value is True:

                    negated = True

            for key in (
                "subject",
                "grammar_subject",
                "grammatical_subject",
                "agent",
            ):

                value = source.get(
                    key
                )

                if value is None:
                    continue

                normalized = self._normalize(
                    str(value)
                )

                if normalized in {
                    "first_person",
                    "signer",
                    "i",
                    "me",
                }:

                    subject = (
                        "first_person"
                    )

                elif normalized in {
                    "second_person",
                    "addressee",
                    "you",
                }:

                    subject = (
                        "second_person"
                    )

            for key in (
                "modality",
                "modal",
                "modal_value",
                "modality_type",
            ):

                value = source.get(
                    key
                )

                if value is None:
                    continue

                if str(value).lower() in {
                    "",
                    "none",
                    "null",
                }:
                    continue

                modality = str(
                    value
                )

        # --------------------------------------------------------------
        # Individual elements
        # --------------------------------------------------------------

        for element in unit.get(
            "elements",
            [],
        ):

            if not isinstance(
                element,
                dict,
            ):
                continue

            if element.get(
                "negated"
            ) is True:

                negated = True

            for key in (
                "modality",
                "modal",
            ):

                value = element.get(
                    key
                )

                if value:
                    modality = str(
                        value
                    )

            concept = self._normalize(
                str(
                    element.get(
                        "source_concept",
                        "",
                    )
                )
            )

            role = self._normalize(
                str(
                    element.get(
                        "semantic_role",
                        element.get(
                            "role",
                            "",
                        ),
                    )
                )
            )

            if concept in {
                "first_person",
                "signer",
            }:

                subject = (
                    "first_person"
                )

            if (
                role in {
                    "agent",
                    "subject",
                }
                and concept in {
                    "first_person",
                    "signer",
                    "me",
                }
            ):

                subject = (
                    "first_person"
                )

        # --------------------------------------------------------------
        # Source-text fallback
        # --------------------------------------------------------------

        source_text = self._get_source_text(
            unit
        )

        normalized_text = (
            source_text
            .lower()
            .replace(
                "’",
                "'",
            )
            .strip()
        )

        cleaned_text = (
            normalized_text
            .replace(
                ",",
                " ",
            )
            .replace(
                ".",
                " ",
            )
            .replace(
                "?",
                " ",
            )
            .replace(
                "!",
                " ",
            )
            .replace(
                ";",
                " ",
            )
            .replace(
                ":",
                " ",
            )
        )

        words = set(
            cleaned_text.split()
        )

        # --------------------------------------------------------------
        # FIRST PERSON
        # --------------------------------------------------------------

        if (
            "i" in words
            or "i'm" in words
            or "ive" in words
            or "i've" in words
            or "ill" in words
            or "i'll" in words
            or "id" in words
            or "i'd" in words
        ):

            subject = (
                subject
                or "first_person"
            )

        # --------------------------------------------------------------
        # INABILITY
        # --------------------------------------------------------------

        inability_markers = (
            "cannot",
            "can't",
            "cant",
            "unable",
            "couldn't",
            "couldnt",
        )

        has_inability = any(
            marker in normalized_text
            for marker
            in inability_markers
        )

        if has_inability:

            negated = True

            if modality is None:

                modality = "inability"

        # --------------------------------------------------------------
        # NEGATION
        # --------------------------------------------------------------

        padded_text = (
            f" {cleaned_text} "
        )

        for marker in (
            "not",
            "never",
            "no",
        ):

            if (
                f" {marker} "
                in padded_text
            ):

                negated = True

        # --------------------------------------------------------------
        # NON-MANUAL
        # --------------------------------------------------------------

        non_manual: set[str] = set()

        if negated:

            non_manual.add(
                "negative_polarity"
            )

        if (
            has_inability
            or (
                modality
                and
                "inabil"
                in modality.lower()
            )
        ):

            non_manual.add(
                "inability"
            )

        if "still" in words:

            non_manual.add(
                "continuative"
            )

        if "again" in words:

            non_manual.add(
                "repetition"
            )

        if modality:

            modality_normalized = (
                modality.lower()
            )

            if (
                "inabil"
                in modality_normalized
            ):

                non_manual.add(
                    "inability"
                )

            elif modality_normalized not in {
                "",
                "none",
                "null",
            }:

                non_manual.add(
                    "modality"
                )

        return {
            "subject": subject,
            "negated": negated,
            "modality": modality,
            "non_manual": sorted(
                non_manual
            ),
        }

    # ==================================================================
    # DEDUPLICATION
    # ==================================================================

    def _deduplicate_lexical_signs(
        self,
        elements: list[GrammarElement],
    ) -> list[GrammarElement]:

        result: list[GrammarElement] = []

        seen: dict[
            tuple[str, str],
            GrammarElement,
        ] = {}

        for element in elements:

            # Never deduplicate SIGNER.
            if (
                element.status
                == "grammatical_marker"
            ):

                result.append(
                    element
                )

                continue

            lexical_value = (
                element.resolved_concept
                or element.requested_gloss
                or element.requested_concept
            )

            lexical_key = (
                self._normalize(
                    lexical_value
                ),
                self._normalize(
                    self._lexical_role(
                        element.role
                    )
                ),
            )

            if not lexical_key[0]:

                result.append(
                    element
                )

                continue

            existing = seen.get(
                lexical_key
            )

            if existing is None:

                seen[lexical_key] = (
                    element
                )

                result.append(
                    element
                )

                continue

            # Merge richer semantic data.
            existing.warnings.extend(
                warning
                for warning in element.warnings
                if (
                    warning
                    not in existing.warnings
                )
            )

            existing.non_manual = sorted(
                set(
                    existing.non_manual
                    + element.non_manual
                )
            )

            existing.discourse = sorted(
                set(
                    existing.discourse
                    + element.discourse
                )
            )

            existing.confidence = max(
                existing.confidence,
                element.confidence,
            )

            existing.animation_ready = (
                existing.animation_ready
                or element.animation_ready
            )

            existing.negated = (
                existing.negated
                or element.negated
            )

            if (
                existing.modality
                is None
                and element.modality
                is not None
            ):

                existing.modality = (
                    element.modality
                )

        return result

    @staticmethod
    def _lexical_role(
        role: str,
    ) -> str:

        aliases = {
            "need_toward_person": "predicate",
            "unsuccessful_search": "predicate",
            "event": "predicate",
        }

        return aliases.get(
            role,
            role,
        )

    # ==================================================================
    # NON-MANUAL
    # ==================================================================

    @staticmethod
    def _build_non_manual(
        element: dict[str, Any],
    ) -> list[str]:

        result: set[str] = set()

        if bool(
            element.get(
                "negated",
                False,
            )
        ):

            result.add(
                "negative_polarity"
            )

        modality = element.get(
            "modality"
        )

        if modality:

            value = str(
                modality
            ).lower()

            if (
                "inabil"
                in value
            ):

                result.add(
                    "inability"
                )

            elif value not in {
                "",
                "none",
                "null",
            }:

                result.add(
                    "modality"
                )

        discourse = element.get(
            "discourse",
            [],
        )

        if isinstance(
            discourse,
            list,
        ):

            for marker in discourse:

                value = str(
                    marker
                ).lower()

                if (
                    "still"
                    in value
                    or "continu"
                    in value
                ):

                    result.add(
                        "continuative"
                    )

                if "again" in value:

                    result.add(
                        "repetition"
                    )

        return sorted(
            result
        )

    @staticmethod
    def _build_discourse(
        element: dict[str, Any],
    ) -> list[str]:

        value = element.get(
            "discourse",
            [],
        )

        if isinstance(
            value,
            list,
        ):

            return [
                str(item)
                for item in value
            ]

        if value:

            return [
                str(value)
            ]

        return []

    # ==================================================================
    # UNIT SUMMARY
    # ==================================================================

    @staticmethod
    def _build_unit_grammar_summary(
        elements: list[GrammarElement],
    ) -> dict[str, Any]:

        subjects = [
            element
            for element in elements
            if (
                element.role
                in {
                    "agent",
                    "subject",
                    "first_person",
                }
            )
        ]

        predicates = [
            element
            for element in elements
            if (
                element.role
                in {
                    "predicate",
                    "event",
                    "need_toward_person",
                    "unsuccessful_search",
                }
            )
        ]

        return {
            "subject": (
                subjects[0].requested_concept
                if subjects
                else None
            ),

            "predicates": [
                (
                    element.resolved_gloss
                    or element.requested_gloss
                    or element.requested_concept
                )
                for element in predicates
            ],

            "negated": any(
                element.negated
                for element in elements
            ),

            "modalities": sorted(
                {
                    element.modality
                    for element in elements
                    if element.modality
                }
            ),

            "non_manual": sorted(
                {
                    marker
                    for element in elements
                    for marker in element.non_manual
                }
            ),
        }

    # ==================================================================
    # HELPERS
    # ==================================================================

    @staticmethod
    def _get_source_text(
        unit: dict[str, Any],
    ) -> str:

        for key in (
            "text",
            "source_text",
            "raw_text",
            "lyrics",
        ):

            value = unit.get(
                key
            )

            if value is not None:

                return str(
                    value
                )

        return ""

    @staticmethod
    def _display_gloss(
        element: GrammarElement,
    ) -> str:

        return (
            element.resolved_gloss
            or element.resolved_concept
            or element.requested_gloss
            or element.requested_concept
        )

    @staticmethod
    def _normalize(
        value: str | None,
    ) -> str:

        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .lower()
            .replace(
                "-",
                "_",
            )
            .replace(
                " ",
                "_",
            )
        )

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
            )
        )

    @staticmethod
    def _determine_status(
        units: list[dict[str, Any]],
    ) -> str:

        lexical_elements = [
            element
            for unit in units
            for element in unit["sequence"]
            if (
                element["status"]
                != "grammatical_marker"
            )
        ]

        if not lexical_elements:

            return "no_elements"

        resolved = sum(
            1
            for element in lexical_elements
            if (
                element["resolved_concept"]
                is not None
            )
        )

        if resolved == len(
            lexical_elements
        ):

            return "ready"

        if resolved > 0:

            return "partially_ready"

        return "planning_only"


# ======================================================================
# TEST
# ======================================================================

def main() -> None:

    lyrics = """I need you
I cannot find you
I still need you"""

    realizer = (
        DGSGrammarRealizer()
    )

    result = (
        realizer.realize_from_lyrics(
            lyrics
        )
    )

    print()
    print("=" * 72)
    print(
        "SIGNMUSIC DGS GRAMMAR REALIZER"
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

    for unit in result[
        "units"
    ]:

        print()
        print(
            f"UNIT {unit['unit_id']}: "
            f"{unit['source_text']}"
        )

        print(
            "  Sequence: "
            + " ".join(
                unit[
                    "gloss_sequence"
                ]
            )
        )

        print(
            f"  Non-manual: "
            f"{unit['non_manual']}"
        )

        print(
            f"  Grammar: "
            f"{unit['grammar']}"
        )

        for element in unit[
            "sequence"
        ]:

            print(
                f"    {element['order']:02d} | "
                f"{element['role']:<24} | "
                f"{element['resolved_gloss'] or element['requested_gloss'] or element['requested_concept']} | "
                f"{element['status']} | "
                f"negated={element['negated']} | "
                f"modality={element['modality']} | "
                f"non_manual={element['non_manual']} | "
                f"animation={element['animation_ready']}"
            )

    print()
    print("Global metadata:")

    for key, value in result[
        "metadata"
    ].items():

        print(
            f"  {key}: {value}"
        )


if __name__ == "__main__":
    main()