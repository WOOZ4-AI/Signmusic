from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from ..arm_motion_solver import ArmMotionSolver
from ..arm_trajectory_compiler import ArmTrajectoryCompiler

from .dgs_motion_planner import DGSMotionPlanner


class DGSMotionCompiler:
    """
    Compila las definiciones de movimiento DGS hacia el formato
    utilizado por Signmusic y Blender.

    Los keyframes almacenados dentro de cada animation utilizan
    TIEMPO LOCAL.

    El executor de Blender añade animation.start_time.
    """

    DEFAULT_FPS = 25
    DEFAULT_SIGN_DURATION = 0.75
    MIN_SIGN_DURATION = 0.20

    # ==============================================================
    # MIXAMO ARM
    # ==============================================================

    RIGHT_ARM_BONE = "mixamorig7:RightArm"
    RIGHT_FOREARM_BONE = "mixamorig7:RightForeArm"

    # ==============================================================
    # MIXAMO HAND
    # ==============================================================

    FINGER_BONES = {
        "thumb": (
            "mixamorig7:RightHandThumb1",
            "mixamorig7:RightHandThumb2",
            "mixamorig7:RightHandThumb3",
        ),
        "index": (
            "mixamorig7:RightHandIndex1",
            "mixamorig7:RightHandIndex2",
            "mixamorig7:RightHandIndex3",
        ),
        "middle": (
            "mixamorig7:RightHandMiddle1",
            "mixamorig7:RightHandMiddle2",
            "mixamorig7:RightHandMiddle3",
        ),
        "ring": (
            "mixamorig7:RightHandRing1",
            "mixamorig7:RightHandRing2",
            "mixamorig7:RightHandRing3",
        ),
        "pinky": (
            "mixamorig7:RightHandPinky1",
            "mixamorig7:RightHandPinky2",
            "mixamorig7:RightHandPinky3",
        ),
    }

    # ==============================================================
    # FINGER FLEXION
    # ==============================================================

    FLEXION_DISTRIBUTION = (
        0.55,
        0.30,
        0.15,
    )

    FINGER_FLEXION_AXIS = "x"

    # ==============================================================
    # CALIBRATED MIXAMO ARM MOVEMENT
    # ==============================================================

    # La calibracion del rig mostro que el movimiento que estabamos
    # obteniendo con Z no desplazaba el brazo hacia delante.
    #
    # Para este avatar:
    #
    # RightArm +X  -> desplazamiento principal hacia la camara
    # RightForeArm +X -> acompana ese desplazamiento
    #
    # Por eso "forward" se compila directamente sobre X.
    #
    # IMPORTANTE:
    # Estos valores son una calibracion de este rig concreto.
    # No representan una regla universal de Mixamo.

    CALIBRATED_FORWARD_ARM_DEG = 25.0
    CALIBRATED_FORWARD_FOREARM_DEG = 10.0

    DEFAULT_NORMALIZED_POINTS = (
        0.0,
        0.5,
        1.0,
    )

    # ==============================================================
    # INIT
    # ==============================================================

    def __init__(
        self,
        motion_planner: DGSMotionPlanner | None = None,
        arm_solver: ArmMotionSolver | None = None,
        trajectory_compiler: ArmTrajectoryCompiler | None = None,
        lexicon_root: str | Path | None = None,
    ) -> None:

        self.motion_planner = (
            motion_planner
            or DGSMotionPlanner()
        )

        self.arm_solver = (
            arm_solver
            or ArmMotionSolver()
        )

        self.trajectory_compiler = (
            trajectory_compiler
            or ArmTrajectoryCompiler()
        )

        if lexicon_root is None:

            project_root = (
                Path(__file__)
                .resolve()
                .parents[2]
            )

            lexicon_root = (
                project_root
                / "data"
                / "signs"
                / "dgs"
            )

        self.lexicon_root = Path(
            lexicon_root
        )

        self._lexicon_cache: dict[
            str,
            dict[str, Any],
        ] = {}

    # ==================================================================
    # PUBLIC API
    # ==================================================================

    def compile_from_lyrics(
        self,
        lyrics: str,
    ) -> dict[str, Any]:

        motion_result = (
            self.motion_planner.plan_from_lyrics(
                lyrics
            )
        )

        return self.compile(
            motion_result
        )

    def compile(
        self,
        motion_result: dict[str, Any],
    ) -> dict[str, Any]:

        timeline = motion_result.get(
            "timeline",
            [],
        )

        animations: list[
            dict[str, Any]
        ] = []

        animation_index = 0

        for item in timeline:

            if "unit_timing" in item:
                continue

            if item.get(
                "type"
            ) != "lexical_sign":
                continue

            animation = (
                self._compile_timeline_item(
                    item=item,
                    index=animation_index,
                )
            )

            animations.append(
                animation
            )

            animation_index += 1

        fps = self._safe_int(
            motion_result.get(
                "fps",
                self.DEFAULT_FPS,
            ),
            self.DEFAULT_FPS,
        )

        total_duration = (
            self._safe_float(
                motion_result.get(
                    "total_duration",
                    0.0,
                )
            )
        )

        result = {
            "fps": fps,

            "total_duration": total_duration,

            "animations": animations,

            "metadata": {
                "animation_count": len(
                    animations
                ),

                "compiled_keyframe_count": sum(
                    len(
                        animation.get(
                            "keyframes",
                            [],
                        )
                    )
                    for animation in animations
                ),

                "animations_with_motion": sum(
                    1
                    for animation in animations
                    if animation.get(
                        "keyframes"
                    )
                ),

                "animations_without_motion": sum(
                    1
                    for animation in animations
                    if not animation.get(
                        "keyframes"
                    )
                ),

                "animations_with_hand_shape": sum(
                    1
                    for animation in animations
                    if animation.get(
                        "hand_shape"
                    )
                ),

                "finger_keyframe_count": sum(
                    self._count_finger_keyframes(
                        animation
                    )
                    for animation in animations
                ),

                "motion_compilation_complete": True,

                "finger_motion_compilation_complete": True,

                "timing_mode": (
                    "local_keyframe_time"
                ),

                "physical_dgs_motion_validated": False,

                "official_dgs_claimed": False,

                "calibrated_rig_motion_enabled": True,
            },

            "notes": [
                "Compiled from the existing Signmusic MotionPlan.",
                "Keyframe times are local to each animation.",
                "The Blender executor adds animation start_time.",
                "Local DGS lexicon is used as physical source data.",
                "ArmMotionSolver remains available for generic movements.",
                "The calibrated forward movement for this Mixamo rig uses the X axis.",
                "Finger flexion is converted into Mixamo finger bones.",
                "Unresolved signs never receive fabricated movement.",
                "Prototype lexicon entries remain prototype.",
            ],
        }

        errors = (
            self.validate_compiled(
                result
            )
        )

        result[
            "metadata"
        ][
            "validation_errors"
        ] = errors

        return result

    # ==================================================================
    # COMPILE TIMELINE ITEM
    # ==================================================================

    def _compile_timeline_item(
        self,
        item: dict[str, Any],
        index: int,
    ) -> dict[str, Any]:

        start_time = self._safe_float(
            item.get(
                "start_time",
                0.0,
            )
        )

        duration = self._get_duration(
            item
        )

        end_time = (
            start_time
            + duration
        )

        requested_concept = str(
            item.get(
                "requested_concept",
                "",
            )
        )

        resolved_concept = item.get(
            "resolved_concept"
        )

        resolved_gloss = item.get(
            "resolved_gloss"
        )

        requested_gloss = item.get(
            "requested_gloss"
        )

        concept = str(
            resolved_concept
            or resolved_gloss
            or requested_gloss
            or requested_concept
            or "UNKNOWN"
        )

        status = str(
            item.get(
                "status",
                "unknown",
            )
        )

        confidence = self._safe_float(
            item.get(
                "confidence",
                0.0,
            )
        )

        non_manual = list(
            item.get(
                "non_manual",
                [],
            )
            or []
        )

        negated = bool(
            item.get(
                "negated",
                False,
            )
        )

        modality = item.get(
            "modality"
        )

        # ==============================================================
        # UNRESOLVED SIGN
        # ==============================================================

        if status == "unresolved":

            return {
                "index": index,

                "concept": concept,

                "start_time": start_time,

                "duration": duration,

                "end_time": end_time,

                "status": (
                    "lexicon_unresolved"
                ),

                "confidence": confidence,

                "hand_shape": {},

                "orientation": {},

                "location": {},

                "movement": {},

                "non_manual": non_manual,

                "negated": negated,

                "modality": modality,

                "keyframes": [],

                "warnings": [
                    "No local DGS lexicon entry exists.",
                    "No movement was invented.",
                ],
            }

        # ==============================================================
        # MOTION PLAN
        # ==============================================================

        motion_plan_data = item.get(
            "motion_plan",
            {}
        )

        if not isinstance(
            motion_plan_data,
            dict,
        ):

            motion_plan_data = {}

        sign_data = (
            self._extract_sign_data(
                item=item,
                motion_plan_data=motion_plan_data,
                concept=concept,
            )
        )

        hand_shape = self._copy_dict(
            sign_data.get(
                "hand_shape",
                motion_plan_data.get(
                    "hand_shape",
                    {},
                ),
            )
        )

        orientation = self._copy_dict(
            sign_data.get(
                "orientation",
                motion_plan_data.get(
                    "orientation",
                    {},
                ),
            )
        )

        location = self._copy_dict(
            sign_data.get(
                "location",
                motion_plan_data.get(
                    "location",
                    {},
                ),
            )
        )

        movement = self._copy_dict(
            sign_data.get(
                "movement",
                motion_plan_data.get(
                    "movement",
                    {},
                ),
            )
        )

        lexicon_status = str(
            sign_data.get(
                "status",
                motion_plan_data.get(
                    "status",
                    "unknown",
                ),
            )
        )

        keyframes = (
            self._compile_physical_keyframes(
                sign_data=sign_data,
                movement=movement,
                hand_shape=hand_shape,
                duration=duration,
            )
        )

        warnings: list[str] = []

        if not sign_data:

            warnings.append(
                "No physical sign definition was found "
                "in the pipeline or local lexicon."
            )

        if not movement:

            warnings.append(
                "No movement definition was found."
            )

        if not hand_shape:

            warnings.append(
                "No hand_shape definition was found."
            )

        if (
            not keyframes
            and (
                movement
                or hand_shape
            )
        ):

            warnings.append(
                "Physical sign data exists, but no "
                "executable keyframes were generated."
            )

        final_status = (
            "motion_defined"
            if keyframes
            else "motion_definition_missing"
        )

        return {
            "index": index,

            "concept": concept,

            "start_time": start_time,

            "duration": duration,

            "end_time": end_time,

            "status": final_status,

            "lexicon_status": lexicon_status,

            "confidence": confidence,

            "hand_shape": hand_shape,

            "orientation": orientation,

            "location": location,

            "movement": movement,

            "non_manual": {
                "markers": non_manual,

                "negated": negated,

                "modality": modality,

                "lexicon": (
                    sign_data.get(
                        "non_manual",
                        {},
                    )
                ),
            },

            "keyframes": keyframes,

            "warnings": warnings,
        }

    # ==================================================================
    # SIGN DATA
    # ==================================================================

    def _extract_sign_data(
        self,
        item: dict[str, Any],
        motion_plan_data: dict[str, Any],
        concept: str,
    ) -> dict[str, Any]:

        sign_data = item.get(
            "sign_data"
        )

        if isinstance(
            sign_data,
            dict,
        ) and sign_data:

            return dict(
                sign_data
            )

        sign_data = motion_plan_data.get(
            "sign_data"
        )

        if isinstance(
            sign_data,
            dict,
        ) and sign_data:

            return dict(
                sign_data
            )

        physical = {}

        for key in (
            "concept",
            "status",
            "duration",
            "confidence",
            "hand_shape",
            "orientation",
            "location",
            "movement",
            "non_manual",
            "keyframes",
        ):

            if key in motion_plan_data:

                physical[
                    key
                ] = motion_plan_data[
                    key
                ]

        if self._contains_physical_data(
            physical
        ):

            return physical

        local_sign = (
            self._load_lexicon_sign(
                concept
            )
        )

        if local_sign:

            return local_sign

        requested_concept = str(
            item.get(
                "requested_concept",
                "",
            )
        )

        if requested_concept:

            local_sign = (
                self._load_lexicon_sign(
                    requested_concept
                )
            )

            if local_sign:

                return local_sign

        return {}

    @staticmethod
    def _contains_physical_data(
        data: dict[str, Any],
    ) -> bool:

        return any(
            bool(
                data.get(
                    key
                )
            )
            for key in (
                "hand_shape",
                "orientation",
                "location",
                "movement",
                "keyframes",
            )
        )

    # ==================================================================
    # LOCAL LEXICON
    # ==================================================================

    def _load_lexicon_sign(
        self,
        concept: str,
    ) -> dict[str, Any]:

        normalized = (
            self._normalize_concept(
                concept
            )
        )

        if not normalized:

            return {}

        if normalized in self._lexicon_cache:

            return dict(
                self._lexicon_cache[
                    normalized
                ]
            )

        if not self.lexicon_root.exists():

            return {}

        direct_path = (
            self.lexicon_root
            / f"{normalized}.json"
        )

        if direct_path.exists():

            data = (
                self._read_json(
                    direct_path
                )
            )

            if data:

                self._lexicon_cache[
                    normalized
                ] = data

                return dict(
                    data
                )

        for json_path in sorted(
            self.lexicon_root.glob(
                "*.json"
            )
        ):

            data = (
                self._read_json(
                    json_path
                )
            )

            if not data:

                continue

            data_concept = (
                self._normalize_concept(
                    str(
                        data.get(
                            "concept",
                            "",
                        )
                    )
                )
            )

            filename_concept = (
                self._normalize_concept(
                    json_path.stem
                )
            )

            if (
                data_concept
                == normalized
                or filename_concept
                == normalized
            ):

                self._lexicon_cache[
                    normalized
                ] = data

                return dict(
                    data
                )

        return {}

    @staticmethod
    def _read_json(
        path: Path,
    ) -> dict[str, Any]:

        try:

            with path.open(
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

            return {}

        if not isinstance(
            data,
            dict,
        ):

            return {}

        return data

    # ==================================================================
    # PHYSICAL KEYFRAMES
    # ==================================================================

    def _compile_physical_keyframes(
        self,
        sign_data: dict[str, Any],
        movement: dict[str, Any],
        hand_shape: dict[str, Any],
        duration: float,
    ) -> list[dict[str, Any]]:

        explicit_keyframes = (
            self._extract_explicit_keyframes(
                sign_data
            )
        )

        if explicit_keyframes:

            return (
                self._normalize_explicit_keyframes(
                    explicit_keyframes,
                    duration,
                )
            )

        if (
            not movement
            and not hand_shape
        ):

            return []

        result: list[
            dict[str, Any]
        ] = []

        path = ""

        if movement:
            path = str(
                movement.get(
                    "path"
                )
                or movement.get(
                    "direction"
                )
                or movement.get(
                    "type"
                )
                or ""
            ).strip().lower()

        for factor in (
            self.DEFAULT_NORMALIZED_POINTS
        ):

            bones: dict[
                str,
                dict[str, Any]
            ] = {}

            # ----------------------------------------------------------
            # CALIBRATED FORWARD MOVEMENT
            # ----------------------------------------------------------
            #
            # The Mixamo calibration showed that the old Z rotation
            # was not moving the hand in the intended forward direction.
            #
            # For "forward", use the calibrated X axis directly.
            #
            if path in (
                "forward",
                "point_forward",
            ):

                bones.update(
                    self._compile_calibrated_forward_motion(
                        factor
                    )
                )

            # ----------------------------------------------------------
            # GENERIC ARM MOVEMENT
            # ----------------------------------------------------------

            elif movement:

                solved = (
                    self.arm_solver
                    .solve_movement(
                        str(path),
                        factor,
                    )
                )

                bones.update(
                    self._map_solver_bones(
                        solved
                    )
                )

            # ----------------------------------------------------------
            # FINGERS
            # ----------------------------------------------------------

            finger_bones = (
                self._compile_finger_bones(
                    hand_shape
                )
            )

            bones.update(
                finger_bones
            )

            result.append(
                {
                    "time": (
                        duration
                        * factor
                    ),

                    "phase": (
                        self._phase_for_factor(
                            factor
                        )
                    ),

                    "bones": bones,
                }
            )

        return result

    # ==================================================================
    # CALIBRATED FORWARD MOTION
    # ==================================================================

    @classmethod
    def _compile_calibrated_forward_motion(
        cls,
        factor: float,
    ) -> dict[str, dict[str, Any]]:

        factor = max(
            0.0,
            min(
                1.0,
                float(factor),
            )
        )

        arm_angle = (
            cls.CALIBRATED_FORWARD_ARM_DEG
            * factor
        )

        forearm_angle = (
            cls.CALIBRATED_FORWARD_FOREARM_DEG
            * factor
        )

        return {
            cls.RIGHT_ARM_BONE: {
                "rotation": [
                    arm_angle,
                    0.0,
                    0.0,
                ]
            },

            cls.RIGHT_FOREARM_BONE: {
                "rotation": [
                    forearm_angle,
                    0.0,
                    0.0,
                ]
            },
        }

    # ==================================================================
    # FINGERS
    # ==================================================================

    @classmethod
    def _compile_finger_bones(
        cls,
        hand_shape: dict[str, Any],
    ) -> dict[
        str,
        dict[str, Any]
    ]:

        fingers = hand_shape.get(
            "fingers",
            {}
        )

        if not isinstance(
            fingers,
            dict,
        ):

            return {}

        result: dict[
            str,
            dict[str, Any]
        ] = {}

        for finger_name, finger_data in (
            fingers.items()
        ):

            normalized_name = (
                cls._normalize_finger_name(
                    finger_name
                )
            )

            if normalized_name is None:
                continue

            if not isinstance(
                finger_data,
                dict,
            ):
                continue

            flexion = finger_data.get(
                "flexion"
            )

            if flexion is None:

                flexion = finger_data.get(
                    "angle"
                )

            try:

                flexion = float(
                    flexion
                )

            except (
                TypeError,
                ValueError,
            ):

                continue

            flexion = max(
                0.0,
                min(
                    120.0,
                    flexion,
                )
            )

            bone_names = cls.FINGER_BONES[
                normalized_name
            ]

            for bone_name, percentage in zip(
                bone_names,
                cls.FLEXION_DISTRIBUTION,
            ):

                angle = (
                    flexion
                    * percentage
                )

                rotation = [
                    0.0,
                    0.0,
                    0.0,
                ]

                if (
                    cls.FINGER_FLEXION_AXIS
                    == "x"
                ):

                    rotation[0] = (
                        float(angle)
                    )

                elif (
                    cls.FINGER_FLEXION_AXIS
                    == "y"
                ):

                    rotation[1] = (
                        float(angle)
                    )

                elif (
                    cls.FINGER_FLEXION_AXIS
                    == "z"
                ):

                    rotation[2] = (
                        float(angle)
                    )

                result[
                    bone_name
                ] = {
                    "rotation": rotation
                }

        # --------------------------------------------------------------
        # THUMB OPPOSITION
        # --------------------------------------------------------------

        thumb_data = fingers.get(
            "thumb"
        )

        if isinstance(
            thumb_data,
            dict,
        ):

            opposition = (
                thumb_data.get(
                    "opposition"
                )
            )

            if opposition is not None:

                try:

                    opposition = float(
                        opposition
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    opposition = 0.0

                opposition = max(
                    -90.0,
                    min(
                        90.0,
                        opposition,
                    )
                )

                thumb_bones = (
                    cls.FINGER_BONES[
                        "thumb"
                    ]
                )

                thumb_distribution = (
                    0.60,
                    0.25,
                    0.15,
                )

                for bone_name, percentage in zip(
                    thumb_bones,
                    thumb_distribution,
                ):

                    result[
                        bone_name
                    ] = {
                        "rotation": [
                            0.0,
                            float(
                                opposition
                                * percentage
                            ),
                            0.0,
                        ]
                    }

        return result

    @staticmethod
    def _normalize_finger_name(
        name: str,
    ) -> str | None:

        aliases = {
            "thumb": "thumb",
            "index": "index",
            "middle": "middle",
            "ring": "ring",
            "pinky": "pinky",
            "little": "pinky",
        }

        return aliases.get(
            str(
                name
            )
            .strip()
            .lower()
        )

    # ==================================================================
    # EXPLICIT KEYFRAMES
    # ==================================================================

    @staticmethod
    def _extract_explicit_keyframes(
        sign_data: dict[str, Any],
    ) -> list[
        dict[str, Any]
    ]:

        keyframes = sign_data.get(
            "keyframes",
            []
        )

        if not isinstance(
            keyframes,
            list,
        ):

            return []

        return [
            dict(
                keyframe
            )
            for keyframe in keyframes
            if isinstance(
                keyframe,
                dict,
            )
        ]

    @classmethod
    def _normalize_explicit_keyframes(
        cls,
        keyframes: list[
            dict[str, Any]
        ],
        duration: float,
    ) -> list[
        dict[str, Any]
    ]:

        if not keyframes:

            return []

        max_time = max(
            cls._safe_float(
                keyframe.get(
                    "time",
                    0.0,
                )
            )
            for keyframe
            in keyframes
        )

        result = []

        for keyframe in keyframes:

            raw_time = cls._safe_float(
                keyframe.get(
                    "time",
                    0.0,
                )
            )

            if max_time > 0:

                factor = (
                    raw_time
                    / max_time
                )

            else:

                factor = 0.0

            factor = max(
                0.0,
                min(
                    1.0,
                    factor,
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

            result.append(
                {
                    "time": (
                        duration
                        * factor
                    ),

                    "phase": str(
                        keyframe.get(
                            "phase",
                            "motion",
                        )
                    ),

                    "bones": cls._map_solver_bones(
                        bones
                    ),
                }
            )

        return result

    # ==================================================================
    # MAP BONE NAMES
    # ==================================================================

    @classmethod
    def _map_solver_bones(
        cls,
        bones: dict[str, Any],
    ) -> dict[
        str,
        dict[str, Any]
    ]:

        result: dict[
            str,
            dict[str, Any]
        ] = {}

        right_arm = bones.get(
            "right_arm"
        )

        if isinstance(
            right_arm,
            dict,
        ):

            result[
                cls.RIGHT_ARM_BONE
            ] = dict(
                right_arm
            )

        right_forearm = bones.get(
            "right_forearm"
        )

        if isinstance(
            right_forearm,
            dict,
        ):

            result[
                cls.RIGHT_FOREARM_BONE
            ] = dict(
                right_forearm
            )

        for bone_name, bone_data in (
            bones.items()
        ):

            if not isinstance(
                bone_data,
                dict,
            ):

                continue

            if ":" in str(
                bone_name
            ):

                result[
                    str(
                        bone_name
                    )
                ] = dict(
                    bone_data
                )

        return result

    # ==================================================================
    # DURATION
    # ==================================================================

    def _get_duration(
        self,
        item: dict[str, Any],
    ) -> float:

        motion_plan = item.get(
            "motion_plan",
            {}
        )

        sources = [
            item,
        ]

        if isinstance(
            motion_plan,
            dict,
        ):

            sources.append(
                motion_plan
            )

        for source in sources:

            for key in (
                "duration",
                "sign_duration",
                "temporal_duration",
            ):

                value = source.get(
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

        concept = str(
            item.get(
                "resolved_concept",
                ""
            )
            or item.get(
                "resolved_gloss",
                ""
            )
            or item.get(
                "requested_gloss",
                ""
            )
            or item.get(
                "requested_concept",
                ""
            )
        )

        sign_data = (
            self._load_lexicon_sign(
                concept
            )
        )

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
    # PHASE
    # ==================================================================

    @staticmethod
    def _phase_for_factor(
        factor: float,
    ) -> str:

        if factor <= 0.0:

            return "start"

        if factor >= 1.0:

            return "end"

        return "motion"

    # ==================================================================
    # VALIDATION
    # ==================================================================

    @classmethod
    def validate_compiled(
        cls,
        compiled_result: dict[str, Any],
    ) -> list[str]:

        errors: list[str] = []

        animations = compiled_result.get(
            "animations",
            [],
        )

        if not isinstance(
            animations,
            list,
        ):

            return [
                "animations debe ser una lista."
            ]

        for index, animation in enumerate(
            animations
        ):

            if not isinstance(
                animation,
                dict,
            ):

                errors.append(
                    f"Animation {index} inválida."
                )

                continue

            duration = cls._safe_float(
                animation.get(
                    "duration",
                    0.0,
                )
            )

            keyframes = animation.get(
                "keyframes",
                [],
            )

            if not isinstance(
                keyframes,
                list,
            ):

                errors.append(
                    f"Animation {index}: "
                    "keyframes inválidos."
                )

                continue

            previous_time = -1.0

            for keyframe_index, keyframe in enumerate(
                keyframes
            ):

                if not isinstance(
                    keyframe,
                    dict,
                ):

                    errors.append(
                        f"Animation {index}, "
                        f"keyframe {keyframe_index}: "
                        "inválido."
                    )

                    continue

                local_time = (
                    cls._safe_float(
                        keyframe.get(
                            "time",
                            0.0,
                        )
                    )
                )

                if local_time < 0:

                    errors.append(
                        f"Animation {index}, "
                        f"keyframe {keyframe_index}: "
                        "tiempo local negativo."
                    )

                if local_time < previous_time:

                    errors.append(
                        f"Animation {index}, "
                        f"keyframe {keyframe_index}: "
                        "tiempo local fuera de orden."
                    )

                if local_time > duration + 1e-6:

                    errors.append(
                        f"Animation {index}, "
                        f"keyframe {keyframe_index}: "
                        "tiempo local excede la duración."
                    )

                previous_time = local_time

                bones = keyframe.get(
                    "bones",
                    {},
                )

                if not isinstance(
                    bones,
                    dict,
                ):

                    errors.append(
                        f"Animation {index}, "
                        f"keyframe {keyframe_index}: "
                        "bones inválidos."
                    )

        return errors

    # ==================================================================
    # COUNT FINGER KEYFRAMES
    # ==================================================================

    @classmethod
    def _count_finger_keyframes(
        cls,
        animation: dict[str, Any],
    ) -> int:

        known_finger_bones = {
            bone
            for group
            in cls.FINGER_BONES.values()
            for bone
            in group
        }

        count = 0

        for keyframe in animation.get(
            "keyframes",
            [],
        ):

            bones = keyframe.get(
                "bones",
                {}
            )

            if not isinstance(
                bones,
                dict,
            ):

                continue

            count += sum(
                1
                for bone_name
                in bones
                if bone_name
                in known_finger_bones
            )

        return count

    # ==================================================================
    # SAVE PIPELINE
    # ==================================================================

    @staticmethod
    def save_pipeline_sequence(
        compiled_result: dict[str, Any],
        output_path: str | Path,
    ) -> Path:

        output_path = Path(
            output_path
        )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        payload = (
            DGSMotionCompiler
            ._convert_to_pipeline_format(
                compiled_result
            )
        )

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:

            json.dump(
                payload,
                file,
                ensure_ascii=False,
                indent=4,
            )

        return output_path

    @staticmethod
    def _convert_to_pipeline_format(
        compiled_result: dict[str, Any],
    ) -> dict[str, Any]:

        return {
            "bpm": 120,

            "fps": compiled_result.get(
                "fps",
                DGSMotionCompiler.DEFAULT_FPS,
            ),

            "beat_duration": 0.5,

            "total_duration": compiled_result.get(
                "total_duration",
                0.0,
            ),

            "animations": compiled_result.get(
                "animations",
                [],
            ),

            "metadata": compiled_result.get(
                "metadata",
                {},
            ),
        }

    # ==================================================================
    # HELPERS
    # ==================================================================

    @staticmethod
    def _safe_float(
        value: Any,
    ) -> float:

        try:

            return float(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return 0.0

    @staticmethod
    def _safe_int(
        value: Any,
        default: int,
    ) -> int:

        try:

            return int(
                value
            )

        except (
            TypeError,
            ValueError,
        ):

            return default

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
    def _normalize_concept(
        concept: str,
    ) -> str:

        return (
            str(
                concept
            )
            .strip()
            .lower()
            .replace(
                " ",
                "_",
            )
            .replace(
                "-",
                "_",
            )
        )


# ======================================================================
# TEST
# ======================================================================

def main() -> None:

    lyrics = """I need you
I cannot find you
I still need you"""

    compiler = (
        DGSMotionCompiler()
    )

    result = (
        compiler.compile_from_lyrics(
            lyrics
        )
    )

    print()
    print("=" * 78)
    print(
        "SIGNMUSIC DGS MOTION COMPILER"
    )
    print("=" * 78)

    print(
        f"FPS: "
        f"{result['fps']}"
    )

    print(
        f"Total duration: "
        f"{result['total_duration']:.3f}s"
    )

    print(
        f"Timing mode: "
        f"{result['metadata']['timing_mode']}"
    )

    print(
        f"Calibrated rig motion: "
        f"{result['metadata']['calibrated_rig_motion_enabled']}"
    )

    print()
    print(
        "Animations:"
    )

    for animation in result[
        "animations"
    ]:

        keyframes = animation.get(
            "keyframes",
            [],
        )

        print(
            f"  "
            f"{animation['start_time']:6.2f}s → "
            f"{animation['end_time']:6.2f}s | "
            f"{animation['concept']:<15} | "
            f"{animation['status']:<28} | "
            f"keyframes={len(keyframes)}"
        )

        for keyframe in keyframes:

            arm = keyframe.get(
                "bones",
                {}
            ).get(
                DGSMotionCompiler.RIGHT_ARM_BONE,
                {}
            )

            forearm = keyframe.get(
                "bones",
                {}
            ).get(
                DGSMotionCompiler.RIGHT_FOREARM_BONE,
                {}
            )

            arm_rotation = arm.get(
                "rotation",
                [],
            )

            forearm_rotation = forearm.get(
                "rotation",
                [],
            )

            print(
                f"      local "
                f"{keyframe['time']:.3f}s | "
                f"phase={keyframe['phase']:<6} | "
                f"bones={len(keyframe['bones'])} | "
                f"arm={arm_rotation} | "
                f"forearm={forearm_rotation}"
            )

    print()
    print(
        "Validation:"
    )

    errors = (
        compiler.validate_compiled(
            result
        )
    )

    print(
        errors
        or "OK"
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