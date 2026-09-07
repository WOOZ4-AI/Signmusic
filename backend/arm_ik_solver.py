import math
from typing import Dict, Tuple


class ArmIKSolver:
    """
    Solver IK de dos segmentos.

    Esta versión es independiente de Blender.

    Recibe:
        - posición del hombro
        - longitud del brazo superior
        - longitud del antebrazo
        - objetivo 2D

    Devuelve:
        - ángulo del brazo
        - ángulo relativo del antebrazo
        - posición calculada de la muñeca
        - error final

    La implementación utiliza una solución geométrica
    de dos segmentos, que es más estable para una cadena
    simple de brazo + antebrazo.
    """

    def __init__(
        self,
        tolerance: float = 0.001,
    ):

        if tolerance <= 0:
            raise ValueError(
                "tolerance debe ser mayor que 0."
            )

        self.tolerance = float(
            tolerance
        )

    # =========================================================
    # DISTANCIA
    # =========================================================

    @staticmethod
    def distance(
        a: Tuple[float, float],
        b: Tuple[float, float],
    ) -> float:

        return math.sqrt(
            (
                a[0] - b[0]
            ) ** 2
            +
            (
                a[1] - b[1]
            ) ** 2
        )

    # =========================================================
    # FORWARD KINEMATICS
    # =========================================================

    @staticmethod
    def forward_kinematics(
        shoulder: Tuple[float, float],
        upper_length: float,
        forearm_length: float,
        arm_angle: float,
        forearm_angle: float,
    ) -> Tuple[float, float]:

        elbow_x = (
            shoulder[0]
            + upper_length
            * math.cos(
                arm_angle
            )
        )

        elbow_y = (
            shoulder[1]
            + upper_length
            * math.sin(
                arm_angle
            )
        )

        wrist_x = (
            elbow_x
            + forearm_length
            * math.cos(
                arm_angle
                + forearm_angle
            )
        )

        wrist_y = (
            elbow_y
            + forearm_length
            * math.sin(
                arm_angle
                + forearm_angle
            )
        )

        return (
            wrist_x,
            wrist_y,
        )

    # =========================================================
    # SOLVER GEOMÉTRICO
    # =========================================================

    def solve(
        self,
        shoulder: Tuple[float, float],
        upper_length: float,
        forearm_length: float,
        target: Tuple[float, float],
        elbow_up: bool = True,
    ) -> Dict[str, float]:

        upper_length = float(
            upper_length
        )

        forearm_length = float(
            forearm_length
        )

        if upper_length <= 0:
            raise ValueError(
                "upper_length debe ser mayor que 0."
            )

        if forearm_length <= 0:
            raise ValueError(
                "forearm_length debe ser mayor que 0."
            )

        sx = float(
            shoulder[0]
        )

        sy = float(
            shoulder[1]
        )

        tx = float(
            target[0]
        )

        ty = float(
            target[1]
        )

        dx = (
            tx - sx
        )

        dy = (
            ty - sy
        )

        distance_to_target = math.sqrt(
            dx * dx
            +
            dy * dy
        )

        if distance_to_target < 1e-9:

            raise ValueError(
                "El objetivo no puede coincidir "
                "exactamente con el hombro."
            )

        max_reach = (
            upper_length
            + forearm_length
        )

        min_reach = abs(
            upper_length
            - forearm_length
        )

        # -----------------------------------------------------
        # Ajustar objetivo si está fuera del alcance
        # -----------------------------------------------------

        effective_distance = distance_to_target

        if effective_distance > max_reach:

            effective_distance = max_reach

        if effective_distance < min_reach:

            effective_distance = min_reach

        scale = (
            effective_distance
            / distance_to_target
        )

        effective_x = (
            dx * scale
        )

        effective_y = (
            dy * scale
        )

        # -----------------------------------------------------
        # Ángulo del vector hombro → objetivo
        # -----------------------------------------------------

        base_angle = math.atan2(
            effective_y,
            effective_x,
        )

        # -----------------------------------------------------
        # Ley de cosenos
        # -----------------------------------------------------

        cos_shoulder = (
            (
                upper_length ** 2
                +
                effective_distance ** 2
                -
                forearm_length ** 2
            )
            /
            (
                2.0
                * upper_length
                * effective_distance
            )
        )

        cos_forearm = (
            (
                upper_length ** 2
                +
                forearm_length ** 2
                -
                effective_distance ** 2
            )
            /
            (
                2.0
                * upper_length
                * forearm_length
            )
        )

        # -----------------------------------------------------
        # Evitar errores numéricos
        # -----------------------------------------------------

        cos_shoulder = max(
            -1.0,
            min(
                1.0,
                cos_shoulder,
            ),
        )

        cos_forearm = max(
            -1.0,
            min(
                1.0,
                cos_forearm,
            ),
        )

        shoulder_offset = math.acos(
            cos_shoulder
        )

        elbow_angle = math.acos(
            cos_forearm
        )

        # -----------------------------------------------------
        # Configuración del codo
        # -----------------------------------------------------

        if elbow_up:

            arm_angle = (
                base_angle
                - shoulder_offset
            )

            total_forearm_angle = (
                base_angle
                + shoulder_offset
            )

        else:

            arm_angle = (
                base_angle
                + shoulder_offset
            )

            total_forearm_angle = (
                base_angle
                - shoulder_offset
            )

        # -----------------------------------------------------
        # Ángulo relativo del antebrazo
        # -----------------------------------------------------

        forearm_angle = (
            total_forearm_angle
            - arm_angle
        )

        # -----------------------------------------------------
        # Forward kinematics final
        # -----------------------------------------------------

        wrist = (
            self.forward_kinematics(
                shoulder=(
                    sx,
                    sy,
                ),
                upper_length=upper_length,
                forearm_length=forearm_length,
                arm_angle=arm_angle,
                forearm_angle=forearm_angle,
            )
        )

        actual_target = (
            tx,
            ty,
        )

        error = self.distance(
            wrist,
            actual_target,
        )

        # -----------------------------------------------------
        # Error respecto al objetivo efectivo
        # -----------------------------------------------------

        effective_target = (
            sx + effective_x,
            sy + effective_y,
        )

        effective_error = self.distance(
            wrist,
            effective_target,
        )

        return {
            "arm_angle": float(
                arm_angle
            ),

            "forearm_angle": float(
                forearm_angle
            ),

            "wrist_x": float(
                wrist[0]
            ),

            "wrist_y": float(
                wrist[1]
            ),

            "error": float(
                error
            ),

            "effective_error": float(
                effective_error
            ),

            "target_x": tx,
            "target_y": ty,

            "effective_target_x": (
                effective_target[0]
            ),

            "effective_target_y": (
                effective_target[1]
            ),
        }


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    solver = ArmIKSolver()

    print(
        "=== SIGNMUSIC ARM IK SOLVER ==="
    )

    shoulder = (
        0.0,
        0.0,
    )

    upper_length = 1.0

    forearm_length = 1.0

    targets = {
        "center": (
            0.0,
            1.5,
        ),

        "right": (
            1.2,
            0.8,
        ),

        "left": (
            -1.2,
            0.8,
        ),

        "lower": (
            0.0,
            -1.2,
        ),
    }

    for name, target in targets.items():

        result = solver.solve(
            shoulder=shoulder,
            upper_length=upper_length,
            forearm_length=forearm_length,
            target=target,
            elbow_up=True,
        )

        print()
        print(
            f"{name}:"
        )

        print(
            f"  target = {target}"
        )

        print(
            "  arm_angle = "
            f"{math.degrees(result['arm_angle']):.3f}°"
        )

        print(
            "  forearm_angle = "
            f"{math.degrees(result['forearm_angle']):.3f}°"
        )

        print(
            "  wrist = "
            f"({result['wrist_x']:.4f}, "
            f"{result['wrist_y']:.4f})"
        )

        print(
            "  error = "
            f"{result['error']:.6f}"
        )

        print(
            "  effective_error = "
            f"{result['effective_error']:.6f}"
        )

    print()
    print(
        "Status: OK"
    )