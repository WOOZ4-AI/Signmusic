from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass
from typing import Any

from .universal_meaning import UniversalMeaningEngine


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class NarrativeRelation:
    source_unit: int
    target_unit: int
    relation: str
    confidence: float
    evidence: list[str]


@dataclass
class NarrativeState:
    unit_index: int
    emotional_polarity: str | None
    relationships: list[str]
    active_participants: list[str]
    continuity_score: float


@dataclass
class NarrativeMeaning:
    theme_candidates: list[str]
    dominant_relationships: list[str]
    emotional_arc: list[str]
    narrative_relations: list[NarrativeRelation]
    states: list[NarrativeState]
    confidence: float
    uncertainty: list[str]


# ============================================================================
# NARRATIVE ENGINE
# ============================================================================

class NarrativeContextEngine:
    """
    Song-level meaning layer.

    Converts independent Universal Meaning units into a connected
    representation of how the song develops over time.

    Processing:

        Language
            ↓
        Linguistic
            ↓
        Context
            ↓
        Semantic
            ↓
        Universal Meaning
            ↓
        Narrative Context        <-- this module
            ↓
        Sign-language realization
    """

    def __init__(
        self,
        universal_meaning_engine: UniversalMeaningEngine | None = None,
    ) -> None:

        self.universal_meaning_engine = (
            universal_meaning_engine
            or UniversalMeaningEngine()
        )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze(
        self,
        lyrics_or_meaning: str | dict[str, Any],
    ) -> dict[str, Any]:

        if isinstance(
            lyrics_or_meaning,
            str,
        ):

            meaning = (
                self.universal_meaning_engine.analyze(
                    lyrics_or_meaning
                )
            )

        elif isinstance(
            lyrics_or_meaning,
            dict,
        ):

            meaning = lyrics_or_meaning

        else:

            raise TypeError(
                "lyrics_or_meaning must be "
                "a string or dictionary"
            )

        units = meaning.get(
            "units",
            [],
        )

        relations = (
            self._build_narrative_relations(
                units
            )
        )

        states = (
            self._build_narrative_states(
                units
            )
        )

        theme_candidates = (
            self._infer_themes(
                units,
                relations,
            )
        )

        dominant_relationships = (
            self._infer_dominant_relationships(
                units
            )
        )

        emotional_arc = (
            self._build_emotional_arc(
                states
            )
        )

        uncertainty = (
            self._build_uncertainty(
                units
            )
        )

        confidence = (
            self._calculate_confidence(
                units,
                relations,
                theme_candidates,
            )
        )

        narrative_meaning = (
            NarrativeMeaning(
                theme_candidates=theme_candidates,
                dominant_relationships=(
                    dominant_relationships
                ),
                emotional_arc=emotional_arc,
                narrative_relations=relations,
                states=states,
                confidence=confidence,
                uncertainty=uncertainty,
            )
        )

        return {
            "status": (
                "ok"
                if units
                else "no_narrative"
            ),

            "source_language": meaning.get(
                "source_language"
            ),

            "source_language_name": meaning.get(
                "source_language_name"
            ),

            "source_language_confidence": (
                meaning.get(
                    "source_language_confidence",
                    0.0,
                )
            ),

            "units": units,

            "narrative": {
                "theme_candidates": (
                    narrative_meaning.theme_candidates
                ),
                "dominant_relationships": (
                    narrative_meaning.dominant_relationships
                ),
                "emotional_arc": (
                    narrative_meaning.emotional_arc
                ),
                "narrative_relations": [
                    asdict(relation)
                    for relation
                    in narrative_meaning.narrative_relations
                ],
                "states": [
                    asdict(state)
                    for state
                    in narrative_meaning.states
                ],
                "confidence": (
                    narrative_meaning.confidence
                ),
                "uncertainty": (
                    narrative_meaning.uncertainty
                ),
            },

            "interpretation_policy": {
                "final_interpretation": False,
                "artist_intent_claimed": False,
                "narrative_is_candidate": True,
            },

            "metadata": {
                "unit_count": len(units),
                "relation_count": len(relations),
                "state_count": len(states),
                "theme_count": len(
                    theme_candidates
                ),
            },
        }

    # ------------------------------------------------------------------
    # NARRATIVE RELATIONS
    # ------------------------------------------------------------------

    def _build_narrative_relations(
        self,
        units: list[dict[str, Any]],
    ) -> list[NarrativeRelation]:

        relations: list[
            NarrativeRelation
        ] = []

        for index in range(
            len(units) - 1
        ):

            current = units[index]
            following = units[index + 1]

            current_relations = {
                relation.get("type")
                for relation
                in current.get(
                    "relations",
                    [],
                )
            }

            next_relations = {
                relation.get("type")
                for relation
                in following.get(
                    "relations",
                    [],
                )
            }

            current_emotions = (
                self._get_emotional_polarity(
                    current
                )
            )

            next_emotions = (
                self._get_emotional_polarity(
                    following
                )
            )

            # ----------------------------------------------------------
            # NEED → ABSENCE
            # ----------------------------------------------------------

            if (
                "need_toward_person"
                in current_relations
                and
                "possible_absence_or_separation"
                in next_relations
            ):

                relations.append(
                    NarrativeRelation(
                        source_unit=index,
                        target_unit=index + 1,
                        relation=(
                            "need_precedes_absence"
                        ),
                        confidence=0.65,
                        evidence=[
                            "need_toward_person",
                            "possible_absence_or_separation",
                        ],
                    )
                )

            # ----------------------------------------------------------
            # ABSENCE → NEED
            # ----------------------------------------------------------

            if (
                "possible_absence_or_separation"
                in current_relations
                and
                "need_toward_person"
                in next_relations
            ):

                relations.append(
                    NarrativeRelation(
                        source_unit=index,
                        target_unit=index + 1,
                        relation=(
                            "absence_precedes_need"
                        ),
                        confidence=0.72,
                        evidence=[
                            "possible_absence_or_separation",
                            "need_toward_person",
                        ],
                    )
                )

            # ----------------------------------------------------------
            # EMOTIONAL CHANGE
            # ----------------------------------------------------------

            if (
                current_emotions
                and next_emotions
                and current_emotions
                != next_emotions
            ):

                relations.append(
                    NarrativeRelation(
                        source_unit=index,
                        target_unit=index + 1,
                        relation=(
                            "emotional_state_change"
                        ),
                        confidence=0.75,
                        evidence=[
                            current_emotions,
                            next_emotions,
                        ],
                    )
                )

            # ----------------------------------------------------------
            # CONTINUATION
            # ----------------------------------------------------------

            if self._shares_participant(
                current,
                following,
            ):

                relations.append(
                    NarrativeRelation(
                        source_unit=index,
                        target_unit=index + 1,
                        relation=(
                            "participant_continuity"
                        ),
                        confidence=0.80,
                        evidence=[
                            "shared_participant"
                        ],
                    )
                )

            # ----------------------------------------------------------
            # REPETITION / PERSISTENCE
            # ----------------------------------------------------------

            if (
                self._has_relation(
                    current,
                    "need_toward_person",
                )
                and
                self._has_relation(
                    following,
                    "need_toward_person",
                )
            ):

                relations.append(
                    NarrativeRelation(
                        source_unit=index,
                        target_unit=index + 1,
                        relation=(
                            "repeated_need"
                        ),
                        confidence=0.88,
                        evidence=[
                            "need_toward_person"
                        ],
                    )
                )

        return relations

    # ------------------------------------------------------------------
    # NARRATIVE STATES
    # ------------------------------------------------------------------

    def _build_narrative_states(
        self,
        units: list[dict[str, Any]],
    ) -> list[NarrativeState]:

        states: list[
            NarrativeState
        ] = []

        for index, unit in enumerate(
            units
        ):

            emotional_polarity = (
                self._get_emotional_polarity(
                    unit
                )
            )

            relationships = [
                relation.get(
                    "type"
                )
                for relation
                in unit.get(
                    "relations",
                    [],
                )
                if relation.get(
                    "type"
                )
            ]

            participants = [
                participant.get(
                    "reference"
                )
                for participant
                in unit.get(
                    "participants",
                    [],
                )
                if participant.get(
                    "reference"
                )
            ]

            continuity = (
                self._calculate_continuity(
                    index,
                    units,
                )
            )

            states.append(
                NarrativeState(
                    unit_index=index,
                    emotional_polarity=(
                        emotional_polarity
                    ),
                    relationships=[
                        str(item)
                        for item
                        in relationships
                    ],
                    active_participants=[
                        str(item)
                        for item
                        in participants
                    ],
                    continuity_score=continuity,
                )
            )

        return states

    # ------------------------------------------------------------------
    # THEMES
    # ------------------------------------------------------------------

    def _infer_themes(
        self,
        units: list[dict[str, Any]],
        relations: list[NarrativeRelation],
    ) -> list[str]:

        candidates: list[str] = []

        relation_counts = Counter(
            relation.get("type")
            for unit in units
            for relation in unit.get(
                "relations",
                 [],
            )
            if isinstance(relation, dict)
            and relation.get("type")
        )

        figurative_concepts: list[
            str
        ] = []

        for unit in units:

            figurative = unit.get(
                "figurative",
                {},
            )

            if not figurative.get(
                "present",
                False,
            ):
                continue

            concept = figurative.get(
                "concept"
            )

            if concept:
                figurative_concepts.append(
                    str(concept)
                )

        # --------------------------------------------------------------
        # ATTACHMENT
        # --------------------------------------------------------------

        attachment_score = (
            relation_counts.get(
                "need_toward_person",
                0,
            )
            + relation_counts.get(
                "affection_toward_person",
                0,
            )
            + relation_counts.get(
                "strong_attachment",
                0,
            )
        )

        if attachment_score >= 2:

            candidates.append(
                "attachment_to_another_person"
            )

        # --------------------------------------------------------------
        # ABSENCE
        # --------------------------------------------------------------

        absence_score = (
            relation_counts.get(
                "possible_absence_or_separation",
                0,
            )
            + relation_counts.get(
                "attachment_with_absence",
                0,
            )
            + relation_counts.get(
                "unsuccessful_search",
                0,
            )
        )

        if absence_score >= 1:

            candidates.append(
                "absence_or_separation"
            )

        # --------------------------------------------------------------
        # EMOTIONAL CHANGE
        # --------------------------------------------------------------

        emotional_changes = sum(
            1
            for relation in relations
            if relation.relation
            == "emotional_state_change"
        )

        if emotional_changes > 0:

            candidates.append(
                "emotional_transformation"
            )

        # --------------------------------------------------------------
        # FIGURATIVE LOVE / AFFECTION
        # --------------------------------------------------------------

        if any(
            concept
            in {
                "intense_affection",
                "deep_affection_and_positive_importance",
                "emotional_dependency",
            }
            for concept
            in figurative_concepts
        ):

            candidates.append(
                "intense_relationship_expression"
            )

        # --------------------------------------------------------------
        # REPEATED NEED
        # --------------------------------------------------------------

        repeated_need = sum(
            1
            for relation in relations
            if relation.relation
            == "repeated_need"
        )

        if repeated_need > 0:

            candidates.append(
                "persistent_need"
            )

        return list(
            dict.fromkeys(
                candidates
            )
        )

    # ------------------------------------------------------------------
    # DOMINANT RELATIONSHIPS
    # ------------------------------------------------------------------

    @staticmethod
    def _infer_dominant_relationships(
        units: list[dict[str, Any]],
    ) -> list[str]:

        counter: Counter[str] = Counter()

        for unit in units:

            for relation in unit.get(
                "relations",
                [],
            ):

                relation_type = (
                    relation.get(
                        "type"
                    )
                )

                if relation_type:
                    counter[
                        relation_type
                    ] += 1

        return [
            relation
            for relation, _count
            in counter.most_common(10)
        ]

    # ------------------------------------------------------------------
    # EMOTIONAL ARC
    # ------------------------------------------------------------------

    @staticmethod
    def _build_emotional_arc(
        states: list[NarrativeState],
    ) -> list[str]:

        arc: list[str] = []

        for state in states:

            polarity = (
                state.emotional_polarity
            )

            if polarity is None:
                continue

            if not arc:

                arc.append(
                    polarity
                )

                continue

            if arc[-1] != polarity:

                arc.append(
                    polarity
                )

        return arc

    # ------------------------------------------------------------------
    # EMOTIONAL POLARITY
    # ------------------------------------------------------------------

    @staticmethod
    def _get_emotional_polarity(
        unit: dict[str, Any],
    ) -> str | None:

        emotions = unit.get(
            "emotions",
            [],
        )

        for emotion in emotions:

            polarity = emotion.get(
                "polarity"
            )

            if polarity:
                return str(
                    polarity
                )

        return None

    # ------------------------------------------------------------------
    # CONTINUITY
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_continuity(
        index: int,
        units: list[dict[str, Any]],
    ) -> float:

        if index == 0:
            return 0.5

        current = units[index]
        previous = units[index - 1]

        score = 0.0

        if NarrativeContextEngine._shares_participant(
            previous,
            current,
        ):
            score += 0.5

        if (
            NarrativeContextEngine._get_emotional_polarity(
                previous
            )
            == NarrativeContextEngine._get_emotional_polarity(
                current
            )
        ):

            score += 0.3

        if (
            NarrativeContextEngine._has_relation(
                current,
                "persistence_relation",
            )
        ):

            score += 0.2

        return round(
            min(
                score,
                1.0,
            ),
            4,
        )

    # ------------------------------------------------------------------
    # PARTICIPANT CONTINUITY
    # ------------------------------------------------------------------

    @staticmethod
    def _shares_participant(
        first: dict[str, Any],
        second: dict[str, Any],
    ) -> bool:

        first_participants = {
            participant.get(
                "reference"
            )
            for participant
            in first.get(
                "participants",
                [],
            )
        }

        second_participants = {
            participant.get(
                "reference"
            )
            for participant
            in second.get(
                "participants",
                [],
            )
        }

        return bool(
            first_participants
            & second_participants
        )

    # ------------------------------------------------------------------
    # RELATION CHECK
    # ------------------------------------------------------------------

    @staticmethod
    def _has_relation(
        unit: dict[str, Any],
        relation_name: str,
    ) -> bool:

        return any(
            relation.get("type")
            == relation_name
            for relation
            in unit.get(
                "relations",
                [],
            )
        )

    # ------------------------------------------------------------------
    # UNCERTAINTY
    # ------------------------------------------------------------------

    @staticmethod
    def _build_uncertainty(
        units: list[dict[str, Any]],
    ) -> list[str]:

        uncertainty: list[str] = []

        for unit in units:

            for item in unit.get(
                "uncertainty",
                [],
            ):

                item = str(
                    item
                )

                if item not in uncertainty:

                    uncertainty.append(
                        item
                    )

        return uncertainty

    # ------------------------------------------------------------------
    # CONFIDENCE
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_confidence(
        units: list[dict[str, Any]],
        relations: list[NarrativeRelation],
        themes: list[str],
    ) -> float:

        if not units:
            return 0.0

        unit_confidences = [
            float(
                unit.get(
                    "confidence",
                    0.0,
                )
            )
            for unit in units
        ]

        average_unit_confidence = (
            sum(unit_confidences)
            / len(unit_confidences)
        )

        if relations:

            relation_confidence = (
                sum(
                    relation.confidence
                    for relation
                    in relations
                )
                / len(relations)
            )

        else:

            relation_confidence = 0.0

        theme_bonus = min(
            0.15,
            0.05 * len(themes),
        )

        if relations:

            score = (
                average_unit_confidence
                * 0.50
                + relation_confidence
                * 0.35
                + theme_bonus
            )

        else:

            score = (
                average_unit_confidence
                * 0.75
                + theme_bonus
            )

        return round(
            min(
                score,
                1.0,
            ),
            4,
        )


# ============================================================================
# DEBUG OUTPUT
# ============================================================================


def _print_result(
    result: dict[str, Any],
) -> None:

    print("\n" + "=" * 72)
    print(
        "SIGNMUSIC NARRATIVE CONTEXT"
    )
    print("=" * 72)

    print(
        f"Status: "
        f"{result['status']}"
    )

    print(
        f"Language: "
        f"{result['source_language']}"
    )

    print(
        f"Confidence: "
        f"{result['narrative']['confidence']}"
    )

    print(
        "\nTheme candidates:"
    )

    for theme in result[
        "narrative"
    ][
        "theme_candidates"
    ]:

        print(
            f"  - {theme}"
        )

    print(
        "\nDominant relationships:"
    )

    for relation in result[
        "narrative"
    ][
        "dominant_relationships"
    ]:

        print(
            f"  - {relation}"
        )

    print(
        "\nEmotional arc:"
    )

    print(
        f"  {' → '.join(result['narrative']['emotional_arc'])}"
    )

    print(
        "\nNarrative relations:"
    )

    for relation in result[
        "narrative"
    ][
        "narrative_relations"
    ]:

        print(
            f"  [{relation['source_unit']}] "
            f"--{relation['relation']}-->"
            f" [{relation['target_unit']}] "
            f"(confidence="
            f"{relation['confidence']})"
        )

    print(
        "\nStates:"
    )

    for state in result[
        "narrative"
    ][
        "states"
    ]:

        print(
            f"  [{state['unit_index']}] "
            f"emotion="
            f"{state['emotional_polarity']} "
            f"continuity="
            f"{state['continuity_score']}"
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

    engine = (
        NarrativeContextEngine()
    )

    lyrics = """I cannot find you
I still need you
I feel alive again
I am alone and broken
I need you forever"""

    result = engine.analyze(
        lyrics
    )

    _print_result(
        result
    )


if __name__ == "__main__":
    main()