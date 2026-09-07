from typing import Any, Dict

from motion_plan import MotionPlan


class MotionCompiler:
    """
    Compilador de MotionPlan.

    Convierte un MotionPlan en una representación
    serializable y validada para el siguiente nivel
    del pipeline.

    Este módulo NO depende de Blender.
    """

    def compile(
        self,
        motion_plan: MotionPlan,
    ) -> Dict[str, Any]:

        if not isinstance(
            motion_plan,
            MotionPlan,
        ):
            raise TypeError(
                "motion_plan debe ser una instancia "
                "de MotionPlan."
            )

        self._validate_motion_plan(
            motion_plan
        )

        compiled_keyframes = []

        for keyframe in motion_plan.keyframes:

            compiled_keyframes.append(
                {
                    "time": float(
                        keyframe.time
                    ),
                    "phase": str(
                        keyframe.phase
                    ),
                    "bones": {
                        bone: dict(transform)
                        for bone, transform
                        in keyframe.bones.items()
                    },
                }
            )

        return {
            "concept": motion_plan.concept,
            "duration": float(
                motion_plan.duration
            ),
            "fps": int(
                motion_plan.fps
            ),

            "hand_shape": dict(
                motion_plan.hand_shape
            ),

            "orientation": dict(
                motion_plan.orientation
            ),

            "location": dict(
                motion_plan.location
            ),

            "movement": dict(
                motion_plan.movement
            ),

            "non_manual": dict(
                motion_plan.non_manual
            ),

            "keyframes": compiled_keyframes,

            "status": "compiled",
        }

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    def _validate_motion_plan(
        self,
        motion_plan: MotionPlan,
    ) -> None:

        if not isinstance(
            motion_plan.concept,
            str,
        ):
            raise TypeError(
                "concept debe ser un string."
            )

        if not motion_plan.concept.strip():
            raise ValueError(
                "concept no puede estar vacío."
            )

        if motion_plan.duration <= 0:
            raise ValueError(
                "duration debe ser mayor que 0."
            )

        if motion_plan.fps <= 0:
            raise ValueError(
                "fps debe ser mayor que 0."
            )

        if not motion_plan.keyframes:
            raise ValueError(
                "MotionPlan debe contener al menos "
                "un keyframe."
            )

        previous_time = -1.0

        for index, keyframe in enumerate(
            motion_plan.keyframes
        ):

            time = float(
                keyframe.time
            )

            if time < 0:
                raise ValueError(
                    f"El keyframe {index} tiene "
                    f"un tiempo negativo."
                )

            if time > motion_plan.duration:
                raise ValueError(
                    f"El keyframe {index} está fuera "
                    f"de la duración del movimiento."
                )

            if time < previous_time:
                raise ValueError(
                    "Los keyframes deben estar "
                    "ordenados cronológicamente."
                )

            if not isinstance(
                keyframe.bones,
                dict,
            ):
                raise TypeError(
                    f"bones del keyframe {index} "
                    f"debe ser un diccionario."
                )

            for bone, transform in (
                keyframe.bones.items()
            ):

                if not isinstance(
                    bone,
                    str,
                ):
                    raise TypeError(
                        "Los nombres de huesos "
                        "deben ser strings."
                    )

                if not isinstance(
                    transform,
                    dict,
                ):
                    raise TypeError(
                        f"La transformación del hueso "
                        f"{bone} debe ser un diccionario."
                    )

            previous_time = time


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    from motion_plan import MotionKeyframe

    plan = MotionPlan(
        concept="SAVE",
        duration=0.8,
        fps=25,
        keyframes=[
            MotionKeyframe(
                time=0.0,
                phase="start",
                bones={
                    "right_arm": {
                        "rotation": [
                            0.0,
                            0.0,
                            0.0,
                        ]
                    },
                    "right_hand": {
                        "rotation": [
                            0.0,
                            0.0,
                            0.0,
                        ]
                    },
                },
            ),

            MotionKeyframe(
                time=0.4,
                phase="motion",
                bones={
                    "right_arm": {
                        "rotation": [
                            25.0,
                            0.0,
                            0.0,
                        ]
                    },
                    "right_hand": {
                        "rotation": [
                            15.0,
                            0.0,
                            0.0,
                        ]
                    },
                },
            ),

            MotionKeyframe(
                time=0.8,
                phase="end",
                bones={
                    "right_arm": {
                        "rotation": [
                            0.0,
                            0.0,
                            0.0,
                        ]
                    },
                    "right_hand": {
                        "rotation": [
                            0.0,
                            0.0,
                            0.0,
                        ]
                    },
                },
            ),
        ],
    )

    compiler = MotionCompiler()

    result = compiler.compile(
        plan
    )

    print(
        "=== SIGNMUSIC MOTION COMPILER ==="
    )

    print(
        "Concept:",
        result["concept"],
    )

    print(
        "Duration:",
        result["duration"],
    )

    print(
        "FPS:",
        result["fps"],
    )

    print(
        "Status:",
        result["status"],
    )

    print(
        "Keyframes:",
        result["keyframes"],
    )