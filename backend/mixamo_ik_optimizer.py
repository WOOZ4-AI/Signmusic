import math
from typing import Any, Callable, Dict, Iterable, Tuple


class MixamoIKOptimizer:
    """
    Optimizador numérico para encontrar las rotaciones de:

        arm_x
        arm_z
        forearm_x
        forearm_z

    que minimizan la distancia entre la mano actual
    y una posición objetivo.

    No depende de Blender.

    Blender proporciona el forward_function():

        ángulos
            ↓
        posición real de la mano
    """

    ANGLES = (
        "arm_x",
        "arm_z",
        "forearm_x",
        "forearm_z",
    )

    DEFAULT_TOLERANCE = 0.003

    DEFAULT_MAX_ITERATIONS = 250

    DEFAULT_STEPS = (
        10.0,
        5.0,
        2.0,
        1.0,
        0.5,
        0.25,
        0.1,
    )

    DEFAULT_STARTS = (
        {
            "arm_x": 0.0,
            "arm_z": 0.0,
            "forearm_x": 0.0,
            "forearm_z": 0.0,
        },
        {
            "arm_x": 10.0,
            "arm_z": 0.0,
            "forearm_x": 5.0,
            "forearm_z": 0.0,
        },
        {
            "arm_x": -10.0,
            "arm_z": 0.0,
            "forearm_x": -5.0,
            "forearm_z": 0.0,
        },
        {
            "arm_x": 0.0,
            "arm_z": 10.0,
            "forearm_x": 0.0,
            "forearm_z": 5.0,
        },
        {
            "arm_x": 0.0,
            "arm_z": -10.0,
            "forearm_x": 0.0,
            "forearm_z": -5.0,
        },
    )

    DEFAULT_LIMITS = {
        "arm_x": (-90.0, 90.0),
        "arm_z": (-90.0, 90.0),
        "forearm_x": (-120.0, 120.0),
        "forearm_z": (-120.0, 120.0),
    }

    def __init__(
        self,
        tolerance: float = DEFAULT_TOLERANCE,
        max_iterations: int = DEFAULT_MAX_ITERATIONS,
        steps: Iterable[float] = DEFAULT_STEPS,
        starts: Iterable[Dict[str, float]] = DEFAULT_STARTS,
        limits: Dict[str, Tuple[float, float]] | None = None,
    ):
        if tolerance <= 0:
            raise ValueError(
                "tolerance debe ser mayor que 0."
            )

        if max_iterations <= 0:
            raise ValueError(
                "max_iterations debe ser mayor que 0."
            )

        self.tolerance = float(
            tolerance
        )

        self.max_iterations = int(
            max_iterations
        )

        self.steps = tuple(
            float(step)
            for step in steps
        )

        if not self.steps:
            raise ValueError(
                "Debe existir al menos un step."
            )

        self.starts = tuple(
            dict(start)
            for start in starts
        )

        if not self.starts:
            raise ValueError(
                "Debe existir al menos un punto inicial."
            )

        self.limits = (
            dict(limits)
            if limits is not None
            else dict(
                self.DEFAULT_LIMITS
            )
        )

    # =========================================================
    # UTILIDADES
    # =========================================================

    @staticmethod
    def distance(
        a,
        b,
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

    def normalize_angles(
        self,
        angles: Dict[str, float],
    ) -> Dict[str, float]:

        result = {}

        for name in self.ANGLES:

            value = float(
                angles.get(
                    name,
                    0.0,
                )
            )

            lower, upper = self.limits[
                name
            ]

            value = max(
                lower,
                min(
                    upper,
                    value,
                ),
            )

            result[name] = value

        return result

    # =========================================================
    # EVALUACIÓN
    # =========================================================

    def evaluate(
        self,
        forward_function: Callable[
            [float, float, float, float],
            Tuple[float, float, float],
        ],
        target,
        angles,
    ):

        normalized = (
            self.normalize_angles(
                angles
            )
        )

        position = forward_function(
            normalized["arm_x"],
            normalized["arm_z"],
            normalized["forearm_x"],
            normalized["forearm_z"],
        )

        error = self.distance(
            position,
            target,
        )

        return (
            normalized,
            position,
            error,
        )

    # =========================================================
    # BÚSQUEDA LOCAL
    # =========================================================

    def local_search(
        self,
        forward_function,
        target,
        initial,
    ):

        current = (
            self.normalize_angles(
                initial
            )
        )

        (
            current,
            position,
            error,
        ) = self.evaluate(
            forward_function,
            target,
            current,
        )

        iterations = 0

        for step in self.steps:

            improved = True

            while (
                improved
                and iterations
                < self.max_iterations
            ):

                improved = False

                for name in self.ANGLES:

                    original = current[
                        name
                    ]

                    candidates = (
                        original - step,
                        original + step,
                    )

                    best_angles = (
                        dict(current)
                    )

                    best_error = error

                    for candidate in candidates:

                        trial = dict(
                            current
                        )

                        trial[name] = (
                            candidate
                        )

                        (
                            trial,
                            trial_position,
                            trial_error,
                        ) = self.evaluate(
                            forward_function,
                            target,
                            trial,
                        )

                        iterations += 1

                        if (
                            trial_error
                            < best_error
                        ):

                            best_angles = (
                                trial
                            )

                            best_error = (
                                trial_error
                            )

                            best_position = (
                                trial_position
                            )

                    if best_error < error:

                        current = (
                            best_angles
                        )

                        error = (
                            best_error
                        )

                        position = (
                            best_position
                        )

                        improved = True

                        if error <= (
                            self.tolerance
                        ):
                            break

                if error <= (
                    self.tolerance
                ):
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

            "error": float(
                error
            ),

            "iterations": int(
                iterations
            ),
        }

    # =========================================================
    # MULTI-START
    # =========================================================

    def solve(
        self,
        forward_function,
        target,
        initial: Dict[str, float] | None = None,
    ) -> Dict[str, Any]:
        """
        Ejecuta múltiples búsquedas locales y conserva
        la solución con menor error.
        """

        starts = []

        if initial is not None:

            starts.append(
                dict(initial)
            )

        starts.extend(
            dict(start)
            for start in self.starts
        )

        best_result = None

        for start in starts:

            result = (
                self.local_search(
                    forward_function,
                    target,
                    start,
                )
            )

            if (
                best_result is None
                or result["error"]
                < best_result["error"]
            ):

                best_result = result

            if result["error"] <= (
                self.tolerance
            ):
                break

        if best_result is None:
            raise RuntimeError(
                "No se obtuvo ninguna solución."
            )

        best_result[
            "success"
        ] = (
            best_result["error"]
            <= self.tolerance
        )

        best_result[
            "target"
        ] = [
            float(
                target[0]
            ),
            float(
                target[1]
            ),
            float(
                target[2]
            ),
        ]

        return best_result

    # =========================================================
    # VALIDAR
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
        "=== SIGNMUSIC MIXAMO IK OPTIMIZER ==="
    )

    base = (
        -0.694436,
        0.045161,
        1.426433,
    )

    # ---------------------------------------------------------
    # Modelo de prueba.
    #
    # NO es Blender.
    # Solo comprueba que el optimizador puede escapar
    # de una mala posición inicial mediante multi-start.
    # ---------------------------------------------------------

    def forward(
        arm_x,
        arm_z,
        forearm_x,
        forearm_z,
    ):

        x = (
            base[0]
            + arm_x * 0.0015
            + forearm_x * 0.0010
            + arm_z * 0.0015
            + forearm_z * 0.0010
        )

        y = (
            base[1]
            + arm_z * 0.0080
            + forearm_z * 0.0040
        )

        z = (
            base[2]
            - arm_x * 0.0080
            - forearm_x * 0.0040
        )

        return (
            x,
            y,
            z,
        )

    optimizer = MixamoIKOptimizer(
        tolerance=0.001,
    )

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

    for name, target in (
        targets.items()
    ):

        result = optimizer.solve(
            forward_function=forward,
            target=target,
        )

        print()
        print(
            f"{name}:"
        )

        print(
            "  angles:"
        )

        print(
            f"    arm_x = "
            f"{result['arm_x']:.3f}°"
        )

        print(
            f"    arm_z = "
            f"{result['arm_z']:.3f}°"
        )

        print(
            f"    forearm_x = "
            f"{result['forearm_x']:.3f}°"
        )

        print(
            f"    forearm_z = "
            f"{result['forearm_z']:.3f}°"
        )

        print(
            "  position:",
            result["position"],
        )

        print(
            "  error:",
            f"{result['error']:.6f}",
        )

        print(
            "  success:",
            result["success"],
        )

    print()
    print(
        "Status: OK"
    )