from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

from .context_engine import ContextEngine


# ============================================================================
# LEXICONS
# ============================================================================

FIRST_PERSON = {
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
    "je",
    "moi",
    "nous",
    "notre",
}

SECOND_PERSON = {
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

NEED_VERBS = {
    "need",
    "needs",
    "needed",
    "necesito",
    "necesitas",
    "necesitar",
    "nécessite",
    "nécessiter",
}

SEARCH_VERBS = {
    "find",
    "finds",
    "found",
    "search",
    "searching",
    "look",
    "looking",
    "seek",
    "seeking",
    "buscar",
    "busco",
    "buscando",
    "encuentro",
    "encontrar",
    "trouve",
    "chercher",
}

LIVE_VERBS = {
    "live",
    "lives",
    "living",
    "vivir",
    "vivo",
    "vive",
    "vivant",
    "vivre",
}

FEEL_VERBS = {
    "feel",
    "feels",
    "feeling",
    "felt",
    "sentir",
    "siento",
    "siente",
    "sentimos",
    "ressentir",
}

AFFECTION_TERMS = {
    "love",
    "loving",
    "loved",
    "adore",
    "adoring",
    "kiss",
    "kisses",
    "kissed",
    "heart",
    "romance",
    "amour",
    "aime",
    "aimer",
    "amor",
    "amar",
    "beso",
    "besos",
    "querer",
}

ABSENCE_TERMS = {
    "gone",
    "away",
    "left",
    "leave",
    "leaving",
    "lost",
    "missing",
    "miss",
    "apart",
    "distance",
    "irse",
    "perdido",
    "perdida",
    "extraño",
    "extrañar",
    "sin",
    "partir",
    "parti",
}

POSITIVE_STATE_TERMS = {
    "alive",
    "happy",
    "joy",
    "joyful",
    "free",
    "safe",
    "healed",
    "bright",
    "hope",
    "hopeful",
    "vida",
    "feliz",
    "alegría",
    "libre",
    "seguro",
    "luz",
    "esperanza",
}

NEGATIVE_STATE_TERMS = {
    "sad",
    "alone",
    "lonely",
    "broken",
    "hurt",
    "pain",
    "cry",
    "crying",
    "tears",
    "dead",
    "death",
    "lost",
    "empty",
    "dark",
    "triste",
    "solo",
    "sola",
    "roto",
    "rota",
    "dolor",
    "llorar",
    "lágrimas",
    "muerte",
    "vacío",
    "vacía",
    "oscuro",
    "oscura",
}

NEGATION_TERMS = {
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
    "ne",
    "pas",
    "jamais",
    "rien",
    "nunca",
    "jamás",
    "nada",
    "nadie",
}

MODAL_INABILITY = {
    "can't",
    "cannot",
    "couldn't",
    "unable",
    "incapable",
    "no puedo",
    "imposible",
    "ne peux",
}

PERSISTENCE_TERMS = {
    "still",
    "aún",
    "aun",
    "todavía",
    "toujours",
}

DURATION_TERMS = {
    "forever",
    "always",
    "ever",
    "para siempre",
    "siempre",
    "pour toujours",
    "toujours",
}


# ============================================================================
# KNOWN FIGURATIVE PHRASES
# ============================================================================

IDIOMATIC_PHRASES = {
    "me muero por ti": {
        "concept": "intense_affection",
        "category": "figurative_language",
        "interpretation": (
            "intense romantic or emotional affection"
        ),
        "figurative": True,
        "confidence": 0.82,
    },
    "i can't live without you": {
        "concept": "emotional_dependency",
        "category": "figurative_language",
        "interpretation": (
            "strong emotional dependency or perceived "
            "inability to be without another person"
        ),
        "figurative": True,
        "confidence": 0.82,
    },
    "i cannot live without you": {
        "concept": "emotional_dependency",
        "category": "figurative_language",
        "interpretation": (
            "strong emotional dependency or perceived "
            "inability to be without another person"
        ),
        "figurative": True,
        "confidence": 0.82,
    },
    "tu me manques": {
        "concept": "missing_someone",
        "category": "idiomatic_language",
        "interpretation": (
            "expression of missing another person"
        ),
        "figurative": False,
        "confidence": 0.82,
    },
    "je meurs pour toi": {
        "concept": "intense_affection",
        "category": "figurative_language",
        "interpretation": (
            "intense romantic or emotional affection"
        ),
        "figurative": True,
        "confidence": 0.82,
    },
    "you are the light of my life": {
        "concept": (
            "deep_affection_and_positive_importance"
        ),
        "category": "figurative_language",
        "interpretation": (
            "another person is portrayed as extremely "
            "important or emotionally illuminating"
        ),
        "figurative": True,
        "confidence": 0.82,
    },
}


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SemanticEvidence:
    type: str
    description: str
    source_terms: list[str]
    strength: float


@dataclass
class SemanticStructure:
    segment_index: int
    text: str

    agent: str | None
    action: str | None
    predicate: str | None
    target: str | None
    state: str | None

    modality: str | None
    negated: bool

    temporal: str | None
    persistence: str | None
    duration: str | None

    result: str | None
    possessor: str | None

    relations: list[str]

    semantic_roles: dict[str, str | None]


@dataclass
class SemanticCandidate:
    concept: str
    category: str
    interpretation: str
    figurative: bool | None
    confidence: float
    uncertainty: str
    segment_index: int
    structure: SemanticStructure | None
    evidence: list[SemanticEvidence]


# ============================================================================
# ENGINE
# ============================================================================

class SemanticEngine:
    """
    Semantic interpretation layer of Signmusic.

    The engine first builds a semantic representation and only then
    proposes interpretations.

    It explicitly separates:
        - lexical evidence
        - semantic roles
        - events
        - states
        - figurative language
        - uncertainty
    """

    def __init__(
        self,
        context_engine: ContextEngine | None = None,
    ) -> None:

        self.context_engine = (
            context_engine
            or ContextEngine()
        )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze(
        self,
        lyrics_or_context: str | dict[str, Any],
    ) -> dict[str, Any]:

        if isinstance(
            lyrics_or_context,
            str,
        ):

            context_analysis = (
                self.context_engine.analyze(
                    lyrics_or_context
                )
            )

        elif isinstance(
            lyrics_or_context,
            dict,
        ):

            context_analysis = (
                lyrics_or_context
            )

        else:

            raise TypeError(
                "lyrics_or_context must be "
                "a string or dictionary"
            )

        context_units = (
            context_analysis.get(
                "context_units",
                [],
            )
        )

        structures: list[
            SemanticStructure
        ] = []

        candidates: list[
            SemanticCandidate
        ] = []

        for unit in context_units:

            structure = (
                self._build_semantic_structure(
                    unit
                )
            )

            structures.append(
                structure
            )

            # A known figurative phrase gets priority over generic
            # lexical state detection.
            idiomatic = (
                self._detect_idioms(
                    unit
                )
            )

            if idiomatic:

                candidates.extend(
                    idiomatic
                )

                # We still create the semantic structure above,
                # but do not generate competing generic candidates
                # for a known figurative phrase.
                continue

            candidates.extend(
                self._interpret_structure(
                    unit,
                    structure,
                )
            )

        candidates = (
            self._deduplicate_candidates(
                candidates
            )
        )

        song_level = (
            self._build_song_level_candidates(
                candidates,
                structures,
                context_analysis,
            )
        )

        all_candidates = (
            candidates
            + song_level
        )

        return {
            "status": self._determine_status(
                context_analysis
            ),
            "language": context_analysis.get(
                "language"
            ),
            "language_name": context_analysis.get(
                "language_name"
            ),
            "language_confidence": context_analysis.get(
                "language_confidence",
                0.0,
            ),
            "semantic_structures": [
                asdict(structure)
                for structure
                in structures
            ],
            "candidates": [
                self._candidate_to_dict(
                    candidate
                )
                for candidate
                in all_candidates
            ],
            "song_level_interpretations": [
                self._candidate_to_dict(
                    candidate
                )
                for candidate
                in song_level
            ],
            "uncertainty_policy": {
                "artist_intent_claimed": False,
                "figurative_meaning_claimed_as_fact": False,
                "semantic_candidate_is_fact": False,
            },
            "metadata": {
                "context_unit_count": len(
                    context_units
                ),
                "semantic_structure_count": len(
                    structures
                ),
                "candidate_count": len(
                    all_candidates
                ),
                "song_level_candidate_count": len(
                    song_level
                ),
            },
        }

    # ------------------------------------------------------------------
    # STATUS
    # ------------------------------------------------------------------

    @staticmethod
    def _determine_status(
        context_analysis: dict[str, Any],
    ) -> str:

        if context_analysis.get(
            "status"
        ) == "empty":

            return "empty"

        if not context_analysis.get(
            "context_units"
        ):

            return "no_semantics"

        return "ok"

    # ------------------------------------------------------------------
    # SEMANTIC STRUCTURE
    # ------------------------------------------------------------------

    def _build_semantic_structure(
        self,
        unit: dict[str, Any],
    ) -> SemanticStructure:

        segment_index = int(
            unit.get(
                "segment_index",
                unit.get(
                    "index",
                    -1,
                ),
            )
        )

        text = str(
            unit.get(
                "text",
                "",
            )
        )

        terms = self._extract_terms(
            unit
        )

        normalized_text = (
            self._normalize_phrase(
                text
            )
        )

        # --------------------------------------------------------------
        # KNOWN METAPHOR
        # --------------------------------------------------------------

        if normalized_text == (
            "you are the light of my life"
        ):

            return SemanticStructure(
                segment_index=segment_index,
                text=text,
                agent="second_person",
                action=None,
                predicate="metaphorically_represents",
                target=None,
                state=None,
                modality=None,
                negated=False,
                temporal=None,
                persistence=None,
                duration=None,
                result="positive_importance",
                possessor="first_person",
                relations=[
                    "metaphor",
                    "positive_importance",
                    "personal_attachment",
                ],
                semantic_roles={
                    "experiencer": "first_person",
                    "subject": "second_person",
                    "predicate": (
                        "metaphorically_represents"
                    ),
                    "possessor": "first_person",
                    "value": "light",
                    "relation": "positive_importance",
                },
            )

        # --------------------------------------------------------------
        # AGENT
        # --------------------------------------------------------------

        agent = None

        first_person = (
            self._matching_terms(
                terms,
                FIRST_PERSON,
            )
        )

        second_person = (
            self._matching_terms(
                terms,
                SECOND_PERSON,
            )
        )

        if first_person:
            agent = "first_person"

        # --------------------------------------------------------------
        # TARGET
        # --------------------------------------------------------------

        target = None

        if second_person:
            target = "second_person"

        # --------------------------------------------------------------
        # ACTION / PREDICATE
        # --------------------------------------------------------------

        action = (
            self._infer_action(
                terms
            )
        )

        predicate = action

        # --------------------------------------------------------------
        # STATE
        # --------------------------------------------------------------

        state = self._infer_state(
            terms
        )

        # --------------------------------------------------------------
        # MODALITY
        # --------------------------------------------------------------

        modality = None

        inability = (
            self._matching_terms(
                terms,
                MODAL_INABILITY,
            )
        )

        if inability:
            modality = "inability"

        # --------------------------------------------------------------
        # NEGATION
        # --------------------------------------------------------------

        negated = bool(
            self._matching_terms(
                terms,
                NEGATION_TERMS,
            )
        )

        # --------------------------------------------------------------
        # TEMPORAL
        # --------------------------------------------------------------

        temporal = self._infer_temporal(
            terms
        )

        # --------------------------------------------------------------
        # PERSISTENCE
        # --------------------------------------------------------------

        persistence = None

        persistence_terms = (
            self._matching_terms(
                terms,
                PERSISTENCE_TERMS,
            )
        )

        if persistence_terms:
            persistence = (
                persistence_terms[0]
            )

        # --------------------------------------------------------------
        # DURATION
        # --------------------------------------------------------------

        duration = None

        duration_terms = (
            self._matching_terms(
                terms,
                DURATION_TERMS,
            )
        )

        if duration_terms:
            duration = (
                duration_terms[0]
            )

        # --------------------------------------------------------------
        # RESULT
        # --------------------------------------------------------------

        result = None

        if action == "search_or_find":

            if modality == "inability":

                result = (
                    "unsuccessful_search"
                )

        elif action == "feel":

            if state:
                result = state

        # --------------------------------------------------------------
        # POSSESSOR
        # --------------------------------------------------------------

        possessor = None

        possessive_terms = {
            "my",
            "mine",
            "our",
            "ours",
            "mi",
            "mis",
            "nuestro",
            "nuestra",
        }

        if self._contains_any(
            terms,
            possessive_terms,
        ):

            possessor = "first_person"

        # --------------------------------------------------------------
        # RELATIONS
        # --------------------------------------------------------------

        relations: list[str] = []

        if agent and action:
            relations.append(
                "agent_performs_action"
            )

        if action and target:
            relations.append(
                "action_targets_person"
            )

        if modality:
            relations.append(
                "modality_relation"
            )

        if negated:
            relations.append(
                "negation_relation"
            )

        if temporal:
            relations.append(
                "temporal_relation"
            )

        if persistence:
            relations.append(
                "persistence_relation"
            )

        if duration:
            relations.append(
                "duration_relation"
            )

        if result:
            relations.append(
                "result_relation"
            )

        if state:
            relations.append(
                "state_relation"
            )

        # --------------------------------------------------------------
        # ROLES
        # --------------------------------------------------------------

        semantic_roles = {
            "agent": agent,
            "action": action,
            "predicate": predicate,
            "target": target,
            "state": state,
            "modality": modality,
            "negation": (
                "true"
                if negated
                else None
            ),
            "temporal": temporal,
            "persistence": persistence,
            "duration": duration,
            "result": result,
            "possessor": possessor,
        }

        return SemanticStructure(
            segment_index=segment_index,
            text=text,
            agent=agent,
            action=action,
            predicate=predicate,
            target=target,
            state=state,
            modality=modality,
            negated=negated,
            temporal=temporal,
            persistence=persistence,
            duration=duration,
            result=result,
            possessor=possessor,
            relations=relations,
            semantic_roles=semantic_roles,
        )

    # ------------------------------------------------------------------
    # ACTION
    # ------------------------------------------------------------------

    @staticmethod
    def _infer_action(
        terms: list[str],
    ) -> str | None:

        if SemanticEngine._contains_any(
            terms,
            NEED_VERBS,
        ):
            return "need"

        if SemanticEngine._contains_any(
            terms,
            SEARCH_VERBS,
        ):
            return "search_or_find"

        if SemanticEngine._contains_any(
            terms,
            LIVE_VERBS,
        ):
            return "live"

        if SemanticEngine._contains_any(
            terms,
            FEEL_VERBS,
        ):
            return "feel"

        if SemanticEngine._contains_any(
            terms,
            AFFECTION_TERMS,
        ):
            return "express_affection"

        return None

    # ------------------------------------------------------------------
    # STATE
    # ------------------------------------------------------------------

    @staticmethod
    def _infer_state(
        terms: list[str],
    ) -> str | None:

        positive = (
            SemanticEngine._matching_terms(
                terms,
                POSITIVE_STATE_TERMS,
            )
        )

        negative = (
            SemanticEngine._matching_terms(
                terms,
                NEGATIVE_STATE_TERMS,
            )
        )

        if positive and negative:
            return "mixed_emotional_state"

        if positive:
            return "positive_emotional_state"

        if negative:
            return "negative_emotional_state"

        return None

    # ------------------------------------------------------------------
    # TEMPORAL
    # ------------------------------------------------------------------

    @staticmethod
    def _infer_temporal(
        terms: list[str],
    ) -> str | None:

        temporal_terms = {
            "now",
            "today",
            "tonight",
            "tomorrow",
            "yesterday",
            "before",
            "after",
            "ahora",
            "hoy",
            "mañana",
            "ayer",
            "antes",
            "después",
        }

        for term in terms:

            if term in temporal_terms:
                return term

        return None

    # ------------------------------------------------------------------
    # STRUCTURE INTERPRETATION
    # ------------------------------------------------------------------

    def _interpret_structure(
        self,
        unit: dict[str, Any],
        structure: SemanticStructure,
    ) -> list[SemanticCandidate]:

        results: list[
            SemanticCandidate
        ] = []

        terms = self._extract_terms(
            unit
        )

        # --------------------------------------------------------------
        # UNSUCCESSFUL SEARCH
        # --------------------------------------------------------------

        if (
            structure.action
            == "search_or_find"
            and structure.target
            == "second_person"
        ):

            evidence = [
                SemanticEvidence(
                    type="action",
                    description=(
                        "A search/find action is directed "
                        "toward another person."
                    ),
                    source_terms=(
                        self._matching_terms(
                            terms,
                            SEARCH_VERBS,
                        )
                        + self._matching_terms(
                            terms,
                            SECOND_PERSON,
                        )
                    ),
                    strength=0.82,
                )
            ]

            if structure.modality == "inability":

                evidence.append(
                    SemanticEvidence(
                        type="inability",
                        description=(
                            "The search/find action is "
                            "associated with inability."
                        ),
                        source_terms=(
                            self._matching_terms(
                                terms,
                                MODAL_INABILITY,
                            )
                        ),
                        strength=0.90,
                    )
                )

            results.append(
                SemanticCandidate(
                    concept=(
                        "unsuccessful_search_for_person"
                    ),
                    category="event",
                    interpretation=(
                        "the speaker describes being "
                        "unable or unsuccessful in "
                        "finding another person"
                    ),
                    figurative=False,
                    confidence=0.80,
                    uncertainty=(
                        "absence or emotional loss may "
                        "be implied but is not assumed "
                        "from this sentence alone"
                    ),
                    segment_index=(
                        structure.segment_index
                    ),
                    structure=structure,
                    evidence=evidence,
                )
            )

        # --------------------------------------------------------------
        # NEED + PERSON
        # --------------------------------------------------------------

        if (
            structure.action == "need"
            and structure.target
            == "second_person"
        ):

            matching_need = (
                self._matching_terms(
                    terms,
                    NEED_VERBS,
                )
            )

            matching_target = (
                self._matching_terms(
                    terms,
                    SECOND_PERSON,
                )
            )

            evidence = [
                SemanticEvidence(
                    type="need_expression",
                    description=(
                        "The speaker explicitly "
                        "expresses a need."
                    ),
                    source_terms=matching_need,
                    strength=0.78,
                ),
                SemanticEvidence(
                    type="target_reference",
                    description=(
                        "The expressed need concerns "
                        "another person."
                    ),
                    source_terms=matching_target,
                    strength=0.62,
                ),
            ]

            if structure.persistence:

                evidence.append(
                    SemanticEvidence(
                        type="persistence",
                        description=(
                            "The need is explicitly "
                            "described as continuing."
                        ),
                        source_terms=[
                            structure.persistence
                        ],
                        strength=0.72,
                    )
                )

            results.append(
                SemanticCandidate(
                    concept=(
                        "expressed_need_toward_person"
                    ),
                    category="relationship",
                    interpretation=(
                        "the speaker explicitly "
                        "expresses a need for another "
                        "person"
                    ),
                    figurative=None,
                    confidence=0.77,
                    uncertainty=(
                        "the reason and emotional nature "
                        "of the need remain context-dependent"
                    ),
                    segment_index=(
                        structure.segment_index
                    ),
                    structure=structure,
                    evidence=evidence,
                )
            )

        # --------------------------------------------------------------
        # FEEL + STATE
        # --------------------------------------------------------------

        if (
            structure.action == "feel"
            and structure.state
        ):

            evidence_terms = (
                self._matching_terms(
                    terms,
                    FEEL_VERBS,
                )
                + self._matching_terms(
                    terms,
                    POSITIVE_STATE_TERMS,
                )
                + self._matching_terms(
                    terms,
                    NEGATIVE_STATE_TERMS,
                )
            )

            results.append(
                SemanticCandidate(
                    concept="felt_emotional_state",
                    category="emotion",
                    interpretation=(
                        "the speaker explicitly describes "
                        "experiencing an emotional or "
                        "experiential state"
                    ),
                    figurative=None,
                    confidence=0.72,
                    uncertainty=(
                        "the broader cause of the state "
                        "requires context"
                    ),
                    segment_index=(
                        structure.segment_index
                    ),
                    structure=structure,
                    evidence=[
                        SemanticEvidence(
                            type="feeling_predicate",
                            description=(
                                "A feeling predicate is "
                                "combined with an identifiable "
                                "state."
                            ),
                            source_terms=evidence_terms,
                            strength=0.78,
                        )
                    ],
                )
            )

        # --------------------------------------------------------------
        # POSITIVE STATE
        # --------------------------------------------------------------

        if (
            structure.state
            == "positive_emotional_state"
        ):

            matching = (
                self._matching_terms(
                    terms,
                    POSITIVE_STATE_TERMS,
                )
            )

            results.append(
                SemanticCandidate(
                    concept="positive_emotional_state",
                    category="emotion",
                    interpretation=(
                        "the lyric describes a positive "
                        "emotional or experiential state"
                    ),
                    figurative=None,
                    confidence=0.66,
                    uncertainty=(
                        "the cause and deeper emotional "
                        "meaning require broader context"
                    ),
                    segment_index=(
                        structure.segment_index
                    ),
                    structure=structure,
                    evidence=[
                        SemanticEvidence(
                            type="state_lexicon",
                            description=(
                                "Positive-state lexical "
                                "evidence."
                            ),
                            source_terms=matching,
                            strength=0.70,
                        )
                    ],
                )
            )

        # --------------------------------------------------------------
        # NEGATIVE STATE
        # --------------------------------------------------------------

        if (
            structure.state
            == "negative_emotional_state"
        ):

            matching = (
                self._matching_terms(
                    terms,
                    NEGATIVE_STATE_TERMS,
                )
            )

            results.append(
                SemanticCandidate(
                    concept="negative_emotional_state",
                    category="emotion",
                    interpretation=(
                        "the lyric describes a negative "
                        "emotional or experiential state"
                    ),
                    figurative=None,
                    confidence=0.66,
                    uncertainty=(
                        "the cause and deeper emotional "
                        "meaning require broader context"
                    ),
                    segment_index=(
                        structure.segment_index
                    ),
                    structure=structure,
                    evidence=[
                        SemanticEvidence(
                            type="state_lexicon",
                            description=(
                                "Negative-state lexical "
                                "evidence."
                            ),
                            source_terms=matching,
                            strength=0.70,
                        )
                    ],
                )
            )

        # --------------------------------------------------------------
        # AFFECTION
        # --------------------------------------------------------------

        if (
            structure.action
            == "express_affection"
            and structure.target
            == "second_person"
        ):

            results.append(
                SemanticCandidate(
                    concept="affection_toward_person",
                    category="relationship",
                    interpretation=(
                        "the speaker expresses affection "
                        "toward another person"
                    ),
                    figurative=None,
                    confidence=0.74,
                    uncertainty=(
                        "the exact type of relationship "
                        "is not established here"
                    ),
                    segment_index=(
                        structure.segment_index
                    ),
                    structure=structure,
                    evidence=[
                        SemanticEvidence(
                            type="affection_expression",
                            description=(
                                "Affection-related language "
                                "targets another person."
                            ),
                            source_terms=(
                                self._matching_terms(
                                    terms,
                                    AFFECTION_TERMS,
                                )
                                + self._matching_terms(
                                    terms,
                                    SECOND_PERSON,
                                )
                            ),
                            strength=0.76,
                        )
                    ],
                )
            )

        # --------------------------------------------------------------
        # ABSENCE
        # --------------------------------------------------------------

        absence = (
            self._matching_terms(
                terms,
                ABSENCE_TERMS,
            )
        )

        if absence:

            results.append(
                SemanticCandidate(
                    concept=(
                        "possible_absence_or_separation"
                    ),
                    category="relationship",
                    interpretation=(
                        "the lyric contains language "
                        "associated with absence, "
                        "separation, distance, or loss"
                    ),
                    figurative=None,
                    confidence=0.60,
                    uncertainty=(
                        "absence or separation is a "
                        "candidate reading rather than "
                        "a confirmed emotional meaning"
                    ),
                    segment_index=(
                        structure.segment_index
                    ),
                    structure=structure,
                    evidence=[
                        SemanticEvidence(
                            type="absence_lexicon",
                            description=(
                                "Absence-related lexical "
                                "evidence."
                            ),
                            source_terms=absence,
                            strength=0.68,
                        )
                    ],
                )
            )

        return results

    # ------------------------------------------------------------------
    # FIGURATIVE PHRASES
    # ------------------------------------------------------------------

    def _detect_idioms(
        self,
        unit: dict[str, Any],
    ) -> list[SemanticCandidate]:

        text = str(
            unit.get(
                "text",
                "",
            )
        )

        normalized = (
            self._normalize_phrase(
                text
            )
        )

        segment_index = int(
            unit.get(
                "segment_index",
                unit.get(
                    "index",
                    -1,
                ),
            )
        )

        results: list[
            SemanticCandidate
        ] = []

        for phrase, info in (
            IDIOMATIC_PHRASES.items()
        ):

            if phrase not in normalized:
                continue

            results.append(
                SemanticCandidate(
                    concept=info[
                        "concept"
                    ],
                    category=info[
                        "category"
                    ],
                    interpretation=info[
                        "interpretation"
                    ],
                    figurative=info[
                        "figurative"
                    ],
                    confidence=info[
                        "confidence"
                    ],
                    uncertainty=(
                        "candidate_interpretation"
                    ),
                    segment_index=segment_index,
                    structure=None,
                    evidence=[
                        SemanticEvidence(
                            type=(
                                "idiomatic_or_figurative_pattern"
                            ),
                            description=(
                                "A known phrase pattern "
                                "was matched directly."
                            ),
                            source_terms=[
                                phrase
                            ],
                            strength=0.92,
                        )
                    ],
                )
            )

        return results

    # ------------------------------------------------------------------
    # SONG LEVEL
    # ------------------------------------------------------------------

    def _build_song_level_candidates(
        self,
        candidates: list[
            SemanticCandidate
        ],
        structures: list[
            SemanticStructure
        ],
        context_analysis: dict[str, Any],
    ) -> list[
        SemanticCandidate
    ]:

        results: list[
            SemanticCandidate
        ] = []

        concept_counts: dict[
            str,
            int,
        ] = {}

        for candidate in candidates:

            concept_counts[
                candidate.concept
            ] = (
                concept_counts.get(
                    candidate.concept,
                    0,
                )
                + 1
            )

        need_count = concept_counts.get(
            "expressed_need_toward_person",
            0,
        )

        if need_count >= 2:

            results.append(
                SemanticCandidate(
                    concept=(
                        "persistent_attachment_candidate"
                    ),
                    category="song_theme",
                    interpretation=(
                        "repeated expressions of need "
                        "toward another person suggest "
                        "a persistent attachment"
                    ),
                    figurative=None,
                    confidence=0.76,
                    uncertainty=(
                        "song-level candidate based on "
                        "repetition; it does not establish "
                        "romantic intent"
                    ),
                    segment_index=-1,
                    structure=None,
                    evidence=[
                        SemanticEvidence(
                            type="repeated_need",
                            description=(
                                "Need toward another "
                                "person occurs repeatedly "
                                "across the analyzed text."
                            ),
                            source_terms=[
                                "expressed_need_toward_person"
                            ],
                            strength=0.78,
                        )
                    ],
                )
            )

        has_need = any(
            candidate.concept
            == "expressed_need_toward_person"
            for candidate
            in candidates
        )

        has_absence = any(
            candidate.concept
            == "possible_absence_or_separation"
            for candidate
            in candidates
        )

        if (
            has_need
            and has_absence
        ):

            results.append(
                SemanticCandidate(
                    concept=(
                        "attachment_with_absence"
                    ),
                    category="song_theme",
                    interpretation=(
                        "the analyzed lyrics combine "
                        "need toward another person "
                        "with absence or separation "
                        "related language"
                    ),
                    figurative=None,
                    confidence=0.73,
                    uncertainty=(
                        "this is a thematic candidate; "
                        "the emotional cause and artist "
                        "intent remain uncertain"
                    ),
                    segment_index=-1,
                    structure=None,
                    evidence=[
                        SemanticEvidence(
                            type="combined_theme",
                            description=(
                                "Both need and absence "
                                "patterns are present "
                                "in the analyzed text."
                            ),
                            source_terms=[
                                "expressed_need_toward_person",
                                "possible_absence_or_separation",
                            ],
                            strength=0.74,
                        )
                    ],
                )
            )

        positive_count = concept_counts.get(
            "positive_emotional_state",
            0,
        )

        negative_count = concept_counts.get(
            "negative_emotional_state",
            0,
        )

        if (
            positive_count > 0
            and negative_count > 0
        ):

            results.append(
                SemanticCandidate(
                    concept="emotional_state_contrast",
                    category="song_theme",
                    interpretation=(
                        "the lyrics contain both positive "
                        "and negative emotional states"
                    ),
                    figurative=None,
                    confidence=0.70,
                    uncertainty=(
                        "the precise chronology or "
                        "causal relationship between "
                        "states is not established"
                    ),
                    segment_index=-1,
                    structure=None,
                    evidence=[
                        SemanticEvidence(
                            type="state_contrast",
                            description=(
                                "Positive and negative "
                                "state candidates both "
                                "occur in the song."
                            ),
                            source_terms=[
                                "positive_emotional_state",
                                "negative_emotional_state",
                            ],
                            strength=0.68,
                        )
                    ],
                )
            )

        return results

    # ------------------------------------------------------------------
    # TOKEN HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_terms(
        unit: dict[str, Any],
    ) -> list[str]:

        terms: list[str] = []

        for token in unit.get(
            "tokens",
            [],
        ):

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

    @staticmethod
    def _normalize_phrase(
        text: str,
    ) -> str:

        text = text.lower().strip()

        # Remove punctuation only for phrase matching.
        # The original lyric text remains untouched elsewhere.
        text = re.sub(
            r"[^\w\s'’-]",
            " ",
            text,
            flags=re.UNICODE,
        )

        text = re.sub(
            r"\s+",
            " ",
            text,
        )

        return text.strip()

    # ------------------------------------------------------------------
    # LEXICON HELPERS
    # ------------------------------------------------------------------

    @staticmethod
    def _contains_any(
        terms: list[str],
        candidates: set[str],
    ) -> bool:

        candidate_lower = {
            item.lower()
            for item in candidates
        }

        return any(
            term.lower()
            in candidate_lower
            for term in terms
        )

    @staticmethod
    def _matching_terms(
        terms: list[str],
        candidates: set[str],
    ) -> list[str]:

        candidate_lower = {
            item.lower()
            for item in candidates
        }

        result: list[str] = []

        for term in terms:

            normalized = term.lower()

            if normalized in candidate_lower:

                if normalized not in result:
                    result.append(
                        normalized
                    )

        return result

    # ------------------------------------------------------------------
    # DEDUPLICATION
    # ------------------------------------------------------------------

    @staticmethod
    def _deduplicate_candidates(
        candidates: list[
            SemanticCandidate
        ],
    ) -> list[
        SemanticCandidate
    ]:

        unique: list[
            SemanticCandidate
        ] = []

        seen: set[
            tuple[str, int]
        ] = set()

        for candidate in candidates:

            key = (
                candidate.concept,
                candidate.segment_index,
            )

            if key in seen:
                continue

            seen.add(
                key
            )

            unique.append(
                candidate
            )

        return unique

    # ------------------------------------------------------------------
    # SERIALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def _candidate_to_dict(
        candidate: SemanticCandidate,
    ) -> dict[str, Any]:

        return asdict(
            candidate
        )


# ============================================================================
# DEBUG
# ============================================================================

def _print_result(
    result: dict[str, Any],
) -> None:

    print("\n" + "=" * 72)
    print("SIGNMUSIC SEMANTIC ENGINE")
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

    print("\nSemantic structures:")

    for structure in result[
        "semantic_structures"
    ]:

        print(
            f"\n  [{structure['segment_index']}] "
            f"{structure['text']}"
        )

        print(
            f"      Agent:       "
            f"{structure['agent']}"
        )

        print(
            f"      Action:      "
            f"{structure['action']}"
        )

        print(
            f"      Predicate:   "
            f"{structure['predicate']}"
        )

        print(
            f"      Target:      "
            f"{structure['target']}"
        )

        print(
            f"      State:       "
            f"{structure['state']}"
        )

        print(
            f"      Modality:    "
            f"{structure['modality']}"
        )

        print(
            f"      Negated:     "
            f"{structure['negated']}"
        )

        print(
            f"      Temporal:    "
            f"{structure['temporal']}"
        )

        print(
            f"      Persistence: "
            f"{structure['persistence']}"
        )

        print(
            f"      Duration:    "
            f"{structure['duration']}"
        )

        print(
            f"      Result:      "
            f"{structure['result']}"
        )

        print(
            f"      Possessor:   "
            f"{structure['possessor']}"
        )

        print(
            f"      Relations:   "
            f"{structure['relations']}"
        )

        print(
            "      Semantic roles:"
        )

        for role, value in structure[
            "semantic_roles"
        ].items():

            print(
                f"          {role}: "
                f"{value}"
            )

    print("\nSemantic candidates:")

    for candidate in result[
        "candidates"
    ]:

        print(
            f"\n  Concept: "
            f"{candidate['concept']}"
        )

        print(
            f"  Category: "
            f"{candidate['category']}"
        )

        print(
            f"  Segment: "
            f"{candidate['segment_index']}"
        )

        print(
            f"  Interpretation: "
            f"{candidate['interpretation']}"
        )

        print(
            f"  Figurative: "
            f"{candidate['figurative']}"
        )

        print(
            f"  Confidence: "
            f"{candidate['confidence']}"
        )

        print(
            f"  Uncertainty: "
            f"{candidate['uncertainty']}"
        )

        print("  Evidence:")

        for evidence in candidate[
            "evidence"
        ]:

            print(
                f"    - "
                f"{evidence['type']}: "
                f"{evidence['source_terms']} "
                f"(strength="
                f"{evidence['strength']})"
            )

    print(
        "\nSong-level interpretations:"
    )

    for candidate in result[
        "song_level_interpretations"
    ]:

        print(
            f"  - "
            f"{candidate['concept']}: "
            f"{candidate['interpretation']} "
            f"(confidence="
            f"{candidate['confidence']})"
        )


# ============================================================================
# TEST
# ============================================================================

def main() -> None:

    engine = SemanticEngine()

    examples = [
        "I cannot find you.",
        "I still need you.",
        "I feel alive again.",
        "I am alone and broken.",
        "Me muero por ti.",
        "I can't live without you.",
        "You are the light of my life.",
    ]

    for lyrics in examples:

        print(
            f"\nTEXT: {lyrics}"
        )

        try:

            result = engine.analyze(
                lyrics
            )

            _print_result(
                result
            )

        except Exception as exc:

            print(
                f"ERROR: "
                f"{type(exc).__name__}: {exc}"
            )


if __name__ == "__main__":
    main()