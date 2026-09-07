from __future__ import annotations

from typing import Any

from ..motion_plan import MotionPlan

from .dgs_grammar_realizer import (
    DGSGrammarRealizer,
)


class DGSMotionPlanner:
    """
    Convierte el resultado del DGS Grammar Realizer en MotionPlan.

    Flujo:

        Lyrics
            ↓
        Semantic analysis
            ↓
        DGS Semantic Mapper
            ↓
        DGS Lexicon Resolver
            ↓
        DGS Grammar Realizer
            ↓
        DGSMotionPlanner
            ↓
        MotionPlan
            ↓
        Blender

    IMPORTANTE:

        - No inventa movimiento para signos unresolved.
        - Conserva sign_data procedente del lexicón.
        - Conserva negación, modalidad y marcadores no manuales.
        - SIGNER es un marcador gramatical y no genera una seña.
        - Los datos prototype permanecen marcados como prototype.
    """

    DEFAULT_FPS = 25

    DEFAULT_SIGN_DURATION = 0.75

    MIN_SIGN_DURATION = 0.20

    def __init__(
        self,
        grammar_realizer: DGSGrammarRealizer | None = None,
    ) -> None:

        self.grammar_realizer = (
            grammar_realizer
            or DGSGrammarRealizer()
        )

    # ==================================================================
    # PUBLIC API
    # ==================================================================

    def plan_from_lyrics(
        self,
        lyrics: str,
    ) -> dict[str, Any]:

        grammar_result = (
            self.grammar_realizer
            .realize_from_lyrics(
                lyrics
            )
        )

        return self.plan_from_grammar(
            grammar_result
        )

    def plan_from_grammar(
        self,
        grammar_result: dict[str, Any],
    ) -> dict[str, Any]:

        units = grammar_result.get(
            "units",
            [],
        )

        all_plans: list[
            MotionPlan
        ] = []

        timeline: list[
            dict[str, Any]
        ] = []

        current_time = 0.0

        fps = self._get_fps(
            grammar_result
        )

        for unit_index, unit in enumerate(
            units
        ):

            unit_id = int(
                unit.get(
                    "unit_id",
                    unit_index,
                )
            )

            sequence = unit.get(
                "sequence",
                [],
            )

            unit_start = current_time

            for element in sequence:

                element_type = self._get_element_type(
                    element
                )

                # ======================================================
                # GRAMMATICAL MARKER
                # ======================================================

                if (
                    element.get("status")
                    == "grammatical_marker"
                    or element_type
                    == "grammatical_marker"
                ):

                    timeline.append(
                        {
                            "unit_id": unit_id,

                            "element_id": element.get(
                                "element_id"
                            ),

                            "type": (
                                "grammatical_marker"
                            ),

                            "role": element.get(
                                "role"
                            ),

                            "concept": (
                                element.get(
                                    "resolved_gloss"
                                )
                                or element.get(
                                    "requested_gloss"
                                )
                                or element.get(
                                    "requested_concept"
                                )
                            ),

                            "requested_concept": element.get(
                                "requested_concept"
                            ),

                            "requested_gloss": element.get(
                                "requested_gloss"
                            ),

                            "resolved_concept": None,

                            "resolved_gloss": element.get(
                                "resolved_gloss"
                            ),

                            "status": "grammatical_marker",

                            "confidence": self._safe_float(
                                element.get(
                                    "confidence",
                                    1.0,
                                )
                            ),

                            "start_time": current_time,

                            "duration": 0.0,

                            "end_time": current_time,

                            "negated": False,

                            "modality": None,

                            "non_manual": [],

                            "animation_ready": True,

                            "motion_plan": None,
                        }
                    )

                    continue

                # ======================================================
                # LEXICAL SIGN
                # ======================================================

                duration = self._get_duration(
                    element
                )

                start_time = (
                    current_time
                )

                end_time = (
                    start_time
                    + duration
                )

                motion_plan = (
                    self._build_motion_plan(
                        element=element,
                        duration=duration,
                        fps=fps,
                    )
                )

                all_plans.append(
                    motion_plan
                )

                timeline.append(
                    {
                        "unit_id": unit_id,

                        "element_id": element.get(
                            "element_id"
                        ),

                        "type": "lexical_sign",

                        "role": element.get(
                            "role"
                        ),

                        "requested_concept": element.get(
                            "requested_concept"
                        ),

                        "requested_gloss": element.get(
                            "requested_gloss"
                        ),

                        "resolved_concept": element.get(
                            "resolved_concept"
                        ),

                        "resolved_gloss": element.get(
                            "resolved_gloss"
                        ),

                        "status": element.get(
                            "status",
                            "unknown",
                        ),

                        "confidence": self._safe_float(
                            element.get(
                                "confidence",
                                0.0,
                            )
                        ),

                        "start_time": start_time,

                        "duration": duration,

                        "end_time": end_time,

                        "negated": bool(
                            element.get(
                                "negated",
                                False,
                            )
                        ),

                        "modality": element.get(
                            "modality"
                        ),

                        "non_manual": list(
                            element.get(
                                "non_manual",
                                [],
                            )
                            or []
                        ),

                        "animation_ready": bool(
                            element.get(
                                "animation_ready",
                                False,
                            )
                        ),

                        "motion_plan": (
                            motion_plan.to_dict()
                        ),
                    }
                )

                current_time = end_time

            unit_end = current_time

            unit_duration = (
                unit_end
                - unit_start
            )

            # ----------------------------------------------------------
            # No modificamos destructivamente el grammar_result.
            # Creamos timing aparte.
            # ----------------------------------------------------------

            timeline_unit_timing = {
                "unit_id": unit_id,
                "start_time": unit_start,
                "end_time": unit_end,
                "duration": unit_duration,
            }

            timeline.append(
                {
                    "unit_timing": (
                        timeline_unit_timing
                    )
                }
            )

        # ==================================================================
        # Build final result
        # ==================================================================

        lexical_timeline = [
            item
            for item in timeline
            if item.get(
                "type"
            )
            == "lexical_sign"
        ]

        grammatical_timeline = [
            item
            for item in timeline
            if item.get(
                "type"
            )
            == "grammatical_marker"
        ]

        resolved_motion_count = sum(
            1
            for item in lexical_timeline
            if (
                item.get(
                    "resolved_concept"
                )
                is not None
                and bool(
                    item.get(
                        "animation_ready",
                        False,
                    )
                )
            )
        )

        unresolved_count = sum(
            1
            for item in lexical_timeline
            if (
                item.get(
                    "status"
                )
                == "unresolved"
            )
        )

        resolved_count = sum(
            1
            for item in lexical_timeline
            if (
                item.get(
                    "resolved_concept"
                )
                is not None
            )
        )

        return {
            "status": self._determine_status(
                lexical_timeline
            ),

            "source_language": grammar_result.get(
                "source_language"
            ),

            "target_language": grammar_result.get(
                "target_language",
                "DGS",
            ),

            "fps": fps,

            "total_duration": current_time,

            "timeline": timeline,

            "motion_plans": [
                plan.to_dict()
                for plan in all_plans
            ],

            "metadata": {
                "unit_count": len(
                    units
                ),

                "timeline_element_count": len(
                    lexical_timeline
                )
                + len(
                    grammatical_timeline
                ),

                "motion_plan_count": len(
                    all_plans
                ),

                "resolved_motion_count": (
                    resolved_motion_count
                ),

                "resolved_count": (
                    resolved_count
                ),

                "unresolved_count": (
                    unresolved_count
                ),

                "grammatical_marker_count": (
                    len(
                        grammatical_timeline
                    )
                ),

                "motion_generation_complete": False,

                "physical_dgs_motion_validated": False,

                "official_dgs_claimed": False,
            },

            "notes": [
                "Motion timing is an intermediate planning layer.",
                "Unresolved signs do not receive invented motion.",
                "Resolved lexicon data is passed into MotionPlan.",
                "Grammatical markers are preserved separately.",
                "Prototype definitions remain marked as prototype.",
                "Physical DGS motion still requires validated sign data.",
            ],
        }

    # ==================================================================
    # BUILD MOTION PLAN
    # ==================================================================

    def _build_motion_plan(
        self,
        element: dict[str, Any],
        duration: float,
        fps: int,
    ) -> MotionPlan:

        resolved_concept = element.get(
            "resolved_concept"
        )

        resolved_gloss = element.get(
            "resolved_gloss"
        )

        requested_gloss = element.get(
            "requested_gloss"
        )

        requested_concept = element.get(
            "requested_concept"
        )

        concept = (
            resolved_concept
            or resolved_gloss
            or requested_gloss
            or requested_concept
            or "UNKNOWN"
        )

        animation_ready = bool(
            element.get(
                "animation_ready",
                False,
            )
        )

        status = str(
            element.get(
                "status",
                "unknown",
            )
        )

        non_manual_markers = list(
            element.get(
                "non_manual",
                [],
            )
            or []
        )

        negated = bool(
            element.get(
                "negated",
                False,
            )
        )

        modality = element.get(
            "modality"
        )

        # ==============================================================
        # CRITICAL:
        # The grammar realizer now propagates the original sign_data
        # from the lexicon resolver.
        # ==============================================================

        sign_data = element.get(
            "sign_data"
        )

        if not isinstance(
            sign_data,
            dict,
        ):
            sign_data = {}

        hand_shape = self._copy_dict(
            sign_data.get(
                "hand_shape",
                {},
            )
        )

        orientation = self._copy_dict(
            sign_data.get(
                "orientation",
                {},
            )
        )

        location = self._copy_dict(
            sign_data.get(
                "location",
                {},
            )
        )

        movement = self._copy_dict(
            sign_data.get(
                "movement",
                {},
            )
        )

        non_manual = {
            "markers": non_manual_markers,

            "negated": negated,

            "modality": modality,
        }

        # Preserve additional non-manual information
        # from the lexicon when present.

        lexicon_non_manual = sign_data.get(
            "non_manual"
        )

        if isinstance(
            lexicon_non_manual,
            dict,
        ):

            non_manual[
                "lexicon"
            ] = lexicon_non_manual

        # ==============================================================
        # Determine MotionPlan status
        # ==============================================================

        if (
            status
            == "unresolved"
        ):

            motion_status = (
                "lexicon_unresolved"
            )

        elif not animation_ready:

            motion_status = (
                "motion_definition_missing"
            )

        else:

            motion_status = (
                "motion_defined"
            )

        plan = MotionPlan(
            concept=str(
                concept
            ),

            duration=float(
                duration
            ),

            fps=int(
                fps
            ),

            hand_shape=hand_shape,

            orientation=orientation,

            location=location,

            movement=movement,

            non_manual=non_manual,

            status=motion_status,
        )

        # ==============================================================
        # Preserve existing physical keyframes
        # ==============================================================

        self._append_existing_keyframes(
            plan=plan,
            sign_data=sign_data,
        )

        return plan

    # ==================================================================
    # KEYFRAMES
    # ==================================================================

    @staticmethod
    def _append_existing_keyframes(
        plan: MotionPlan,
        sign_data: dict[str, Any],
    ) -> None:

        keyframes = sign_data.get(
            "keyframes"
        )

        if not isinstance(
            keyframes,
            list,
        ):

            return

        for keyframe in keyframes:

            if not isinstance(
                keyframe,
                dict,
            ):
                continue

            time_value = keyframe.get(
                "time"
            )

            if time_value is None:

                continue

            try:

                time_value = float(
                    time_value
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            phase = str(
                keyframe.get(
                    "phase",
                    "motion",
                )
            )

            bones = keyframe.get(
                "bones",
                {},
            )

            if not isinstance(
                bones,
                dict,
            ):

                bones = {}

            plan.add_keyframe(
                time=time_value,
                phase=phase,
                bones=bones,
            )

    # ==================================================================
    # DURATION
    # ==================================================================

    def _get_duration(
        self,
        element: dict[str, Any],
    ) -> float:

        # First try explicit duration coming from future
        # lexical timing layers.

        for key in (
            "duration",
            "sign_duration",
            "temporal_duration",
        ):

            value = element.get(
                key
            )

            if value is None:
                continue

            try:

                duration = float(
                    value
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            if duration > 0:

                return max(
                    duration,
                    self.MIN_SIGN_DURATION,
                )

        # If the lexicon contains a duration field,
        # use it as the next source of truth.

        sign_data = element.get(
            "sign_data"
        )

        if isinstance(
            sign_data,
            dict,
        ):

            value = sign_data.get(
                "duration"
            )

            try:

                duration = float(
                    value
                )

                if duration > 0:

                    return max(
                        duration,
                        self.MIN_SIGN_DURATION,
                    )

            except (
                TypeError,
                ValueError,
            ):
                pass

        return self.DEFAULT_SIGN_DURATION

    # ==================================================================
    # FPS
    # ==================================================================

    @classmethod
    def _get_fps(
        cls,
        grammar_result: dict[str, Any],
    ) -> int:

        metadata = grammar_result.get(
            "metadata",
            {},
        )

        fps = None

        if isinstance(
            metadata,
            dict,
        ):

            fps = metadata.get(
                "fps"
            )

        if fps is None:

            fps = grammar_result.get(
                "fps"
            )

        try:

            fps = int(
                fps
            )

        except (
            TypeError,
            ValueError,
        ):

            return cls.DEFAULT_FPS

        return max(
            fps,
            1,
        )

    # ==================================================================
    # STATUS
    # ==================================================================

    @staticmethod
    def _determine_status(
        lexical_timeline: list[
            dict[str, Any]
        ],
    ) -> str:

        if not lexical_timeline:

            return "empty"

        ready = sum(
            1
            for item in lexical_timeline
            if (
                item.get(
                    "resolved_concept"
                )
                is not None
                and bool(
                    item.get(
                        "animation_ready",
                        False,
                    )
                )
            )
        )

        unresolved = sum(
            1
            for item in lexical_timeline
            if (
                item.get(
                    "status"
                )
                == "unresolved"
            )
        )

        total = len(
            lexical_timeline
        )

        if ready == total:

            return "ready"

        if ready > 0:

            return "partially_ready"

        if unresolved == total:

            return "waiting_for_lexicon"

        return "waiting_for_motion_definitions"

    # ==================================================================
    # ELEMENT TYPE
    # ==================================================================

    @staticmethod
    def _get_element_type(
        element: dict[str, Any],
    ) -> str:

        status = str(
            element.get(
                "status",
                ""
            )
        )

        if (
            status
            == "grammatical_marker"
        ):

            return "grammatical_marker"

        return "lexical_sign"

    # ==================================================================
    # UTILITIES
    # ==================================================================

    @staticmethod
    def _copy_dict(
        value: Any,
    ) -> dict[str, Any]:

        if isinstance(
            value,
            dict,
        ):

            return dict(
                value
            )

        return {}

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


# ======================================================================
# TEST
# ======================================================================

def main() -> None:

    lyrics = """I need you
I cannot find you
I still need you"""

    planner = DGSMotionPlanner()

    result = planner.plan_from_lyrics(
        lyrics
    )

    print()
    print("=" * 78)
    print(
        "SIGNMUSIC DGS MOTION PLANNER"
    )
    print("=" * 78)

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
        f"FPS: "
        f"{result['fps']}"
    )

    print(
        f"Total duration: "
        f"{result['total_duration']:.2f}s"
    )

    print()
    print(
        "Timeline:"
    )

    for item in result[
        "timeline"
    ]:

        if "unit_timing" in item:
            continue

        print(
            f"  "
            f"{item['start_time']:6.2f}s → "
            f"{item['end_time']:6.2f}s | "
            f"{item['type']:<18} | "
            f"{item.get('resolved_gloss') or item.get('requested_gloss') or item.get('requested_concept')} | "
            f"{item.get('status')} | "
            f"animation={item.get('animation_ready')} | "
            f"non_manual={item.get('non_manual')}"
        )

    print()
    print(
        "Motion plans:"
    )

    for plan in result[
        "motion_plans"
    ]:

        print(
            f"  "
            f"{plan['concept']:<15} | "
            f"duration={plan['duration']:.2f}s | "
            f"status={plan['status']} | "
            f"keyframes={len(plan['keyframes'])}"
        )

    print()
    print(
        "Metadata:"
    )

    for key, value in result[
        "metadata"
    ].items():

        print(
            f"  {key}: {value}"
        )


if __name__ == "__main__":
    main()