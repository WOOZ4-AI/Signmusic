from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any

from ..language.narrative_context import NarrativeContextEngine
from ..language.universal_meaning import UniversalMeaningEngine


# ============================================================================
# DGS SEMANTIC MAPPING
# ============================================================================
#
# This module does NOT claim to produce grammatically complete DGS.
#
# It converts language-independent meaning into an intermediate DGS-oriented
# structure that can later be realized using:
#
#     lexical sign selection
#     DGS grammatical ordering
#     non-manual markers
#     spatial reference
#     classifier constructions
#     agreement
#     aspect
#     final sign sequence
#
# DGS has no generally used written form; corpus annotation commonly uses
# glosses as labels for signs. Therefore glosses here are identifiers for the
# pipeline, NOT a substitute for actual DGS. [External documentation]
# ============================================================================


# ============================================================================
# CONCEPT → DGS-ORIENTED REPRESENTATION
# ============================================================================

RELATION_TO_DGS_PLAN = {
    "need_toward_person": {
        "gloss": "NEED",
        "semantic_role": "need_toward_person",
    },
    "expressed_need_toward_person": {
        "gloss": "NEED",
        "semantic_role": "need_toward_person",
    },
    "unsuccessful_search": {
        "gloss": "FIND",
        "semantic_role": "unsuccessful_search",
    },
    "possible_absence_or_separation": {
        "gloss": "ABSENT",
        "semantic_role": "absence",
    },
    "intense_affection": {
        "gloss": "LOVE",
        "semantic_role": "intense_affection",
    },
    "affection_toward_person": {
        "gloss": "LOVE",
        "semantic_role": "affection_toward_person",
    },
    "emotional_dependency": {
        "gloss": "DEPEND",
        "semantic_role": "emotional_dependency",
    },
    "deep_positive_importance": {
        "gloss": "IMPORTANT",
        "semantic_role": "positive_importance",
    },
}


EMOTION_TO_DGS_PLAN = {
    "positive": {
        "gloss": "POSITIVE",
        "semantic_role": "positive_state",
    },
    "negative": {
        "gloss": "NEGATIVE",
        "semantic_role": "negative_state",
    },
    "mixed": {
        "gloss": "MIXED",
        "semantic_role": "mixed_state",
    },
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================


@dataclass
class DGSParticipant:
    id: str
    role: str
    reference: str
    locus: str | None
    confidence: float


@dataclass
class DGSMeaningElement:
    element_id: str
    element_type: str
    gloss_candidate: str | None
    semantic_role: str
    source_concept: str | None
    source_unit: int
    confidence: float
    notes: list[str] = field(
        default_factory=list
    )


@dataclass
class DGSGrammarPlan:
    # This is deliberately an intermediate plan.
    topic: str | None
    subject: str | None
    predicate: str | None
    object: str | None
    negation: bool
    modality: str | None
    temporal: str | None
    aspect: str | None
    intensity: str | None

    # Ordered conceptual elements.
    ordered_elements: list[str]

    # Non-manual information is represented separately.
    non_manual: list[str]


@dataclass
class DGSMeaningUnit:
    unit_id: int
    source_unit: int
    source_text: str

    participants: list[DGSParticipant]
    elements: list[DGSMeaningElement]
    grammar: DGSGrammarPlan

    figurative: bool
    figurative_concept: str | None

    confidence: float
    uncertainty: list[str]


# ============================================================================
# MAPPER
# ============================================================================


class DGSSemanticMapper:
    """
    Converts Universal Meaning into a DGS-oriented semantic plan.

    This is NOT yet a DGS translator.

    Pipeline:

        Universal Meaning
                ↓
        DGS Semantic Mapper
                ↓
        DGS Grammar Planner
                ↓
        Sign Lexicon
                ↓
        DGS Sign Sequence
                ↓
        Motion
                ↓
        Avatar

    Key rule:

        We do NOT map English words directly to DGS signs.

        We map universal semantic relations to a target-language
        intermediate representation.
    """

    TARGET_LANGUAGE = "DGS"
    TARGET_LANGUAGE_NAME = "Deutsche Gebärdensprache"

    def __init__(
        self,
        universal_engine: UniversalMeaningEngine | None = None,
        narrative_engine: NarrativeContextEngine | None = None,
    ) -> None:

        self.universal_engine = (
            universal_engine
            or UniversalMeaningEngine()
        )

        self.narrative_engine = (
            narrative_engine
            or NarrativeContextEngine(
                self.universal_engine
            )
        )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze(
        self,
        source: str | dict[str, Any],
    ) -> dict[str, Any]:
        """
        Accept:

            raw lyrics
            UniversalMeaning output
            NarrativeContext output
        """

        if isinstance(
            source,
            str,
        ):

            narrative = (
                self.narrative_engine.analyze(
                    source
                )
            )

        elif isinstance(
            source,
            dict,
        ):

            if "narrative" in source:

                narrative = source

            elif "units" in source:

                narrative = (
                    self.narrative_engine.analyze(
                        source
                    )
                )

            else:

                raise ValueError(
                    "Dictionary input must contain "
                    "'units' or 'narrative'."
                )

        else:

            raise TypeError(
                "source must be a string or dictionary"
            )

        universal_units = (
            narrative.get(
                "units",
                [],
            )
        )

        dgs_units: list[
            DGSMeaningUnit
        ] = []

        for unit in universal_units:

            mapped = (
                self._map_unit(
                    unit
                )
            )

            dgs_units.append(
                mapped
            )

        song_plan = (
            self._build_song_plan(
                narrative,
                dgs_units,
            )
        )

        return {
            "status": (
                "ok"
                if dgs_units
                else "no_dgs_mapping"
            ),
            "source_language": narrative.get(
                "source_language"
            ),
            "source_language_name": narrative.get(
                "source_language_name"
            ),
            "target_language": (
                self.TARGET_LANGUAGE
            ),
            "target_language_name": (
                self.TARGET_LANGUAGE_NAME
            ),
            "units": [
                asdict(unit)
                for unit in dgs_units
            ],
            "song_plan": song_plan,
            "mapping_policy": {
                "direct_word_to_sign": False,
                "universal_meaning_used": True,
                "grammar_translation_complete": False,
                "dgs_lexicon_selection_complete": False,
                "motion_generation_complete": False,
            },
            "metadata": {
                "unit_count": len(
                    dgs_units
                ),
                "mapped_element_count": sum(
                    len(unit.elements)
                    for unit
                    in dgs_units
                ),
            },
        }

    # ------------------------------------------------------------------
    # UNIT MAPPING
    # ------------------------------------------------------------------

    def _map_unit(
        self,
        unit: dict[str, Any],
    ) -> DGSMeaningUnit:

        source_unit = int(
            unit.get(
                "unit_id",
                unit.get(
                    "segment_index",
                    -1,
                ),
            )
        )

        source_text = str(
            unit.get(
                "source_text",
                "",
            )
        )

        participants = (
            self._map_participants(
                unit
            )
        )

        relations = unit.get(
            "relations",
            [],
        )

        elements: list[
            DGSMeaningElement
        ] = []

        # --------------------------------------------------------------
        # RELATION ELEMENTS
        # --------------------------------------------------------------

        for index, relation in enumerate(
            relations
        ):

            relation_type = str(
                relation.get(
                    "type",
                    "",
                )
            )

            mapped_plan = (
                RELATION_TO_DGS_PLAN.get(
                    relation_type
                )
            )

            if not mapped_plan:
                continue

            elements.append(
                DGSMeaningElement(
                    element_id=(
                        f"U{source_unit}_R{index}"
                    ),
                    element_type="relation",
                    gloss_candidate=(
                        mapped_plan["gloss"]
                    ),
                    semantic_role=(
                        mapped_plan[
                            "semantic_role"
                        ]
                    ),
                    source_concept=(
                        relation_type
                    ),
                    source_unit=source_unit,
                    confidence=float(
                        relation.get(
                            "certainty",
                            0.0,
                        )
                    ),
                    notes=[
                        "Intermediate DGS "
                        "lexical candidate.",
                        "Requires target-language "
                        "lexicon validation.",
                    ],
                )
            )

        # --------------------------------------------------------------
        # EVENT
        # --------------------------------------------------------------

        event = unit.get(
            "event"
        )

        if event:

            action = event.get(
                "action"
            )

            predicate = event.get(
                "predicate"
            )

            target = event.get(
                "target"
            )

            if action:

                elements.append(
                    DGSMeaningElement(
                        element_id=(
                            f"U{source_unit}_EVENT"
                        ),
                        element_type="predicate",
                        gloss_candidate=(
                            self._action_to_gloss(
                                action
                            )
                        ),
                        semantic_role="predicate",
                        source_concept=(
                            predicate
                            or action
                        ),
                        source_unit=source_unit,
                        confidence=0.70,
                        notes=[
                            "Predicate candidate "
                            "requires DGS grammatical "
                            "realization."
                        ],
                    )
                )

            if target:

                elements.append(
                    DGSMeaningElement(
                        element_id=(
                            f"U{source_unit}_TARGET"
                        ),
                        element_type="participant",
                        gloss_candidate=None,
                        semantic_role="target",
                        source_concept=target,
                        source_unit=source_unit,
                        confidence=0.90,
                        notes=[
                            "Target participant "
                            "must be realized using "
                            "appropriate DGS spatial "
                            "reference or lexical form."
                        ],
                    )
                )

        # --------------------------------------------------------------
        # EMOTIONS
        # --------------------------------------------------------------

        for index, emotion in enumerate(
            unit.get(
                "emotions",
                [],
            )
        ):

            polarity = emotion.get(
                "polarity"
            )

            emotion_plan = (
                EMOTION_TO_DGS_PLAN.get(
                    polarity
                )
            )

            if not emotion_plan:
                continue

            elements.append(
                DGSMeaningElement(
                    element_id=(
                        f"U{source_unit}_E{index}"
                    ),
                    element_type="emotion",
                    gloss_candidate=(
                        emotion_plan["gloss"]
                    ),
                    semantic_role=(
                        emotion_plan[
                            "semantic_role"
                        ]
                    ),
                    source_concept=(
                        emotion.get(
                            "category"
                        )
                    ),
                    source_unit=source_unit,
                    confidence=float(
                        emotion.get(
                            "certainty",
                            0.0,
                        )
                    ),
                    notes=[
                        "Generic emotional "
                        "candidate; exact DGS "
                        "realization is context-dependent."
                    ],
                )
            )

        # --------------------------------------------------------------
        # FIGURATIVE MEANING
        # --------------------------------------------------------------

        figurative = unit.get(
            "figurative",
            {},
        )

        figurative_present = bool(
            figurative.get(
                "present",
                False,
            )
        )

        figurative_concept = (
            figurative.get(
                "concept"
            )
        )

        # --------------------------------------------------------------
        # GRAMMAR PLAN
        # --------------------------------------------------------------

        grammar = (
            self._build_grammar_plan(
                unit,
                elements,
            )
        )

        # --------------------------------------------------------------
        # UNCERTAINTY
        # --------------------------------------------------------------

        uncertainty = list(
            unit.get(
                "uncertainty",
                [],
            )
        )

        if figurative_present:

            uncertainty.append(
                "Figurative meaning requires "
                "target-language realization."
            )

        if not elements:

            uncertainty.append(
                "No direct semantic-to-DGS "
                "lexical candidate was identified."
            )

        uncertainty = list(
            dict.fromkeys(
                uncertainty
            )
        )

        confidence = (
            self._calculate_unit_confidence(
                unit,
                elements,
            )
        )

        return DGSMeaningUnit(
            unit_id=source_unit,
            source_unit=source_unit,
            source_text=source_text,
            participants=participants,
            elements=elements,
            grammar=grammar,
            figurative=figurative_present,
            figurative_concept=(
                figurative_concept
            ),
            confidence=confidence,
            uncertainty=uncertainty,
        )

    # ------------------------------------------------------------------
    # PARTICIPANTS
    # ------------------------------------------------------------------

    @staticmethod
    def _map_participants(
        unit: dict[str, Any],
    ) -> list[DGSParticipant]:

        result: list[
            DGSParticipant
        ] = []

        for participant in unit.get(
            "participants",
            [],
        ):

            role = str(
                participant.get(
                    "role",
                    "",
                )
            )

            reference = str(
                participant.get(
                    "reference",
                    "",
                )
            )

            participant_id = str(
                participant.get(
                    "id",
                    "",
                )
            )

            # Initial spatial-locus strategy.
            #
            # P1/P2 are stable discourse participants.
            if reference == "first_person":

                locus = "SIGNER"

            elif reference == "second_person":

                locus = "ADDRESSEE"

            else:

                locus = None

            result.append(
                DGSParticipant(
                    id=(
                        participant_id
                        or f"P{len(result) + 1}"
                    ),
                    role=role,
                    reference=reference,
                    locus=locus,
                    confidence=float(
                        participant.get(
                            "certainty",
                            0.0,
                        )
                    ),
                )
            )

        return result

    # ------------------------------------------------------------------
    # GRAMMAR PLAN
    # ------------------------------------------------------------------

    def _build_grammar_plan(
        self,
        unit: dict[str, Any],
        elements: list[
            DGSMeaningElement
        ],
    ) -> DGSGrammarPlan:

        event = unit.get(
            "event",
            {},
        )

        agent = event.get(
            "agent"
        )

        target = event.get(
            "target"
        )

        predicate = event.get(
            "predicate"
        )

        state = event.get(
            "state"
        )

        modality = event.get(
            "modality"
        )

        negated = bool(
            event.get(
                "negated",
                False,
            )
        )

        temporal = unit.get(
            "temporal",
            {},
        )

        temporal_value = (
            temporal.get(
                "temporal"
            )
        )

        persistence = (
            temporal.get(
                "persistence"
            )
        )

        duration = (
            temporal.get(
                "duration"
            )
        )

        # --------------------------------------------------------------
        # TOPIC / SUBJECT
        # --------------------------------------------------------------

        topic = None
        subject = agent
        object_value = target

        # --------------------------------------------------------------
        # PREDICATE
        # --------------------------------------------------------------

        predicate_value = (
            predicate
            or state
        )

        # --------------------------------------------------------------
        # ORDER
        # --------------------------------------------------------------
        #
        # This is NOT claimed to be final DGS syntax.
        # It is an intermediate ordering plan.
        # The later DGS grammar engine must validate it.
        #

        ordered_elements: list[str] = []

        if temporal_value:

            ordered_elements.append(
                "TEMPORAL"
            )

        if topic:

            ordered_elements.append(
                "TOPIC"
            )

        if subject:

            ordered_elements.append(
                "SUBJECT"
            )

        if predicate_value:

            ordered_elements.append(
                "PREDICATE"
            )

        if object_value:

            ordered_elements.append(
                "OBJECT"
            )

        if negated:

            ordered_elements.append(
                "NEGATION"
            )

        if modality:

            ordered_elements.append(
                "MODALITY"
            )

        if persistence:

            ordered_elements.append(
                "PERSISTENCE"
            )

        if duration:

            ordered_elements.append(
                "DURATION"
            )

        # --------------------------------------------------------------
        # NON-MANUAL MARKERS
        # --------------------------------------------------------------

        non_manual: list[str] = []

        if negated:
            non_manual.append(
                "negative_polarity"
            )

        if modality == "inability":
            non_manual.append(
                "inability"
            )

        if persistence:
            non_manual.append(
                "continuative"
            )

        return DGSGrammarPlan(
            topic=topic,
            subject=subject,
            predicate=predicate_value,
            object=object_value,
            negation=negated,
            modality=modality,
            temporal=temporal_value,
            aspect=None,
            intensity=None,
            ordered_elements=ordered_elements,
            non_manual=non_manual,
        )

    # ------------------------------------------------------------------
    # ACTION → GLOSS CANDIDATE
    # ------------------------------------------------------------------

    @staticmethod
    def _action_to_gloss(
        action: str,
    ) -> str | None:

        mapping = {
            "need": "NEED",
            "search_or_find": "FIND",
            "live": "LIVE",
            "feel": "FEEL",
            "express_affection": "LOVE",
        }

        return mapping.get(
            action
        )

    # ------------------------------------------------------------------
    # CONFIDENCE
    # ------------------------------------------------------------------

    @staticmethod
    def _calculate_unit_confidence(
        unit: dict[str, Any],
        elements: list[
            DGSMeaningElement
        ],
    ) -> float:

        universal_confidence = float(
            unit.get(
                "confidence",
                0.0,
            )
        )

        if not elements:

            return round(
                universal_confidence
                * 0.50,
                4,
            )

        element_confidence = (
            sum(
                element.confidence
                for element
                in elements
            )
            / len(elements)
        )

        score = (
            universal_confidence
            * 0.45
            + element_confidence
            * 0.55
        )

        return round(
            min(
                score,
                1.0,
            ),
            4,
        )

    # ------------------------------------------------------------------
    # SONG PLAN
    # ------------------------------------------------------------------

    @staticmethod
    def _build_song_plan(
        narrative: dict[str, Any],
        units: list[DGSMeaningUnit],
    ) -> dict[str, Any]:

        narrative_data = narrative.get(
            "narrative",
            {},
        )

        themes = narrative_data.get(
            "theme_candidates",
            [],
        )

        emotional_arc = narrative_data.get(
            "emotional_arc",
            [],
        )

        return {
            "theme_candidates": themes,
            "emotional_arc": emotional_arc,
            "unit_order": [
                unit.unit_id
                for unit in units
            ],
            "target_language": "DGS",
            "requires_grammar_realization": True,
            "requires_lexicon_lookup": True,
            "requires_non_manual_realization": True,
        }


# ============================================================================
# DEBUG OUTPUT
# ============================================================================


def _print_result(
    result: dict[str, Any],
) -> None:

    print("\n" + "=" * 72)
    print(
        "SIGNMUSIC DGS SEMANTIC MAPPER"
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
        "\nDGS meaning units:"
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
                f"{participant['reference']} "
                f"locus="
                f"{participant['locus']}"
            )

        print(
            "      Elements:"
        )

        for element in unit[
            "elements"
        ]:

            print(
                f"        - "
                f"{element['element_type']} "
                f"→ "
                f"{element['gloss_candidate']} "
                f"role="
                f"{element['semantic_role']} "
                f"confidence="
                f"{element['confidence']}"
            )

        grammar = unit[
            "grammar"
        ]

        print(
            "      Grammar plan:"
        )

        print(
            f"        subject: "
            f"{grammar['subject']}"
        )

        print(
            f"        predicate: "
            f"{grammar['predicate']}"
        )

        print(
            f"        object: "
            f"{grammar['object']}"
        )

        print(
            f"        negation: "
            f"{grammar['negation']}"
        )

        print(
            f"        modality: "
            f"{grammar['modality']}"
        )

        print(
            f"        temporal: "
            f"{grammar['temporal']}"
        )

        print(
            f"        ordered_elements: "
            f"{grammar['ordered_elements']}"
        )

        print(
            f"        non_manual: "
            f"{grammar['non_manual']}"
        )

        if unit[
            "figurative"
        ]:

            print(
                "      Figurative:"
            )

            print(
                f"        concept: "
                f"{unit['figurative_concept']}"
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
        "\nSong plan:"
    )

    print(
        f"  Themes: "
        f"{result['song_plan']['theme_candidates']}"
    )

    print(
        f"  Emotional arc: "
        f"{result['song_plan']['emotional_arc']}"
    )

    print(
        "\nMapping policy:"
    )

    for key, value in result[
        "mapping_policy"
    ].items():

        print(
            f"  {key}: {value}"
        )


# ============================================================================
# TEST
# ============================================================================


def main() -> None:

    mapper = DGSSemanticMapper()

    lyrics = """I cannot find you
I still need you
I feel alive again
I am alone and broken"""

    result = mapper.analyze(
        lyrics
    )

    _print_result(
        result
    )


if __name__ == "__main__":
    main()