from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class MotionKeyframe:
    """
    Punto temporal dentro de un movimiento.

    Los nombres de los huesos son nombres lógicos
    de Signmusic, NO nombres específicos de Blender.
    """

    time: float
    phase: str

    bones: Dict[str, Dict[str, Any]] = field(
        default_factory=dict
    )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "time": self.time,
            "phase": self.phase,
            "bones": self.bones,
        }


@dataclass
class MotionPlan:
    """
    Representación intermedia de un signo animado.

    NO depende de Blender.

    Puede utilizarse posteriormente por:

        - Blender
        - WebGL
        - Three.js
        - Unity
        - otros renderizadores

    Los huesos utilizan nombres lógicos:

        right_arm
        left_arm
        right_hand
        left_hand

    El BoneMapper se encargará posteriormente
    de convertirlos al rig específico.
    """

    concept: str
    duration: float
    fps: int = 25

    hand_shape: Dict[str, Any] = field(
        default_factory=dict
    )

    orientation: Dict[str, Any] = field(
        default_factory=dict
    )

    location: Dict[str, Any] = field(
        default_factory=dict
    )

    movement: Dict[str, Any] = field(
        default_factory=dict
    )

    non_manual: Dict[str, Any] = field(
        default_factory=dict
    )

    keyframes: List[MotionKeyframe] = field(
        default_factory=list
    )

    status: str = "motion_defined"

    # =========================================================
    # AÑADIR KEYFRAME
    # =========================================================

    def add_keyframe(
        self,
        time: float,
        phase: str,
        bones: Dict[str, Dict[str, Any]] = None,
    ) -> None:
        """
        Añade un keyframe al plan.
        """

        self.keyframes.append(
            MotionKeyframe(
                time=float(time),
                phase=phase,
                bones=bones or {},
            )
        )

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    def validate(self) -> List[str]:
        """
        Valida la estructura básica del MotionPlan.
        """

        errors = []

        if not self.concept:
            errors.append(
                "El concepto es obligatorio."
            )

        if self.duration <= 0:
            errors.append(
                "La duración debe ser mayor que 0."
            )

        if self.fps <= 0:
            errors.append(
                "FPS debe ser mayor que 0."
            )

        if not self.keyframes:
            errors.append(
                "El MotionPlan debe contener "
                "al menos un keyframe."
            )

        for keyframe in self.keyframes:

            if keyframe.time < 0:
                errors.append(
                    f"Keyframe con tiempo inválido: "
                    f"{keyframe.time}"
                )

            if keyframe.time > self.duration:
                errors.append(
                    f"Keyframe fuera de duración: "
                    f"{keyframe.time}"
                )

            if not keyframe.phase:
                errors.append(
                    "Un keyframe debe tener phase."
                )

        return errors

    # =========================================================
    # SERIALIZACIÓN
    # =========================================================

    def to_dict(self) -> Dict[str, Any]:
        """
        Convierte el MotionPlan a un diccionario
        serializable.
        """

        return {
            "concept": self.concept,
            "duration": self.duration,
            "fps": self.fps,

            "hand_shape": self.hand_shape,
            "orientation": self.orientation,
            "location": self.location,
            "movement": self.movement,
            "non_manual": self.non_manual,

            "keyframes": [
                keyframe.to_dict()
                for keyframe in self.keyframes
            ],

            "status": self.status,
        }


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    plan = MotionPlan(
        concept="SAVE",
        duration=0.8,
    )

    plan.add_keyframe(
        time=0.0,
        phase="start",
        bones={
            "right_arm": {
                "rotation": [0.0, 0.0, 0.0],
            },
            "right_hand": {
                "rotation": [0.0, 0.0, 0.0],
            },
        },
    )

    plan.add_keyframe(
        time=0.4,
        phase="motion",
        bones={
            "right_arm": {
                "rotation": [25.0, 0.0, 0.0],
            },
            "right_hand": {
                "rotation": [15.0, 0.0, 0.0],
            },
        },
    )

    plan.add_keyframe(
        time=0.8,
        phase="end",
        bones={
            "right_arm": {
                "rotation": [0.0, 0.0, 0.0],
            },
            "right_hand": {
                "rotation": [0.0, 0.0, 0.0],
            },
        },
    )

    print(
        "=== SIGNMUSIC MOTION PLAN ==="
    )

    print(
        plan.to_dict()
    )

    print(
        "\nValidation:",
        plan.validate()
        or "OK",
    )