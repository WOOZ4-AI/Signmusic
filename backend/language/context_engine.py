from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from typing import Any

from .linguistic_analyzer import LinguisticAnalyzer


# ---------------------------------------------------------------------------
# CONTEXT / DISCOURSE MARKERS
# ---------------------------------------------------------------------------

CAUSAL_MARKERS = {
    "because",
    "since",
    "therefore",
    "so",
    "why",
    "porque",
    "pues",
    "porqué",
    "por que",
    "donc",
    "parce",
}

CONTRAST_MARKERS = {
    "but",
    "however",
    "yet",
    "although",
    "though",
    "pero",
    "sin embargo",
    "aunque",
    "mais",
    "pourtant",
}

TEMPORAL_MARKERS = {
    "now",
    "today",
    "tonight",
    "tomorrow",
    "yesterday",
    "before",
    "after",
    "ahora",
    "hoy",
    "esta noche",
    "mañana",
    "ayer",
    "antes",
    "después",
    "encore",
    "maintenant",
    "avant",
    "après",
}

PERSISTENCE_MARKERS = {
    "still",
    "aún",
    "aun",
    "todavía",
    "toujours",
}

REPETITION_TEMPORAL_MARKERS = {
    "again",
    "otra vez",
    "de nuevo",
    "encore",
}

DURATION_MARKERS = {
    "forever",
    "always",
    "ever",
    "para siempre",
    "siempre",
    "pour toujours",
    "toujours",
}

CONDITION_MARKERS = {
    "if",
    "unless",
    "when",
    "whenever",
    "si",
    "cuando",
    "siempre que",
    "lorsque",
}

ADDRESS_MARKERS = {
    "you",
    "your",
    "yours",
    "tu",
    "tú",
    "te",
    "ti",
    "usted",
    "ustedes",
    "vous",
    "toi",
}

FIRST_PERSON_MARKERS = {
    "i",
    "me",
    "my",
    "mine",
    "we",
    "us",
    "our",
    "ours",
    "yo",
    "mi",
    "mis",
    "nos",
    "nosotros",
    "nuestra",
    "nuestro",
    "je",
    "moi",
    "nous",
    "notre",
}

NEGATION_MARKERS = {
    "not",
    "never",
    "no",
    "nothing",
    "nobody",
    "don't",
    "doesn't",
    "didn't",
    "can't",
    "cannot",
    "won't",
    "isn't",
    "aren't",
    "wasn't",
    "weren't",
    "ni",
    "nunca",
    "jamás",
    "nada",
    "nadie",
    "ne",
    "pas",
    "jamais",
    "rien",
}

INTENSIFIER_MARKERS = {
    "very",
    "really",
    "so",
    "too",
    "deeply",
    "much",
    "muy",
    "realmente",
    "tan",
    "demasiado",
    "très",
    "vraiment",
}


# ---------------------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------------------

@dataclass
class ContextClue:
    type: str
    evidence: list[str]
    strength: float
    evidence_scope: str


@dataclass
class ContextUnit:
    index: int
    segment_index: int
    text: str
    normalized_text: str
    segment_type: str
    tokens: list[dict[str, Any]]
    previous_segment_index: int | None
    next_segment_index: int | None
    repeated_terms: list[str]
    surrounding_terms: list[str]
    clues: list[ContextClue]
    confidence: float


@dataclass
class RepetitionGroup:
    term: str
    occurrences: int
    segment_indices: list[int]
    token_indices: list[int]
    spread: int


# ---------------------------------------------------------------------------
# CONTEXT ENGINE
# ---------------------------------------------------------------------------

class ContextEngine:
    """
    Structural context layer of Signmusic.

    The ContextEngine receives linguistic analysis and adds contextual
    evidence without pretending to know the final meaning.

    Important:

        local evidence
            Current segment.

        immediate_context
            Directly adjacent segment.

        surrounding_terms
            Nearby lexical material used as context only.

    ContextUnit intentionally contains the original token information so
    that downstream semantic layers do not lose linguistic evidence.
    """

    def __init__(
        self,
        linguistic_analyzer: LinguisticAnalyzer | None = None,
        context_window: int = 3,
    ) -> None:

        if context_window < 1:
            raise ValueError(
                "context_window must be >= 1"
            )

        self.linguistic_analyzer = (
            linguistic_analyzer
            or LinguisticAnalyzer()
        )

        self.context_window = context_window

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze(
        self,
        lyrics_or_analysis: str | dict[str, Any],
    ) -> dict[str, Any]:

        if isinstance(
            lyrics_or_analysis,
            str,
        ):

            linguistic_analysis = (
                self.linguistic_analyzer.analyze(
                    lyrics_or_analysis
                )
            )

        elif isinstance(
            lyrics_or_analysis,
            dict,
        ):

            linguistic_analysis = (
                lyrics_or_analysis
            )

        else:

            raise TypeError(
                "lyrics_or_analysis must be "
                "a string or dictionary"
            )

        segments = linguistic_analysis.get(
            "segments",
            [],
        )

        global_tokens = linguistic_analysis.get(
            "global_tokens",
            [],
        )

        repetition_groups = (
            self._build_repetition_groups(
                global_tokens,
                segments,
            )
        )

        context_units = (
            self._build_context_units(
                segments,
                repetition_groups,
            )
        )

        global_context = (
            self._build_global_context(
                linguistic_analysis,
                segments,
                repetition_groups,
            )
        )

        return {
            "status": self._determine_status(
                linguistic_analysis
            ),
            "language": linguistic_analysis.get(
                "language"
            ),
            "language_name": linguistic_analysis.get(
                "language_name"
            ),
            "language_confidence": linguistic_analysis.get(
                "language_confidence",
                0.0,
            ),
            "source_status": linguistic_analysis.get(
                "status"
            ),
            "original_text": linguistic_analysis.get(
                "original_text",
                "",
            ),
            "normalized_text": linguistic_analysis.get(
                "normalized_text",
                "",
            ),
            "context_units": [
                self._context_unit_to_dict(
                    unit
                )
                for unit in context_units
            ],
            "repetition_groups": [
                asdict(group)
                for group in repetition_groups
            ],
            "global_context": global_context,
            "metadata": {
                "segment_count": len(
                    segments
                ),
                "token_count": len(
                    global_tokens
                ),
                "repetition_group_count": len(
                    repetition_groups
                ),
                "context_unit_count": len(
                    context_units
                ),
                "context_window": (
                    self.context_window
                ),
            },
        }

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_status(
        analysis: dict[str, Any],
    ) -> str:

        if analysis.get("status") == "empty":
            return "empty"

        if not analysis.get("segments"):
            return "no_context"

        return "ok"

    # ------------------------------------------------------------------
    # REPETITIONS
    # ------------------------------------------------------------------

    def _build_repetition_groups(
        self,
        global_tokens: list[dict[str, Any]],
        segments: list[dict[str, Any]],
    ) -> list[RepetitionGroup]:

        positions: dict[
            str,
            list[tuple[int, int]],
        ] = defaultdict(list)

        for global_index, token in enumerate(
            global_tokens
        ):

            normalized = str(
                token.get(
                    "normalized",
                    "",
                )
            ).strip().lower()

            if not normalized:
                continue

            if token.get(
                "is_non_lexical",
                False,
            ):
                continue

            segment_index = (
                self._find_segment_for_token(
                    global_index,
                    segments,
                )
            )

            positions[normalized].append(
                (
                    global_index,
                    segment_index,
                )
            )

        groups: list[
            RepetitionGroup
        ] = []

        for term, occurrences in positions.items():

            if len(occurrences) < 2:
                continue

            token_indices = [
                occurrence[0]
                for occurrence in occurrences
            ]

            segment_indices = sorted(
                {
                    occurrence[1]
                    for occurrence in occurrences
                    if occurrence[1] >= 0
                }
            )

            spread = (
                max(token_indices)
                - min(token_indices)
            )

            groups.append(
                RepetitionGroup(
                    term=term,
                    occurrences=len(
                        occurrences
                    ),
                    segment_indices=segment_indices,
                    token_indices=token_indices,
                    spread=spread,
                )
            )

        groups.sort(
            key=lambda group: (
                -group.occurrences,
                group.term,
            )
        )

        return groups

    @staticmethod
    def _find_segment_for_token(
        global_token_index: int,
        segments: list[dict[str, Any]],
    ) -> int:

        count = 0

        for segment in segments:

            token_count = len(
                segment.get(
                    "tokens",
                    [],
                )
            )

            if (
                global_token_index
                < count + token_count
            ):

                return int(
                    segment.get(
                        "index",
                        -1,
                    )
                )

            count += token_count

        return -1

    # ------------------------------------------------------------------
    # CONTEXT UNITS
    # ------------------------------------------------------------------

    def _build_context_units(
        self,
        segments: list[dict[str, Any]],
        repetition_groups: list[RepetitionGroup],
    ) -> list[ContextUnit]:

        units: list[ContextUnit] = []

        repetition_lookup = {
            group.term
            for group in repetition_groups
        }

        for position, segment in enumerate(
            segments
        ):

            segment_index = int(
                segment.get(
                    "index",
                    position,
                )
            )

            text = str(
                segment.get(
                    "text",
                    "",
                )
            )

            normalized_text = str(
                segment.get(
                    "normalized_text",
                    text,
                )
            )

            segment_type = str(
                segment.get(
                    "segment_type",
                    "line",
                )
            )

            # Preserve the linguistic tokens!
            tokens = list(
                segment.get(
                    "tokens",
                    [],
                )
            )

            nearby_terms = (
                self._get_surrounding_terms(
                    position,
                    segments,
                )
            )

            repeated_terms: list[str] = []

            for token in tokens:

                normalized = str(
                    token.get(
                        "normalized",
                        "",
                    )
                ).lower()

                if normalized in repetition_lookup:

                    if normalized not in repeated_terms:

                        repeated_terms.append(
                            normalized
                        )

            clues = (
                self._detect_context_clues(
                    position,
                    segments,
                )
            )

            confidence = (
                self._calculate_context_confidence(
                    clues,
                    repeated_terms,
                    nearby_terms,
                )
            )

            previous_index = None
            next_index = None

            if position > 0:

                previous_index = int(
                    segments[
                        position - 1
                    ].get(
                        "index",
                        position - 1,
                    )
                )

            if position + 1 < len(
                segments
            ):

                next_index = int(
                    segments[
                        position + 1
                    ].get(
                        "index",
                        position + 1,
                    )
                )

            units.append(
                ContextUnit(
                    index=position,
                    segment_index=segment_index,
                    text=text,
                    normalized_text=normalized_text,
                    segment_type=segment_type,
                    tokens=tokens,
                    previous_segment_index=previous_index,
                    next_segment_index=next_index,
                    repeated_terms=repeated_terms,
                    surrounding_terms=nearby_terms,
                    clues=clues,
                    confidence=confidence,
                )
            )

        return units

    # ------------------------------------------------------------------
    # SURROUNDING TERMS
    # ------------------------------------------------------------------

    def _get_surrounding_terms(
        self,
        position: int,
        segments: list[dict[str, Any]],
    ) -> list[str]:

        terms: list[str] = []

        start = max(
            0,
            position - self.context_window,
        )

        end = min(
            len(segments),
            position
            + self.context_window
            + 1,
        )

        for neighbor_position in range(
            start,
            end,
        ):

            if neighbor_position == position:
                continue

            neighbor = segments[
                neighbor_position
            ]

            for token in neighbor.get(
                "tokens",
                [],
            ):

                if token.get(
                    "is_non_lexical",
                    False,
                ):
                    continue

                normalized = str(
                    token.get(
                        "normalized",
                        "",
                    )
                )

                if not normalized:
                    continue

                if normalized not in terms:
                    terms.append(
                        normalized
                    )

        return terms

    # ------------------------------------------------------------------
    # CONTEXT CLUES
    # ------------------------------------------------------------------

    def _detect_context_clues(
        self,
        position: int,
        segments: list[dict[str, Any]],
    ) -> list[ContextClue]:

        current_terms = (
            self._get_segment_terms(
                segments[position]
            )
        )

        previous_terms: list[str] = []

        next_terms: list[str] = []

        if position > 0:

            previous_terms = (
                self._get_segment_terms(
                    segments[
                        position - 1
                    ]
                )
            )

        if position + 1 < len(
            segments
        ):

            next_terms = (
                self._get_segment_terms(
                    segments[
                        position + 1
                    ]
                )
            )

        clues: list[ContextClue] = []

        # --------------------------------------------------------------
        # LOCAL
        # --------------------------------------------------------------

        self._append_marker_clue(
            clues,
            current_terms,
            CAUSAL_MARKERS,
            "causal_relation",
            0.90,
            "local",
        )

        self._append_marker_clue(
            clues,
            current_terms,
            CONTRAST_MARKERS,
            "contrast_relation",
            0.90,
            "local",
        )

        self._append_marker_clue(
            clues,
            current_terms,
            TEMPORAL_MARKERS,
            "temporal_reference",
            0.85,
            "local",
        )

        self._append_marker_clue(
            clues,
            current_terms,
            PERSISTENCE_MARKERS,
            "persistence",
            0.85,
            "local",
        )

        self._append_marker_clue(
            clues,
            current_terms,
            REPETITION_TEMPORAL_MARKERS,
            "temporal_recurrence",
            0.85,
            "local",
        )

        self._append_marker_clue(
            clues,
            current_terms,
            DURATION_MARKERS,
            "duration_or_permanence",
            0.80,
            "local",
        )

        self._append_marker_clue(
            clues,
            current_terms,
            CONDITION_MARKERS,
            "conditional_relation",
            0.85,
            "local",
        )

        self._append_marker_clue(
            clues,
            current_terms,
            NEGATION_MARKERS,
            "negation",
            0.95,
            "local",
        )

        self._append_marker_clue(
            clues,
            current_terms,
            INTENSIFIER_MARKERS,
            "intensification",
            0.80,
            "local",
        )

        first_person = self._intersection(
            current_terms,
            FIRST_PERSON_MARKERS,
        )

        if first_person:

            clues.append(
                ContextClue(
                    type="first_person_reference",
                    evidence=first_person,
                    strength=0.85,
                    evidence_scope="local",
                )
            )

        address = self._intersection(
            current_terms,
            ADDRESS_MARKERS,
        )

        if address:

            clues.append(
                ContextClue(
                    type="direct_address",
                    evidence=address,
                    strength=0.85,
                    evidence_scope="local",
                )
            )

        # --------------------------------------------------------------
        # IMMEDIATE CONTEXT
        # --------------------------------------------------------------

        self._append_immediate_context_clue(
            clues,
            previous_terms,
            next_terms,
            CAUSAL_MARKERS,
            "causal_context",
            0.45,
        )

        self._append_immediate_context_clue(
            clues,
            previous_terms,
            next_terms,
            CONTRAST_MARKERS,
            "contrast_context",
            0.45,
        )

        self._append_immediate_context_clue(
            clues,
            previous_terms,
            next_terms,
            TEMPORAL_MARKERS,
            "temporal_context",
            0.40,
        )

        self._append_immediate_context_clue(
            clues,
            previous_terms,
            next_terms,
            PERSISTENCE_MARKERS,
            "persistence_context",
            0.40,
        )

        self._append_immediate_context_clue(
            clues,
            previous_terms,
            next_terms,
            REPETITION_TEMPORAL_MARKERS,
            "recurrence_context",
            0.40,
        )

        self._append_immediate_context_clue(
            clues,
            previous_terms,
            next_terms,
            NEGATION_MARKERS,
            "negation_context",
            0.45,
        )

        return clues

    # ------------------------------------------------------------------
    # TERMS
    # ------------------------------------------------------------------

    @staticmethod
    def _get_segment_terms(
        segment: dict[str, Any],
    ) -> list[str]:

        terms: list[str] = []

        for token in segment.get(
            "tokens",
            [],
        ):

            if token.get(
                "is_non_lexical",
                False,
            ):
                continue

            normalized = str(
                token.get(
                    "normalized",
                    "",
                )
            ).lower()

            if normalized:
                terms.append(
                    normalized
                )

        return terms

    # ------------------------------------------------------------------
    # CLUE HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _append_marker_clue(
        clues: list[ContextClue],
        current_terms: list[str],
        marker_set: set[str],
        clue_type: str,
        strength: float,
        scope: str,
    ) -> None:

        evidence = (
            ContextEngine._intersection(
                current_terms,
                marker_set,
            )
        )

        if evidence:

            clues.append(
                ContextClue(
                    type=clue_type,
                    evidence=evidence,
                    strength=strength,
                    evidence_scope=scope,
                )
            )

    @staticmethod
    def _append_immediate_context_clue(
        clues: list[ContextClue],
        previous_terms: list[str],
        next_terms: list[str],
        marker_set: set[str],
        clue_type: str,
        strength: float,
    ) -> None:

        evidence: list[str] = []

        for terms in (
            previous_terms,
            next_terms,
        ):

            found = (
                ContextEngine._intersection(
                    terms,
                    marker_set,
                )
            )

            for item in found:

                if item not in evidence:
                    evidence.append(
                        item
                    )

        if evidence:

            clues.append(
                ContextClue(
                    type=clue_type,
                    evidence=evidence,
                    strength=strength,
                    evidence_scope="immediate_context",
                )
            )

    # ------------------------------------------------------------------
    # CONFIDENCE
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_context_confidence(
        clues: list[ContextClue],
        repeated_terms: list[str],
        surrounding_terms: list[str],
    ) -> float:

        score = 0.35

        local_clues = [
            clue
            for clue in clues
            if clue.evidence_scope == "local"
        ]

        immediate_clues = [
            clue
            for clue in clues
            if clue.evidence_scope
            == "immediate_context"
        ]

        score += min(
            0.35,
            0.08 * len(local_clues),
        )

        score += min(
            0.15,
            0.04 * len(immediate_clues),
        )

        score += min(
            0.10,
            0.05 * len(repeated_terms),
        )

        if surrounding_terms:

            score += min(
                0.05,
                0.005 * len(
                    surrounding_terms
                ),
            )

        return round(
            min(
                score,
                1.0,
            ),
            4,
        )

    # ------------------------------------------------------------------
    # GLOBAL CONTEXT
    # ------------------------------------------------------------------

    def _build_global_context(
        self,
        analysis: dict[str, Any],
        segments: list[dict[str, Any]],
        repetition_groups: list[RepetitionGroup],
    ) -> dict[str, Any]:

        token_counter: Counter[str] = Counter()

        for token in analysis.get(
            "global_tokens",
            [],
        ):

            if token.get(
                "is_non_lexical",
                False,
            ):
                continue

            normalized = str(
                token.get(
                    "normalized",
                    "",
                )
            )

            if normalized:

                token_counter[
                    normalized
                ] += 1

        repeated_terms = [
            {
                "term": term,
                "count": count,
            }
            for term, count
            in token_counter.most_common()
            if count >= 2
        ]

        structure = [
            {
                "index": segment.get(
                    "index"
                ),
                "text": segment.get(
                    "text"
                ),
                "segment_type": segment.get(
                    "segment_type"
                ),
            }
            for segment in segments
        ]

        return {
            "most_repeated_terms": (
                repeated_terms[:20]
            ),
            "structural_segments": structure,
            "has_repetition": bool(
                repetition_groups
            ),
            "has_multiple_segments": (
                len(segments) > 1
            ),
            "source_language": analysis.get(
                "language"
            ),
            "source_language_confidence": (
                analysis.get(
                    "language_confidence",
                    0.0,
                )
            ),
        }

    # ------------------------------------------------------------------
    # SERIALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def _context_unit_to_dict(
        unit: ContextUnit,
    ) -> dict[str, Any]:

        return asdict(
            unit
        )

    # ------------------------------------------------------------------
    # UTILITY
    # ------------------------------------------------------------------

    @staticmethod
    def _intersection(
        values: list[str],
        candidates: set[str],
    ) -> list[str]:

        candidate_lower = {
            value.lower()
            for value in candidates
        }

        result: list[str] = []

        for value in values:

            normalized = value.lower()

            if normalized in candidate_lower:

                if normalized not in result:
                    result.append(
                        normalized
                    )

        return result


# ---------------------------------------------------------------------------
# DEBUG OUTPUT
# ---------------------------------------------------------------------------

def _print_result(
    result: dict[str, Any],
) -> None:

    print("\n" + "=" * 72)
    print("SIGNMUSIC CONTEXT ENGINE")
    print("=" * 72)

    print(
        f"Status:              "
        f"{result['status']}"
    )

    print(
        f"Language:            "
        f"{result['language']}"
    )

    print(
        f"Language confidence: "
        f"{result['language_confidence']:.4f}"
    )

    print("\nContext units:")

    for unit in result[
        "context_units"
    ]:

        print(
            f"\n  [{unit['index']}] "
            f"{unit['text']}"
        )

        print(
            f"      Tokens:   "
            f"{len(unit['tokens'])}"
        )

        print(
            f"      Previous: "
            f"{unit['previous_segment_index']}"
        )

        print(
            f"      Next:     "
            f"{unit['next_segment_index']}"
        )

        print(
            f"      Repeated: "
            f"{unit['repeated_terms']}"
        )

        print(
            f"      Nearby:   "
            f"{unit['surrounding_terms']}"
        )

        for clue in unit[
            "clues"
        ]:

            print(
                f"      Clue: "
                f"{clue['type']} "
                f"{clue['evidence']} "
                f"(strength="
                f"{clue['strength']}, "
                f"scope="
                f"{clue['evidence_scope']})"
            )

        print(
            f"      Confidence: "
            f"{unit['confidence']}"
        )

    print("\nRepetition groups:")

    for group in result[
        "repetition_groups"
    ]:

        print(
            f"  {group['term']} "
            f"×{group['occurrences']} "
            f"segments="
            f"{group['segment_indices']}"
        )

    print("\nGlobal context:")

    global_context = result[
        "global_context"
    ]

    print("  Most repeated:")

    for item in global_context[
        "most_repeated_terms"
    ]:

        print(
            f"    - {item['term']}: "
            f"{item['count']}"
        )

    print(
        f"  Has repetition: "
        f"{global_context['has_repetition']}"
    )

    print(
        f"  Multiple segments: "
        f"{global_context['has_multiple_segments']}"
    )

    print("\nMetadata:")

    for key, value in result[
        "metadata"
    ].items():

        print(
            f"  {key}: {value}"
        )


# ---------------------------------------------------------------------------
# TEST
# ---------------------------------------------------------------------------

def main() -> None:

    engine = ContextEngine()

    lyrics = """I cannot find you
I still need you
I feel alive again
I am alone and broken"""

    result = engine.analyze(
        lyrics
    )

    _print_result(
        result
    )


if __name__ == "__main__":
    main()