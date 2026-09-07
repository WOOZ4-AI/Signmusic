from typing import Any, Dict

from keyframe_generator import KeyframeGenerator
from motion_plan import MotionKeyframe, MotionPlan

from hand_pose_compiler import HandPoseCompiler
from hand_orientation_compiler import HandOrientationCompiler
from hand_location_compiler import HandLocationCompiler

from movement_compiler import MovementCompiler
from arm_trajectory_compiler import ArmTrajectoryCompiler
from arm_motion_solver import ArmMotionSolver


class MotionGenerator:
    """
    Generador principal de MotionPlan para Signmusic.

    Arquitectura:

        SignModel
            ↓
        MotionGenerator
            ├── HandPoseCompiler
            ├── HandOrientationCompiler
            ├── HandLocationCompiler
            ├── MovementCompiler
            ├── ArmTrajectoryCompiler
            └── ArmMotionSolver
                    ↓
                MotionPlan
                    ↓
                MotionCompiler
                    ↓
                Blender

    IMPORTANTE
    ----------

    Los movimientos corporales contenidos en
    KeyframeGenerator son experimentales y NO se
    heredan automáticamente.

    El movimiento espacial de un signo sigue ahora
    este flujo:

        movement conceptual
              ↓
        MovementCompiler
              ↓
        trayectoria temporal
              ↓
        ArmTrajectoryCompiler
              ↓
        posiciones intermedias
              ↓
        ArmMotionSolver
              ↓
        RightArm / RightForeArm

    La implementación actual del ArmMotionSolver es una
    aproximación determinista y no pretende todavía ser
    una IK anatómicamente perfecta.
    """

    DEFAULT_FPS = 25

    # =========================================================
    # CONSTRUCTOR
    # =========================================================

    def __init__(
        self,
        fps: int = DEFAULT_FPS,
        keyframe_generator: KeyframeGenerator | None = None,
        hand_pose_compiler: HandPoseCompiler | None = None,
        hand_orientation_compiler: (
            HandOrientationCompiler | None
        ) = None,
        hand_location_compiler: (
            HandLocationCompiler | None
        ) = None,
        movement_compiler: MovementCompiler | None = None,
        arm_trajectory_compiler: (
            ArmTrajectoryCompiler | None
        ) = None,
        arm_motion_solver: ArmMotionSolver | None = None,
    ):
        if fps <= 0:
            raise ValueError(
                "fps debe ser mayor que 0."
            )

        self.fps = int(
            fps
        )

        self.keyframe_generator = (
            keyframe_generator
            or KeyframeGenerator()
        )

        self.hand_pose_compiler = (
            hand_pose_compiler
            or HandPoseCompiler()
        )

        self.hand_orientation_compiler = (
            hand_orientation_compiler
            or HandOrientationCompiler()
        )

        self.hand_location_compiler = (
            hand_location_compiler
            or HandLocationCompiler()
        )

        self.movement_compiler = (
            movement_compiler
            or MovementCompiler()
        )

        self.arm_trajectory_compiler = (
            arm_trajectory_compiler
            or ArmTrajectoryCompiler()
        )

        self.arm_motion_solver = (
            arm_motion_solver
            or ArmMotionSolver()
        )

    # =========================================================
    # GENERAR MOVIMIENTO
    # =========================================================

    def generate_motion(
        self,
        sign: Dict[str, Any],
    ) -> MotionPlan:
        """
        Genera un MotionPlan completo.

        Incluye:

            - forma de mano
            - orientación
            - ubicación semántica
            - movimiento
            - trayectoria del brazo
            - rotación del brazo
            - rotación del antebrazo
        """

        if not isinstance(
            sign,
            dict,
        ):
            raise TypeError(
                "sign debe ser un diccionario."
            )

        # =====================================================
        # CONCEPTO
        # =====================================================

        concept = str(
            sign.get(
                "concept",
                "UNKNOWN",
            )
        ).strip().upper()

        if not concept:
            raise ValueError(
                "El concepto no puede estar vacío."
            )

        # =====================================================
        # GESTO BASE
        # =====================================================

        gesture = (
            self.keyframe_generator.get_gesture(
                concept
            )
        )

        if gesture["status"] != "defined":

            raise ValueError(
                f"No existe un gesto definido para "
                f"el concepto {concept}."
            )

        gesture_data = (
            gesture["gesture"]
        )

        source_duration = float(
            gesture_data.get(
                "duration",
                0.5,
            )
        )

        if source_duration <= 0:

            source_duration = 0.5

        # =====================================================
        # DURACIÓN FINAL
        # =====================================================

        duration = float(
            sign.get(
                "duration",
                source_duration,
            )
        )

        if duration <= 0:

            raise ValueError(
                f"El signo {concept} debe tener "
                f"una duración mayor que 0."
            )

        # =====================================================
        # DATOS ESTRUCTURALES
        # =====================================================

        hand_shape = dict(
            sign.get(
                "hand_shape",
                {},
            )
        )

        orientation = dict(
            sign.get(
                "orientation",
                {},
            )
        )

        location = dict(
            sign.get(
                "location",
                {},
            )
        )

        movement = dict(
            sign.get(
                "movement",
                {},
            )
        )

        non_manual = dict(
            sign.get(
                "non_manual",
                {},
            )
        )

        # =====================================================
        # COMPATIBILIDAD CON GESTOS ANTIGUOS
        # =====================================================

        use_gesture_motion = bool(
            sign.get(
                "use_gesture_motion",
                False,
            )
        )

        # =====================================================
        # COMPILAR MOVIMIENTO SEMÁNTICO
        # =====================================================

        compiled_movement = None

        if movement:

            compiled_movement = (
                self.movement_compiler
                .compile_movement(
                    movement
                )
            )

        # =====================================================
        # COMPILAR TRAYECTORIA DEL BRAZO
        # =====================================================

        compiled_trajectory = None

        if compiled_movement:

            compiled_trajectory = (
                self.arm_trajectory_compiler
                .compile_trajectory(
                    compiled_movement,
                    total_duration=duration,
                )
            )

        # =====================================================
        # KEYFRAMES DE ORIGEN
        # =====================================================

        source_keyframes = (
            gesture_data.get(
                "keyframes",
                [],
            )
        )

        # -----------------------------------------------------
        # FALLBACK
        # -----------------------------------------------------

        if not source_keyframes:

            source_keyframes = [
                {
                    "time": 0.0,
                },

                {
                    "time": (
                        source_duration
                        / 2.0
                    ),
                },

                {
                    "time": source_duration,
                },
            ]

        # =====================================================
        # GENERAR KEYFRAMES
        # =====================================================

        keyframes = []

        for source_keyframe in source_keyframes:

            # -------------------------------------------------
            # TIEMPO ORIGINAL
            # -------------------------------------------------

            source_time = float(
                source_keyframe.get(
                    "time",
                    0.0,
                )
            )

            # -------------------------------------------------
            # NORMALIZACIÓN
            # -------------------------------------------------

            normalized_time = (
                source_time
                / source_duration
            )

            normalized_time = max(
                0.0,
                min(
                    1.0,
                    normalized_time,
                ),
            )

            # -------------------------------------------------
            # TIEMPO FINAL
            # -------------------------------------------------

            time = (
                normalized_time
                * duration
            )

            # -------------------------------------------------
            # FASE
            # -------------------------------------------------

            phase = (
                self._detect_phase(
                    normalized_time
                )
            )

            # =================================================
            # HUESOS
            # =================================================

            bones = {}

            # -------------------------------------------------
            # GESTO CORPORAL EXPERIMENTAL
            # -------------------------------------------------

            if use_gesture_motion:

                source_bones = (
                    source_keyframe.get(
                        "bones",
                        {},
                    )
                )

                if isinstance(
                    source_bones,
                    dict,
                ):

                    bones.update(
                        self._normalize_bones(
                            source_bones
                        )
                    )

            # -------------------------------------------------
            # FORMA DE MANO
            # -------------------------------------------------

            compiled_hand_bones = (
                self._compile_hand_bones_for_phase(
                    hand_shape,
                    phase,
                )
            )

            bones.update(
                compiled_hand_bones
            )

            # -------------------------------------------------
            # ORIENTACIÓN
            # -------------------------------------------------

            compiled_orientation = (
                self._compile_orientation_for_phase(
                    orientation,
                    phase,
                )
            )

            bones.update(
                compiled_orientation
            )

            # -------------------------------------------------
            # MOVIMIENTO DEL BRAZO
            # -------------------------------------------------
            #
            # El movimiento solamente se aplica cuando existe
            # una trayectoria compilada.
            #
            # START:
            #     posición inicial
            #
            # MOTION:
            #     posición evaluada en el tiempo actual
            #
            # END:
            #     posición final
            # -------------------------------------------------

            arm_motion_bones = (
                self._compile_arm_motion_for_time(
                    compiled_trajectory,
                    time,
                )
            )

            bones.update(
                arm_motion_bones
            )

            # -------------------------------------------------
            # CREAR KEYFRAME
            # -------------------------------------------------

            keyframes.append(
                MotionKeyframe(
                    time=time,
                    phase=phase,
                    bones=bones,
                )
            )

        # =====================================================
        # MOTION PLAN
        # =====================================================

        plan = MotionPlan(
            concept=concept,

            duration=duration,

            fps=self.fps,

            hand_shape=hand_shape,

            orientation=orientation,

            location=location,

            movement=(
                compiled_movement
                if compiled_movement is not None
                else movement
            ),

            non_manual=non_manual,

            keyframes=keyframes,

            status="motion_defined",
        )

        return plan

    # =========================================================
    # MOVIMIENTO DEL BRAZO SEGÚN TIEMPO
    # =========================================================

    def _compile_arm_motion_for_time(
        self,
        trajectory: Dict[str, Any] | None,
        time: float,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Evalúa la trayectoria del brazo en un momento dado.

        Devuelve:

            right_arm
            right_forearm

        Si no existe trayectoria, devuelve {}.
        """

        if not trajectory:
            return {}

        try:

            position = (
                self.arm_trajectory_compiler
                .evaluate_at_time(
                    trajectory,
                    float(time),
                )
            )

        except (
            TypeError,
            ValueError,
        ):

            return {}

        return (
            self.arm_motion_solver
            .solve_position(
                position
            )
        )

    # =========================================================
    # COMPILAR MANO SEGÚN FASE
    # =========================================================

    def _compile_hand_bones_for_phase(
        self,
        hand_shape: Dict[str, Any],
        phase: str,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Durante start/end utiliza pose neutra.
        Durante motion utiliza la pose solicitada.
        """

        if not hand_shape:
            return {}

        if phase in (
            "start",
            "end",
        ):

            return self._create_neutral_hand(
                hand_shape
            )

        return self._compile_hand_bones(
            hand_shape
        )

    # =========================================================
    # CREAR MANO NEUTRA
    # =========================================================

    def _create_neutral_hand(
        self,
        hand_shape: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Genera una pose neutra explícita.
        """

        if not hand_shape:
            return {}

        result = {}

        # -----------------------------------------------------
        # DOS MANOS
        # -----------------------------------------------------

        if (
            "left" in hand_shape
            or "right" in hand_shape
        ):

            for side in (
                "left",
                "right",
            ):

                hand = (
                    hand_shape.get(
                        side
                    )
                )

                if not hand:
                    continue

                fingers = (
                    hand.get(
                        "fingers",
                        {},
                    )
                )

                if not isinstance(
                    fingers,
                    dict,
                ):
                    continue

                for finger_name in fingers:

                    normalized_finger = (
                        str(
                            finger_name
                        )
                        .strip()
                        .lower()
                    )

                    if normalized_finger not in {
                        "thumb",
                        "index",
                        "middle",
                        "ring",
                        "pinky",
                    }:
                        continue

                    for segment in range(
                        1,
                        4,
                    ):

                        bone_name = (
                            f"{side}_"
                            f"{normalized_finger}_"
                            f"{segment}"
                        )

                        result[
                            bone_name
                        ] = {
                            "rotation": [
                                0.0,
                                0.0,
                                0.0,
                            ]
                        }

            return result

        # -----------------------------------------------------
        # UNA MANO → DERECHA
        # -----------------------------------------------------

        fingers = (
            hand_shape.get(
                "fingers",
                {},
            )
        )

        if not isinstance(
            fingers,
            dict,
        ):
            return {}

        for finger_name in fingers:

            normalized_finger = (
                str(
                    finger_name
                )
                .strip()
                .lower()
            )

            if normalized_finger not in {
                "thumb",
                "index",
                "middle",
                "ring",
                "pinky",
            }:
                continue

            for segment in range(
                1,
                4,
            ):

                bone_name = (
                    "right_"
                    f"{normalized_finger}_"
                    f"{segment}"
                )

                result[
                    bone_name
                ] = {
                    "rotation": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                }

        return result

    # =========================================================
    # COMPILAR MANOS
    # =========================================================

    def _compile_hand_bones(
        self,
        hand_shape: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:

        if not hand_shape:
            return {}

        # -----------------------------------------------------
        # DOS MANOS
        # -----------------------------------------------------

        if (
            "left" in hand_shape
            or "right" in hand_shape
        ):

            return (
                self.hand_pose_compiler
                .compile_hands(
                    left_hand=(
                        hand_shape.get(
                            "left"
                        )
                    ),

                    right_hand=(
                        hand_shape.get(
                            "right"
                        )
                    ),
                )
            )

        # -----------------------------------------------------
        # UNA MANO → DERECHA
        # -----------------------------------------------------

        return (
            self.hand_pose_compiler
            .compile_hand(
                hand_shape,
                "right",
            )
        )

    # =========================================================
    # ORIENTACIÓN SEGÚN FASE
    # =========================================================

    def _compile_orientation_for_phase(
        self,
        orientation: Dict[str, Any],
        phase: str,
    ) -> Dict[str, Dict[str, Any]]:

        if not orientation:
            return {}

        if phase in (
            "start",
            "end",
        ):

            return self._create_neutral_orientation(
                orientation
            )

        return self._compile_orientation(
            orientation
        )

    # =========================================================
    # CREAR ORIENTACIÓN NEUTRA
    # =========================================================

    def _create_neutral_orientation(
        self,
        orientation: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:

        if not orientation:
            return {}

        result = {}

        # -----------------------------------------------------
        # DOS MANOS
        # -----------------------------------------------------

        if (
            "left" in orientation
            or "right" in orientation
        ):

            for side in (
                "left",
                "right",
            ):

                side_orientation = (
                    orientation.get(
                        side
                    )
                )

                if side_orientation is None:
                    continue

                result[
                    f"{side}_hand"
                ] = {
                    "rotation": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                }

            return result

        # -----------------------------------------------------
        # UNA MANO → DERECHA
        # -----------------------------------------------------

        return {
            "right_hand": {
                "rotation": [
                    0.0,
                    0.0,
                    0.0,
                ]
            }
        }

    # =========================================================
    # COMPILAR ORIENTACIÓN
    # =========================================================

    def _compile_orientation(
        self,
        orientation: Dict[str, Any],
    ) -> Dict[str, Dict[str, Any]]:

        if not orientation:
            return {}

        # -----------------------------------------------------
        # DOS MANOS
        # -----------------------------------------------------

        if (
            "left" in orientation
            or "right" in orientation
        ):

            result = {}

            for side in (
                "left",
                "right",
            ):

                side_orientation = (
                    orientation.get(
                        side
                    )
                )

                if not side_orientation:
                    continue

                compiled = (
                    self.hand_orientation_compiler
                    .compile_orientation(
                        side_orientation,
                        side,
                    )
                )

                result.update(
                    compiled
                )

            return result

        # -----------------------------------------------------
        # UNA MANO → DERECHA
        # -----------------------------------------------------

        return (
            self.hand_orientation_compiler
            .compile_orientation(
                orientation,
                "right",
            )
        )

    # =========================================================
    # LOCATION
    # =========================================================

    def _compile_location_for_phase(
        self,
        location: Dict[str, Any],
        phase: str,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Location permanece como información semántica.

        No genera directamente rotaciones.

        El movimiento espacial se procesa mediante:

            movement
              ↓
            trajectory
              ↓
            arm solver
        """

        return {}

    # =========================================================
    # NORMALIZAR HUESOS
    # =========================================================

    @staticmethod
    def _normalize_bones(
        bones: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Convierte nombres de huesos de KeyframeGenerator
        a nombres lógicos internos.
        """

        if not isinstance(
            bones,
            dict,
        ):
            return {}

        normalized = {}

        aliases = {
            # -------------------------------------------------
            # CUERPO
            # -------------------------------------------------

            "Hips": "hips",
            "Spine": "spine",
            "Spine1": "spine1",
            "Spine2": "spine2",
            "Neck": "neck",
            "Head": "head",

            # -------------------------------------------------
            # BRAZO IZQUIERDO
            # -------------------------------------------------

            "LeftShoulder": "left_shoulder",
            "LeftArm": "left_arm",
            "LeftForeArm": "left_forearm",
            "LeftHand": "left_hand",

            # -------------------------------------------------
            # BRAZO DERECHO
            # -------------------------------------------------

            "RightShoulder": "right_shoulder",
            "RightArm": "right_arm",
            "RightForeArm": "right_forearm",
            "RightHand": "right_hand",

            # -------------------------------------------------
            # DEDOS IZQUIERDOS
            # -------------------------------------------------

            "LeftHandThumb1": "left_thumb_1",
            "LeftHandThumb2": "left_thumb_2",
            "LeftHandThumb3": "left_thumb_3",

            "LeftHandIndex1": "left_index_1",
            "LeftHandIndex2": "left_index_2",
            "LeftHandIndex3": "left_index_3",

            "LeftHandMiddle1": "left_middle_1",
            "LeftHandMiddle2": "left_middle_2",
            "LeftHandMiddle3": "left_middle_3",

            "LeftHandRing1": "left_ring_1",
            "LeftHandRing2": "left_ring_2",
            "LeftHandRing3": "left_ring_3",

            "LeftHandPinky1": "left_pinky_1",
            "LeftHandPinky2": "left_pinky_2",
            "LeftHandPinky3": "left_pinky_3",

            # -------------------------------------------------
            # DEDOS DERECHOS
            # -------------------------------------------------

            "RightHandThumb1": "right_thumb_1",
            "RightHandThumb2": "right_thumb_2",
            "RightHandThumb3": "right_thumb_3",

            "RightHandIndex1": "right_index_1",
            "RightHandIndex2": "right_index_2",
            "RightHandIndex3": "right_index_3",

            "RightHandMiddle1": "right_middle_1",
            "RightHandMiddle2": "right_middle_2",
            "RightHandMiddle3": "right_middle_3",

            "RightHandRing1": "right_ring_1",
            "RightHandRing2": "right_ring_2",
            "RightHandRing3": "right_ring_3",

            "RightHandPinky1": "right_pinky_1",
            "RightHandPinky2": "right_pinky_2",
            "RightHandPinky3": "right_pinky_3",
        }

        for bone_name, transform in bones.items():

            logical_name = aliases.get(
                bone_name,
                str(
                    bone_name
                )
                .strip()
                .lower(),
            )

            if isinstance(
                transform,
                dict,
            ):

                normalized[
                    logical_name
                ] = dict(
                    transform
                )

        return normalized

    # =========================================================
    # DETECTAR FASE
    # =========================================================

    @staticmethod
    def _detect_phase(
        normalized_time: float,
    ) -> str:

        if normalized_time <= 0.0:
            return "start"

        if normalized_time >= 1.0:
            return "end"

        return "motion"


# =============================================================
# PRUEBA DIRECTA
# =============================================================

if __name__ == "__main__":

    generator = MotionGenerator()

    example_sign = {
        "concept": "SAVE",

        "duration": 0.8,

        # -----------------------------------------------------
        # MANO
        # -----------------------------------------------------

        "hand_shape": {
            "shape": "bent_fingers",

            "fingers": {
                "thumb": {
                    "opposition": 45,
                },

                "index": {
                    "flexion": 60,
                },

                "middle": {
                    "flexion": 50,
                },

                "ring": {
                    "flexion": 45,
                },

                "pinky": {
                    "flexion": 35,
                },
            },
        },

        # -----------------------------------------------------
        # ORIENTACIÓN
        # -----------------------------------------------------

        "orientation": {
            "palm": "left",
        },

        # -----------------------------------------------------
        # LOCATION
        # -----------------------------------------------------

        "location": {
            "body_region": "chest",
        },

        # -----------------------------------------------------
        # MOVIMIENTO
        # -----------------------------------------------------

        "movement": {
            "path": "pull_up",

            "duration": 0.8,
        },

        # -----------------------------------------------------
        # NON-MANUAL
        # -----------------------------------------------------

        "non_manual": {},
    }

    plan = generator.generate_motion(
        example_sign
    )

    print()
    print(
        "=== SIGNMUSIC MOTION GENERATOR ==="
    )

    print(
        "Concept:",
        plan.concept,
    )

    print(
        "Duration:",
        plan.duration,
    )

    print(
        "FPS:",
        plan.fps,
    )

    print(
        "Status:",
        plan.status,
    )

    print()
    print(
        "Keyframes:"
    )

    for keyframe in plan.keyframes:

        print()

        print(
            {
                "time": keyframe.time,
                "phase": keyframe.phase,
            }
        )

        for bone, transform in (
            keyframe.bones.items()
        ):

            print(
                f"  {bone}: {transform}"
            )

    print()
    print(
        "Compiled movement:"
    )

    print(
        plan.movement
    )

    print()

    print(
        "Validation:",
        plan.validate()
        or "OK",
    )