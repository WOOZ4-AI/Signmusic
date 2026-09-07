import math
from typing import Dict, Tuple


class MixamoArmIK:
    """
    Adaptador de cinemática inversa para el brazo derecho
    del avatar Mixamo utilizado por Signmusic.

    Este módulo es independiente de Blender.

    Trabaja con cuatro grados de libertad conceptuales:

        arm_x
        arm_z
        forearm_x
        forearm_z

    Estos grados de libertad fueron seleccionados a partir
    de la calibración experimental del avatar.

    IMPORTANTE:

    Los valores de calibración NO son datos lingüísticos.
    Son parámetros técnicos del avatar.
    """

    # =========================================================
    # CONFIGURACIÓN
    # =========================================================

    DEFAULT_STEP_DEGREES = 2.0

    DEFAULT_MAX_ITERATIONS = 250

    DEFAULT_TOLERANCE = 0.002

    # =========================================================
    # CONSTRUCTOR
    # =========================================================

    def __init__(
        self,
        step_degrees: float = DEFAULT_STEP_DEGREES,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        tolerance: float = DEFAULT_TOLERANCE,
    ):
        if step_degrees <= 0:
            raise ValueError(
                "step_degrees debe ser mayor que 0."
            )

        if max_iterations <= 0:
            raise ValueError(
                "max_iterations debe ser mayor que 0."
            )

        if tolerance <= 0:
            raise ValueError(
                "tolerance debe ser mayor que 0."
            )

        self.step_degrees = float(
            step_degrees
        )

        self.max_iterations = int(
            max_iterations
        )

        self.tolerance = float(
            tolerance
        )

    # =========================================================
    # DISTANCIA 3D
    # =========================================================

    @staticmethod
    def distance_3d(
        a: Tuple[float, float, float],
        b: Tuple[float, float, float],
    ) -> float:

        dx = (
            float(a[0])
            - float(b[0])
        )

        dy = (
            float(a[1])
            - float(b[1])
        )

        dz = (
            float(a[2])
            - float(b[2])
        )

        return math.sqrt(
            dx * dx
            + dy * dy
            + dz * dz
        )

    # =========================================================
    # VECTOR DE ERROR
    # =========================================================

    @staticmethod
    def error_vector(
        actual: Tuple[float, float, float],
        target: Tuple[float, float, float],
    ) -> Tuple[float, float, float]:

        return (
            float(target[0])
            - float(actual[0]),
            float(target[1])
            - float(actual[1]),
            float(target[2])
            - float(actual[2]),
        )

    # =========================================================
    # SOLVER NUMÉRICO GENÉRICO
    # =========================================================

    def solve(
        self,
        forward_function,
        target: Tuple[float, float, float],
        initial: Dict[str, float] | None = None,
    ) -> Dict[str, float]:
        """
        Busca iterativamente los cuatro ángulos
        que minimizan la distancia entre la posición
        generada y el objetivo.

        forward_function recibe:

            arm_x
            arm_z
            forearm_x
            forearm_z

        y debe devolver:

            (x, y, z)
        """

        if initial is None:
            angles = {
                "arm_x": 0.0,
                "arm_z": 0.0,
                "forearm_x": 0.0,
                "forearm_z": 0.0,
            }

        else:
            angles = {
                "arm_x": float(
                    initial.get(
                        "arm_x",
                        0.0,
                    )
                ),

                "arm_z": float(
                    initial.get(
                        "arm_z",
                        0.0,
                    )
                ),

                "forearm_x": float(
                    initial.get(
                        "forearm_x",
                        0.0,
                    )
                ),

                "forearm_z": float(
                    initial.get(
                        "forearm_z",
                        0.0,
                    )
                ),
            }

        angle_names = (
            "arm_x",
            "arm_z",
            "forearm_x",
            "forearm_z",
        )

        for _ in range(
            self.max_iterations
        ):

            current = forward_function(
                angles["arm_x"],
                angles["arm_z"],
                angles["forearm_x"],
                angles["forearm_z"],
            )

            current_error = (
                self.distance_3d(
                    current,
                    target,
                )
            )

            if current_error <= (
                self.tolerance
            ):
                break

            improved = False

            # -------------------------------------------------
            # Buscar mejora por cada DOF
            # -------------------------------------------------

            for angle_name in angle_names:

                original = angles[
                    angle_name
                ]

                candidates = (
                    original
                    + self.step_degrees,
                    original
                    - self.step_degrees,
                )

                best_angle = original

                best_error = current_error

                for candidate in candidates:

                    angles[
                        angle_name
                    ] = candidate

                    candidate_position = (
                        forward_function(
                            angles["arm_x"],
                            angles["arm_z"],
                            angles["forearm_x"],
                            angles["forearm_z"],
                        )
                    )

                    candidate_error = (
                        self.distance_3d(
                            candidate_position,
                            target,
                        )
                    )

                    if candidate_error < best_error:

                        best_error = (
                            candidate_error
                        )

                        best_angle = (
                            candidate
                        )

                angles[
                    angle_name
                ] = best_angle

                if best_error < (
                    current_error
                ):
                    current_error = (
                        best_error
                    )

                    improved = True

            if not improved:
                break

        final_position = forward_function(
            angles["arm_x"],
            angles["arm_z"],
            angles["forearm_x"],
            angles["forearm_z"],
        )

        final_error = (
            self.distance_3d(
                final_position,
                target,
            )
        )

        result = {
            **angles,

            "position_x": float(
                final_position[0]
            ),

            "position_y": float(
                final_position[1]
            ),

            "position_z": float(
                final_position[2]
            ),

            "error": float(
                final_error
            ),

            "iterations": (
                self.max_iterations
            ),
        }

        return result

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    def is_good_solution(
        self,
        result: Dict[str, float],
    ) -> bool:

        return (
            float(
                result.get(
                    "error",
                    float("inf"),
                )
            )
            <= self.tolerance
        )


# =============================================================
# PRUEBA MATEMÁTICA
# =============================================================

if __name__ == "__main__":

    solver = MixamoArmIK()

    print(
        "=== SIGNMUSIC MIXAMO ARM IK ==="
    )

    # ---------------------------------------------------------
    # Forward model artificial para probar el solver.
    #
    # Esto NO es todavía el modelo del avatar.
    # ---------------------------------------------------------

    base = (
        -0.694436,
        0.045161,
        1.426433,
    )

    def forward(
        arm_x,
        arm_z,
        forearm_x,
        forearm_z,
    ):

        # Sensibilidad aproximada derivada de nuestras
        # mediciones experimentales.

        x = (
            base[0]
            + (
                arm_x
                + forearm_x
            )
            * 0.0015
            + (
                arm_z
                + forearm_z
            )
            * 0.0015
        )

        y = (
            base[1]
            + (
                arm_z
                + forearm_z
            )
            * 0.0080
        )

        z = (
            base[2]
            - (
                arm_x
                + forearm_x
            )
            * 0.0080
        )

        return (
            x,
            y,
            z,
        )

    targets = {
        "center": (
            base[0],
            base[1],
            base[2],
        ),

        "lower": (
            base[0],
            base[1],
            base[2] - 0.10,
        ),

        "side": (
            base[0],
            base[1] + 0.10,
            base[2],
        ),
    }

    for name, target in (
        targets.items()
    ):

        result = solver.solve(
            forward_function=forward,
            target=target,
        )

        print()

        print(
            f"{name}:"
        )

        print(
            "  target =",
            target,
        )

        print(
            "  angles =",
            {
                key: round(
                    value,
                    3,
                )
                for key, value
                in result.items()
                if key in {
                    "arm_x",
                    "arm_z",
                    "forearm_x",
                    "forearm_z",
                }
            },
        )

        print(
            "  position =",
            (
                round(
                    result["position_x"],
                    6,
                ),
                round(
                    result["position_y"],
                    6,
                ),
                round(
                    result["position_z"],
                    6,
                ),
            ),
        )

        print(
            "  error =",
            f"{result['error']:.6f}",
        )

    print()
    print(
        "Status: OK"
    )