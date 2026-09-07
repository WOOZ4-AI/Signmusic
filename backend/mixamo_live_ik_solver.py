from typing import Any, Callable, Dict, Tuple


class MixamoLiveIKSolver:
    """
    Solver de IK numérico pensado para trabajar con el avatar Mixamo
    real dentro de Blender.

    Este módulo NO importa bpy.

    Blender será responsable de proporcionar una función que:

        ángulos
            ↓
        posición real de la mano

    El solver hará:

        objetivo
            ↓
        buscar ángulos
            ↓
        minimizar error
    """

    ANGLE_NAMES = (
        "arm_x",
        "arm_z",
        "forearm_x",
        "forearm_z",
    )

    DEFAULT_STEP_DEGREES = 5.0
    DEFAULT_REFINEMENT_STEP = 1.0

    DEFAULT_MAX_ITERATIONS = 100

    DEFAULT_TOLERANCE = 0.005

    def __init__(
        self,
        step_degrees: float = DEFAULT_STEP_DEGREES,
        refinement_step: float = DEFAULT_REFINEMENT_STEP,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        tolerance: float = DEFAULT_TOLERANCE,
    ):
        if step_degrees <= 0:
            raise ValueError(
                "step_degrees debe ser mayor que 0."
            )

        if refinement_step <= 0:
            raise ValueError(
                "refinement_step debe ser mayor que 0."
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

        self.refinement_step = float(
            refinement_step
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
    def distance(
        a: Tuple[float, float, float],
        b: Tuple[float, float, float],
    ) -> float:

        dx = float(
            a[0]
        ) - float(
            b[0]
        )

        dy = float(
            a[1]
        ) - float(
            b[1]
        )

        dz = float(
            a[2]
        ) - float(
            b[2]
        )

        return (
            dx * dx
            + dy * dy
            + dz * dz
        ) ** 0.5

    # =========================================================
    # COPIAR SOLUCIÓN
    # =========================================================

    @staticmethod
    def _copy_solution(
        values: Dict[str, float],
    ) -> Dict[str, float]:

        return {
            "arm_x": float(
                values.get(
                    "arm_x",
                    0.0,
                )
            ),

            "arm_z": float(
                values.get(
                    "arm_z",
                    0.0,
                )
            ),

            "forearm_x": float(
                values.get(
                    "forearm_x",
                    0.0,
                )
            ),

            "forearm_z": float(
                values.get(
                    "forearm_z",
                    0.0,
                )
            ),
        }

    # =========================================================
    # EVALUAR
    # =========================================================

    def _evaluate(
        self,
        forward_function: Callable[
            [float, float, float, float],
            Tuple[float, float, float],
        ],
        angles: Dict[str, float],
        target: Tuple[float, float, float],
    ) -> Tuple[
        Tuple[float, float, float],
        float,
    ]:

        position = forward_function(
            angles["arm_x"],
            angles["arm_z"],
            angles["forearm_x"],
            angles["forearm_z"],
        )

        error = self.distance(
            position,
            target,
        )

        return (
            position,
            error,
        )

    # =========================================================
    # BÚSQUEDA LOCAL
    # =========================================================

    def _search_step(
        self,
        forward_function,
        target,
        current,
        step,
    ):

        best = self._copy_solution(
            current
        )

        _, best_error = self._evaluate(
            forward_function,
            best,
            target,
        )

        improved = False

        for angle_name in self.ANGLE_NAMES:

            original = best[
                angle_name
            ]

            candidates = (
                original - step,
                original + step,
            )

            for candidate in candidates:

                trial = dict(
                    best
                )

                trial[
                    angle_name
                ] = candidate

                _, error = self._evaluate(
                    forward_function,
                    trial,
                    target,
                )

                if error < best_error:

                    best = trial

                    best_error = error

                    improved = True

        return (
            best,
            best_error,
            improved,
        )

    # =========================================================
    # SOLVER
    # =========================================================

    def solve(
        self,
        forward_function: Callable[
            [float, float, float, float],
            Tuple[float, float, float],
        ],
        target: Tuple[float, float, float],
        initial: Dict[str, float] | None = None,
    ) -> Dict[str, Any]:
        """
        Busca una combinación de cuatro ángulos:

            arm_x
            arm_z
            forearm_x
            forearm_z

        que aproxime la posición objetivo.
        """

        if initial is None:

            current = {
                "arm_x": 0.0,
                "arm_z": 0.0,
                "forearm_x": 0.0,
                "forearm_z": 0.0,
            }

        else:

            current = (
                self._copy_solution(
                    initial
                )
            )

        position, error = self._evaluate(
            forward_function,
            current,
            target,
        )

        iterations = 0

        step = self.step_degrees

        # -----------------------------------------------------
        # Refinamiento iterativo
        # -----------------------------------------------------

        while (
            iterations
            < self.max_iterations
        ):

            iterations += 1

            candidate, candidate_error, improved = (
                self._search_step(
                    forward_function,
                    target,
                    current,
                    step,
                )
            )

            if candidate_error < error:

                current = candidate

                error = candidate_error

                position, _ = self._evaluate(
                    forward_function,
                    current,
                    target,
                )

                if error <= self.tolerance:
                    break

            else:

                # -------------------------------------------------
                # Reducir el paso
                # -------------------------------------------------

                if step > self.refinement_step:

                    step = max(
                        self.refinement_step,
                        step / 2.0,
                    )

                else:

                    break

        return {
            **current,

            "position": [
                float(
                    position[0]
                ),
                float(
                    position[1]
                ),
                float(
                    position[2]
                ),
            ],

            "target": [
                float(
                    target[0]
                ),
                float(
                    target[1]
                ),
                float(
                    target[2]
                ),
            ],

            "error": float(
                error
            ),

            "iterations": iterations,

            "success": (
                error
                <= self.tolerance
            ),
        }

    # =========================================================
    # VALIDAR SOLUCIÓN
    # =========================================================

    def validate_solution(
        self,
        result: Dict[str, Any],
    ) -> bool:

        required = (
            "arm_x",
            "arm_z",
            "forearm_x",
            "forearm_z",
            "position",
            "target",
            "error",
        )

        for key in required:

            if key not in result:
                return False

        return (
            float(
                result["error"]
            )
            <= self.tolerance
        )


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    print(
        "=== SIGNMUSIC MIXAMO LIVE IK SOLVER ==="
    )

    solver = MixamoLiveIKSolver(
        step_degrees=5.0,
        refinement_step=0.5,
        max_iterations=100,
        tolerance=0.001,
    )

    base = (
        -0.694436,
        0.045161,
        1.426433,
    )

    # ---------------------------------------------------------
    # Modelo experimental basado en las mediciones reales
    # del avatar.
    #
    # NO es todavía Blender.
    # Sirve únicamente para comprobar la lógica del solver.
    # ---------------------------------------------------------

    def forward(
        arm_x,
        arm_z,
        forearm_x,
        forearm_z,
    ):

        x = (
            base[0]
            + (
                arm_x
                * 0.0015
            )
            + (
                forearm_x
                * 0.0010
            )
            + (
                arm_z
                * 0.0015
            )
            + (
                forearm_z
                * 0.0010
            )
        )

        y = (
            base[1]
            + (
                arm_z
                * 0.0080
            )
            + (
                forearm_z
                * 0.0040
            )
        )

        z = (
            base[2]
            - (
                arm_x
                * 0.0080
            )
            - (
                forearm_x
                * 0.0040
            )
        )

        return (
            x,
            y,
            z,
        )

    # ---------------------------------------------------------
    # Objetivos
    # ---------------------------------------------------------

    targets = {
        "neutral": base,

        "lower": (
            base[0],
            base[1],
            base[2] - 0.08,
        ),

        "side": (
            base[0],
            base[1] + 0.08,
            base[2],
        ),
    }

    for name, target in targets.items():

        result = solver.solve(
            forward_function=forward,
            target=target,
        )

        print()
        print(
            f"{name}:"
        )

        print(
            f"  Target: {target}"
        )

        print(
            "  Angles:"
        )

        print(
            f"    arm_x      = "
            f"{result['arm_x']:.3f}°"
        )

        print(
            f"    arm_z      = "
            f"{result['arm_z']:.3f}°"
        )

        print(
            f"    forearm_x  = "
            f"{result['forearm_x']:.3f}°"
        )

        print(
            f"    forearm_z  = "
            f"{result['forearm_z']:.3f}°"
        )

        print(
            "  Position:",
            result["position"],
        )

        print(
            "  Error:",
            f"{result['error']:.6f}",
        )

        print(
            "  Success:",
            result["success"],
        )

    print()
    print(
        "Status: OK"
    )