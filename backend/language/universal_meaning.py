from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
from typing import Any

from .semantic_engine import SemanticEngine


# ============================================================================
# UNIVERSAL CONCEPT NORMALIZATION
# ============================================================================
#
# These mappings intentionally use language-independent semantic concepts.
#
# Example:
#
#   "I still need you"
#            ↓
#   expressed_need_toward_person
#            ↓
#   strong_attachment (candidate)
#
# The goal is NOT to create the final DGS structure.
# The goal is to create a stable meaning representation that any target
# language can consume later.
# ============================================================================


CONCEPT_TO_RELATION = {
    "expressed_need_toward_person": "need_toward_person",
    "persistent_attachment_candidate": "persistent_attachment",
    "attachment_with_absence": "attachment_with_absence",
    "affection_toward_person": "affection_toward_person",
    "intense_affection": "intense_affection",
    "emotional_dependency": "emotional_dependency",
    "possible_absence_or_separation": "possible_absence_or_separation",
    "unsuccessful_search_for_person": "unsuccessful_search",
    "deep_affection_and_positive_importance": (
        "deep_positive_importance"
    ),
}

EMOTION_CONCEPTS = {
    "positive_emotional_state": "positive",
    "negative_emotional_state": "negative",
    "felt_emotional_state": "felt_state",
    "emotional_state_contrast": "mixed",
}

FIGURATIVE_CATEGORIES = {
    "figurative_language",
    "idiomatic_language",
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class UniversalParticipant:
    id: str
    role: str
    reference: str
    certainty: float


@dataclass
class UniversalEvent:
    predicate: str | None
    action: str | None
    agent: str | None
    target: str | None
    state: str | None
    modality: str | None
    negated: bool
    result: str | None


@dataclass
class UniversalEmotion:
    category: str
    polarity: str | None
    intensity: float | None
    source: str
    certainty: float


@dataclass
class UniversalRelation:
    type: str
    source: str | None
    target: str | None
    certainty: float
    evidence: list[str] = field(
        default_factory=list
    )


@dataclass
class UniversalFigurativeMeaning:
    present: bool
    type: str | None
    concept: str | None
    interpretation: str | None
    certainty: float
    source_phrase: str | None


@dataclass
class UniversalMeaningUnit:
    unit_id: int
    segment_index: int
    source_text: str

    participants: list[
        UniversalParticipant
    ]

    event: UniversalEvent | None

    emotions: list[
        UniversalEmotion
    ]

    relations: list[
        UniversalRelation
    ]

    figurative: UniversalFigurativeMeaning

    temporal: dict[str, Any]
    discourse: dict[str, Any]

    confidence: float
    uncertainty: list[str]


# ============================================================================
# UNIVERSAL MEANING ENGINE
# ============================================================================


class UniversalMeaningEngine:
    """
    Converts SemanticEngine output into a language-independent representation.

    Processing:

        Source language
            ↓
        Linguistic analysis
            ↓
        Context
            ↓
        Semantic structure
            ↓
        Universal Meaning       ← this module
            ↓
        Target sign language
            ↓
        Sign grammar
            ↓
        Motion / avatar

    Important:

        Universal Meaning is NOT:
            - English
            - Spanish
            - DGS
            - ASL
            - literal translation

        It is a semantic representation.

    The engine preserves uncertainty and evidence.
    """

    def __init__(
        self,
        semantic_engine: SemanticEngine | None = None,
    ) -> None:

        self.semantic_engine = (
            semantic_engine
            or SemanticEngine()
        )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze(
        self,
        lyrics_or_semantics: str | dict[str, Any],
    ) -> dict[str, Any]:
        """
        Accept:

            raw lyrics

        OR:

            SemanticEngine output.
        """

        if isinstance(
            lyrics_or_semantics,
            str,
        ):

            semantic_analysis = (
                self.semantic_engine.analyze(
                    lyrics_or_semantics
                )
            )

        elif isinstance(
            lyrics_or_semantics,
            dict,
        ):

            semantic_analysis = (
                lyrics_or_semantics
            )

        else:

            raise TypeError(
                "lyrics_or_semantics must be "
                "a string or dictionary"
            )

        structures = (
            semantic_analysis.get(
                "semantic_structures",
                [],
            )
        )

        candidates = (
            semantic_analysis.get(
                "candidates",
                [],
            )
        )

        candidates_by_segment = (
            self._group_candidates_by_segment(
                candidates
            )
        )

        units: list[
            UniversalMeaningUnit
        ] = []

        for structure in structures:

            segment_index = int(
                structure.get(
                    "segment_index",
                    -1,
                )
            )

            source_text = str(
                structure.get(
                    "text",
                    "",
                )
            )

            segment_candidates = (
                candidates_by_segment.get(
                    segment_index,
                    [],
                )
            )

            unit = (
                self._build_unit(
                    structure,
                    segment_candidates,
                )
            )

            units.append(
                unit
            )

        song_meaning = (
            self._build_song_meaning(
                units,
                semantic_analysis,
            )
        )

        return {
            "status": self._determine_status(
                semantic_analysis
            ),
            "source_language": semantic_analysis.get(
                "language"
            ),
            "source_language_name": semantic_analysis.get(
                "language_name"
            ),
            "source_language_confidence": semantic_analysis.get(
                "language_confidence",
                0.0,
            ),
            "units": [
                self._unit_to_dict(
                    unit
                )
                for unit in units
            ],
            "song_meaning": song_meaning,
            "guarantees": {
                "target_language_independent": True,
                "not_a_literal_translation": True,
                "artist_intent_not_claimed": True,
                "uncertainty_preserved": True,
            },
            "metadata": {
                "unit_count": len(
                    units
                ),
                "candidate_count": len(
                    candidates
                ),
                "song_level_candidates": len(
                    semantic_analysis.get(
                        "song_level_interpretations",
                        [],
                    )
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

        if analysis.get(
            "status"
        ) == "empty":

            return "empty"

        if not analysis.get(
            "semantic_structures"
        ):

            return "no_meaning"

        return "ok"

    # ------------------------------------------------------------------
    # GROUP CANDIDATES
    # ------------------------------------------------------------------

    @staticmethod
    def _group_candidates_by_segment(
        candidates: list[dict[str, Any]],
    ) -> dict[
        int,
        list[dict[str, Any]],
    ]:

        grouped: dict[
            int,
            list[dict[str, Any]],
        ] = {}

        for candidate in candidates:

            segment_index = int(
                candidate.get(
                    "segment_index",
                    -1,
                )
            )

            # Song-level candidates have segment -1
            # and are handled separately.
            if segment_index < 0:
                continue

            grouped.setdefault(
                segment_index,
                [],
            ).append(
                candidate
            )

        return grouped

    # ------------------------------------------------------------------
    # BUILD UNIT
    # ------------------------------------------------------------------

    def _build_unit(
        self,
        structure: dict[str, Any],
        candidates: list[dict[str, Any]],
    ) -> UniversalMeaningUnit:

        segment_index = int(
            structure.get(
                "segment_index",
                -1,
            )
        )

        source_text = str(
            structure.get(
                "text",
                "",
            )
        )

        participants = (
            self._build_participants(
                structure
            )
        )

        event = (
            self._build_event(
                structure
            )
        )

        emotions = (
            self._build_emotions(
                structure,
                candidates,
            )
        )

        relations = (
            self._build_relations(
                structure,
                candidates,
            )
        )

        figurative = (
            self._build_figurative(
                source_text,
                candidates,
            )
        )

        temporal = {
            "temporal": structure.get(
                "temporal"
            ),
            "persistence": structure.get(
                "persistence"
            ),
            "duration": structure.get(
                "duration"
            ),
        }

        discourse = {
            "relations": structure.get(
                "relations",
                [],
            ),
        }

        uncertainty = (
            self._build_uncertainty(
                candidates
            )
        )

        confidence = (
            self._calculate_unit_confidence(
                structure,
                candidates,
            )
        )

        return UniversalMeaningUnit(
            unit_id=segment_index,
            segment_index=segment_index,
            source_text=source_text,
            participants=participants,
            event=event,
            emotions=emotions,
            relations=relations,
            figurative=figurative,
            temporal=temporal,
            discourse=discourse,
            confidence=confidence,
            uncertainty=uncertainty,
        )

    # ------------------------------------------------------------------
    # PARTICIPANTS
    # ------------------------------------------------------------------

    @staticmethod
    def _build_participants(
        structure: dict[str, Any],
    ) -> list[
        UniversalParticipant
    ]:

        participants: list[
            UniversalParticipant
        ] = []

        agent = structure.get(
            "agent"
        )

        if agent:

            participants.append(
                UniversalParticipant(
                    id="P1",
                    role="agent",
                    reference=agent,
                    certainty=0.90,
                )
            )

        target = structure.get(
            "target"
        )

        if target:

            participants.append(
                UniversalParticipant(
                    id="P2",
                    role="target",
                    reference=target,
                    certainty=0.90,
                )
            )

        possessor = structure.get(
            "possessor"
        )

        if (
            possessor
            and possessor != agent
        ):

            participants.append(
                UniversalParticipant(
                    id="P3",
                    role="possessor",
                    reference=possessor,
                    certainty=0.80,
                )
            )

        return participants

    # ------------------------------------------------------------------
    # EVENT
    # ------------------------------------------------------------------

    @staticmethod
    def _build_event(
        structure: dict[str, Any],
    ) -> UniversalEvent | None:

        has_event_information = any(
            structure.get(key) is not None
            for key in (
                "action",
                "predicate",
                "agent",
                "target",
                "modality",
                "result",
            )
        )

        if not has_event_information:
            return None

        return UniversalEvent(
            predicate=structure.get(
                "predicate"
            ),
            action=structure.get(
                "action"
            ),
            agent=structure.get(
                "agent"
            ),
            target=structure.get(
                "target"
            ),
            state=structure.get(
                "state"
            ),
            modality=structure.get(
                "modality"
            ),
            negated=bool(
                structure.get(
                    "negated",
                    False,
                )
            ),
            result=structure.get(
                "result"
            ),
        )

    # ------------------------------------------------------------------
    # EMOTIONS
    # ------------------------------------------------------------------

    def _build_emotions(
        self,
        structure: dict[str, Any],
        candidates: list[dict[str, Any]],
    ) -> list[
        UniversalEmotion
    ]:

        emotions: list[
            UniversalEmotion
        ] = []

        state = structure.get(
            "state"
        )

        if state:

            polarity = (
                "positive"
                if state
                == "positive_emotional_state"
                else (
                    "negative"
                    if state
                    == "negative_emotional_state"
                    else "mixed"
                )
            )

            emotions.append(
                UniversalEmotion(
                    category="emotional_state",
                    polarity=polarity,
                    intensity=None,
                    source="semantic_structure",
                    certainty=0.75,
                )
            )

        for candidate in candidates:

            concept = candidate.get(
                "concept"
            )

            if concept in EMOTION_CONCEPTS:

                emotions.append(
                    UniversalEmotion(
                        category=EMOTION_CONCEPTS[
                            concept
                        ],
                        polarity=self._emotion_polarity(
                            concept
                        ),
                        intensity=None,
                        source="semantic_candidate",
                        certainty=float(
                            candidate.get(
                                "confidence",
                                0.0,
                            )
                        ),
                    )
                )

        return self._deduplicate_emotions(
            emotions
        )

    @staticmethod
    def _emotion_polarity(
        concept: str,
    ) -> str | None:

        if concept == (
            "positive_emotional_state"
        ):
            return "positive"

        if concept == (
            "negative_emotional_state"
        ):
            return "negative"

        if concept == (
            "emotional_state_contrast"
        ):
            return "mixed"

        return None

    # ------------------------------------------------------------------
    # RELATIONS
    # ------------------------------------------------------------------

    def _build_relations(
        self,
        structure: dict[str, Any],
        candidates: list[dict[str, Any]],
    ) -> list[
        UniversalRelation
    ]:

        relations: list[
            UniversalRelation
        ] = []

        for relation in structure.get(
            "relations",
            [],
        ):

            relations.append(
                UniversalRelation(
                    type=relation,
                    source=structure.get(
                        "agent"
                    ),
                    target=structure.get(
                        "target"
                    ),
                    certainty=0.70,
                    evidence=[],
                )
            )

        for candidate in candidates:

            concept = candidate.get(
                "concept"
            )

            normalized_relation = (
                CONCEPT_TO_RELATION.get(
                    concept
                )
            )

            if not normalized_relation:
                continue

            evidence_terms = []

            for evidence in candidate.get(
                "evidence",
                [],
            ):

                evidence_terms.extend(
                    evidence.get(
                        "source_terms",
                        [],
                    )
                )

            relations.append(
                UniversalRelation(
                    type=normalized_relation,
                    source=structure.get(
                        "agent"
                    ),
                    target=structure.get(
                        "target"
                    ),
                    certainty=float(
                        candidate.get(
                            "confidence",
                            0.0,
                        )
                    ),
                    evidence=list(
                        dict.fromkeys(
                            evidence_terms
                        )
                    ),
                )
            )

        return self._deduplicate_relations(
            relations
        )

    # ------------------------------------------------------------------
    # FIGURATIVE
    # ------------------------------------------------------------------

    def _build_figurative(
        self,
        source_text: str,
        candidates: list[dict[str, Any]],
    ) -> UniversalFigurativeMeaning:

        figurative_candidates = [
            candidate
            for candidate
            in candidates
            if candidate.get(
                "figurative"
            ) is True
            or candidate.get(
                "category"
            ) in FIGURATIVE_CATEGORIES
        ]

        if not figurative_candidates:

            return UniversalFigurativeMeaning(
                present=False,
                type=None,
                concept=None,
                interpretation=None,
                certainty=1.0,
                source_phrase=None,
            )

        best = max(
            figurative_candidates,
            key=lambda candidate: float(
                candidate.get(
                    "confidence",
                    0.0,
                )
            ),
        )

        category = best.get(
            "category"
        )

        figurative_type = (
            "idiom"
            if category
            == "idiomatic_language"
            else "figurative_expression"
        )

        source_phrase = None

        evidence = best.get(
            "evidence",
            [],
        )

        for item in evidence:

            source_terms = item.get(
                "source_terms",
                [],
            )

            if source_terms:

                source_phrase = str(
                    source_terms[0]
                )

                break

        return UniversalFigurativeMeaning(
            present=True,
            type=figurative_type,
            concept=best.get(
                "concept"
            ),
            interpretation=best.get(
                "interpretation"
            ),
            certainty=float(
                best.get(
                    "confidence",
                    0.0,
                )
            ),
            source_phrase=source_phrase,
        )

    # ------------------------------------------------------------------
    # UNCERTAINTY
    # ------------------------------------------------------------------

    @staticmethod
    def _build_uncertainty(
        candidates: list[dict[str, Any]],
    ) -> list[str]:

        uncertainty: list[str] = []

        for candidate in candidates:

            text = candidate.get(
                "uncertainty"
            )

            if not text:
                continue

            text = str(
                text
            )

            if text not in uncertainty:
                uncertainty.append(
                    text
                )

        return uncertainty

    # ------------------------------------------------------------------
    # CONFIDENCE
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_unit_confidence(
        structure: dict[str, Any],
        candidates: list[dict[str, Any]],
    ) -> float:

        structural_fields = [
            "agent",
            "action",
            "predicate",
            "target",
            "state",
        ]

        available = sum(
            1
            for field_name
            in structural_fields
            if structure.get(
                field_name
            ) is not None
        )

        structural_score = (
            min(
                1.0,
                available
                / len(
                    structural_fields
                ),
            )
            if structural_fields
            else 0.0
        )

        candidate_scores = [
            float(
                candidate.get(
                    "confidence",
                    0.0,
                )
            )
            for candidate
            in candidates
            if candidate.get(
                "confidence"
            ) is not None
        ]

        if candidate_scores:

            candidate_score = sum(
                candidate_scores
            ) / len(
                candidate_scores
            )

        else:

            candidate_score = 0.0

        if (
            structural_score > 0
            and candidate_scores
        ):

            score = (
                structural_score
                * 0.40
                + candidate_score
                * 0.60
            )

        elif structural_score > 0:

            score = (
                structural_score
                * 0.75
            )

        else:

            score = candidate_score

        return round(
            min(
                score,
                1.0,
            ),
            4,
        )

    # ------------------------------------------------------------------
    # SONG MEANING
    # ------------------------------------------------------------------

    def _build_song_meaning(
        self,
        units: list[
            UniversalMeaningUnit
        ],
        semantic_analysis: dict[str, Any],
    ) -> dict[str, Any]:

        relation_counts: Counter[str] = (
            Counter()
        )

        emotion_counts: Counter[str] = (
            Counter()
        )

        figurative_count = 0

        for unit in units:

            for relation in unit.relations:

                relation_counts[
                    relation.type
                ] += 1

            for emotion in unit.emotions:

                key = (
                    f"{emotion.category}:"
                    f"{emotion.polarity}"
                )

                emotion_counts[
                    key
                ] += 1

            if unit.figurative.present:
                figurative_count += 1

        top_relations = [
            {
                "type": relation,
                "count": count,
            }
            for relation, count
            in relation_counts.most_common()
        ]

        top_emotions = [
            {
                "type": emotion,
                "count": count,
            }
            for emotion, count
            in emotion_counts.most_common()
        ]

        return {
            "dominant_relations": (
                top_relations[:10]
            ),
            "dominant_emotional_patterns": (
                top_emotions[:10]
            ),
            "figurative_unit_count": (
                figurative_count
            ),
            "candidate_interpretations": (
                semantic_analysis.get(
                    "song_level_interpretations",
                    [],
                )
            ),
            "interpretation_policy": {
                "is_final": False,
                "requires_context": True,
                "artist_intent_known": False,
            },
        }

    # ------------------------------------------------------------------
    # DEDUPLICATION
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate_emotions(
        emotions: list[
            UniversalEmotion
        ],
    ) -> list[
        UniversalEmotion
    ]:

        result: list[
            UniversalEmotion
        ] = []

        seen: set[
            tuple[str, str | None]
        ] = set()

        for emotion in emotions:

            key = (
                emotion.category,
                emotion.polarity,
            )

            if key in seen:
                continue

            seen.add(
                key
            )

            result.append(
                emotion
            )

        return result

    @staticmethod
    def _deduplicate_relations(
        relations: list[
            UniversalRelation
        ],
    ) -> list[
        UniversalRelation
    ]:

        result: list[
            UniversalRelation
        ] = []

        seen: set[
            tuple[
                str,
                str | None,
                str | None,
            ]
        ] = set()

        for relation in relations:

            key = (
                relation.type,
                relation.source,
                relation.target,
            )

            if key in seen:

                # Keep the stronger relation if a duplicate
                # appears with higher certainty.
                for existing in result:

                    if (
                        existing.type
                        == relation.type
                        and existing.source
                        == relation.source
                        and existing.target
                        == relation.target
                    ):

                        if (
                            relation.certainty
                            > existing.certainty
                        ):

                            existing.certainty = (
                                relation.certainty
                            )

                            existing.evidence = list(
                                dict.fromkeys(
                                    existing.evidence
                                    + relation.evidence
                                )
                            )

                        break

                continue

            seen.add(
                key
            )

            result.append(
                relation
            )

        return result

    # ------------------------------------------------------------------
    # SERIALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def _unit_to_dict(
        unit: UniversalMeaningUnit,
    ) -> dict[str, Any]:

        return asdict(
            unit
        )


# ============================================================================
# DEBUG OUTPUT
# ============================================================================


def _print_result(
    result: dict[str, Any],
) -> None:

    print("\n" + "=" * 72)
    print(
        "SIGNMUSIC UNIVERSAL MEANING"
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
        f"Language confidence: "
        f"{result['source_language_confidence']:.4f}"
    )

    print(
        "\nUniversal meaning units:"
    )

    for unit in result[
        "units"
    ]:

        print(
            f"\n  [{unit['unit_id']}] "
            f"{unit['source_text']}"
        )

        print(
            f"      Confidence: "
            f"{unit['confidence']}"
        )

        print(
            "      Participants:"
        )

        for participant in unit[
            "participants"
        ]:

            print(
                f"        - "
                f"{participant['role']}: "
                f"{participant['reference']}"
            )

        event = unit[
            "event"
        ]

        if event is not None:

            print(
                "      Event:"
            )

            print(
                f"        predicate: "
                f"{event['predicate']}"
            )

            print(
                f"        action: "
                f"{event['action']}"
            )

            print(
                f"        target: "
                f"{event['target']}"
            )

            print(
                f"        modality: "
                f"{event['modality']}"
            )

            print(
                f"        negated: "
                f"{event['negated']}"
            )

            print(
                f"        result: "
                f"{event['result']}"
            )

        print(
            "      Relations:"
        )

        for relation in unit[
            "relations"
        ]:

            print(
                f"        - "
                f"{relation['type']} "
                f"(confidence="
                f"{relation['certainty']})"
            )

        print(
            "      Emotions:"
        )

        for emotion in unit[
            "emotions"
        ]:

            print(
                f"        - "
                f"{emotion['category']} "
                f"polarity="
                f"{emotion['polarity']}"
            )

        figurative = unit[
            "figurative"
        ]

        if figurative[
            "present"
        ]:

            print(
                "      Figurative:"
            )

            print(
                f"        type: "
                f"{figurative['type']}"
            )

            print(
                f"        concept: "
                f"{figurative['concept']}"
            )

            print(
                f"        interpretation: "
                f"{figurative['interpretation']}"
            )

            print(
                f"        confidence: "
                f"{figurative['certainty']}"
            )

        if unit[
            "uncertainty"
        ]:

            print(
                "      Uncertainty:"
            )

            for item in unit[
                "uncertainty"
            ]:

                print(
                    f"        - {item}"
                )

    print(
        "\nSong meaning:"
    )

    song_meaning = result[
        "song_meaning"
    ]

    print(
        "  Dominant relations:"
    )

    for item in song_meaning[
        "dominant_relations"
    ]:

        print(
            f"    - "
            f"{item['type']}: "
            f"{item['count']}"
        )

    print(
        "  Dominant emotions:"
    )

    for item in song_meaning[
        "dominant_emotional_patterns"
    ]:

        print(
            f"    - "
            f"{item['type']}: "
            f"{item['count']}"
        )

    print(
        f"  Figurative units: "
        f"{song_meaning['figurative_unit_count']}"
    )

    print(
        "\nGuarantees:"
    )

    for key, value in result[
        "guarantees"
    ].items():

        print(
            f"  {key}: {value}"
        )


# ============================================================================
# TEST
# ============================================================================


def main() -> None:

    engine = (
        UniversalMeaningEngine()
    )

    lyrics = """I cannot find you
I still need you
I feel alive again
I am alone and broken
Me muero por ti
I can't live without you
You are the light of my life"""

    result = engine.analyze(
        lyrics
    )

    _print_result(
        result
    )


if __name__ == "__main__":
    main()