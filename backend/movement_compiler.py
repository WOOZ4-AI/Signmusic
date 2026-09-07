from typing import Any, Dict, List


class MovementCompiler:
    """
    Compilador de movimientos espaciales para Signmusic.

    Convierte una descripción conceptual de movimiento
    en una secuencia intermedia de puntos espaciales.

    Esta clase NO depende de Blender.

    Flujo:

        movimiento conceptual
                ↓
        trayectoria espacial
                ↓
        puntos temporales
                ↓
        ArmTrajectoryCompiler
                ↓
        ArmMotionSolver / IK
                ↓
        avatar

    IMPORTANTE:

    Los movimientos definidos aquí son estructuras
    experimentales del motor.

    NO representan movimientos lingüísticos
    verificados de DGS, ASL u otra lengua de signos.
    """

    # =========================================================
    # TRAYECTORIAS EXPERIMENTALES
    # =========================================================

    MOVEMENTS = {

        # -----------------------------------------------------
        # SIN MOVIMIENTO
        # -----------------------------------------------------

        "none": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
            ]
        },

        # -----------------------------------------------------
        # VERTICAL
        # -----------------------------------------------------

        "down": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
                {
                    "position": [
                        0.0,
                        -1.0,
                        0.0,
                    ]
                },
            ]
        },

        "up": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
                {
                    "position": [
                        0.0,
                        1.0,
                        0.0,
                    ]
                },
            ]
        },

        # -----------------------------------------------------
        # PROFUNDIDAD
        # -----------------------------------------------------

        "forward": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
                {
                    "position": [
                        0.0,
                        0.0,
                        1.0,
                    ]
                },
            ]
        },

        "backward": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
                {
                    "position": [
                        0.0,
                        0.0,
                        -1.0,
                    ]
                },
            ]
        },

        # -----------------------------------------------------
        # LATERAL
        # -----------------------------------------------------

        "left": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
                {
                    "position": [
                        -1.0,
                        0.0,
                        0.0,
                    ]
                },
            ]
        },

        "right": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
                {
                    "position": [
                        1.0,
                        0.0,
                        0.0,
                    ]
                },
            ]
        },

        # -----------------------------------------------------
        # TRANSICIONES
        # -----------------------------------------------------

        "front_to_center": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        1.0,
                    ]
                },
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
            ]
        },

        "center_to_upper": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
                {
                    "position": [
                        0.0,
                        1.0,
                        0.0,
                    ]
                },
            ]
        },

        # =====================================================
        # MOVIMIENTOS SEMÁNTICOS EXPERIMENTALES
        # =====================================================

        # -----------------------------------------------------
        # PULL UP
        # -----------------------------------------------------

        "pull_up": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
                {
                    "position": [
                        0.0,
                        0.35,
                        0.0,
                    ]
                },
                {
                    "position": [
                        0.0,
                        0.75,
                        0.0,
                    ]
                },
                {
                    "position": [
                        0.0,
                        1.0,
                        0.0,
                    ]
                },
            ]
        },

        # -----------------------------------------------------
        # POINT TO SELF
        # -----------------------------------------------------

        "point_to_self": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.8,
                    ]
                },
                {
                    "position": [
                        0.0,
                        0.0,
                        0.35,
                    ]
                },
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
            ]
        },

        # -----------------------------------------------------
        # POINT FORWARD
        # -----------------------------------------------------

        "point_forward": {
            "path": [
                {
                    "position": [
                        0.0,
                        0.0,
                        0.0,
                    ]
                },
                {
                    "position": [
                        0.0,
                        0.0,
                        0.5,
                    ]
                },
                {
                    "position": [
                        0.0,
                        0.0,
                        1.0,
                    ]
                },
            ]
        },
    }

    # =========================================================
    # ALIAS
    # =========================================================

    ALIASES = {

        # -----------------------------------------------------
        # NONE
        # -----------------------------------------------------

        "none": "none",
        "neutral": "none",
        "static": "none",

        # -----------------------------------------------------
        # DOWN
        # -----------------------------------------------------

        "down": "down",
        "downward": "down",

        # -----------------------------------------------------
        # UP
        # -----------------------------------------------------

        "up": "up",
        "upward": "up",

        # -----------------------------------------------------
        # FORWARD
        # -----------------------------------------------------

        "forward": "forward",
        "front": "forward",

        # -----------------------------------------------------
        # BACKWARD
        # -----------------------------------------------------

        "backward": "backward",
        "back": "backward",

        # -----------------------------------------------------
        # LEFT
        # -----------------------------------------------------

        "left": "left",

        # -----------------------------------------------------
        # RIGHT
        # -----------------------------------------------------

        "right": "right",

        # -----------------------------------------------------
        # TRANSITIONS
        # -----------------------------------------------------

        "front_to_center": (
            "front_to_center"
        ),

        "center_to_upper": (
            "center_to_upper"
        ),

        # -----------------------------------------------------
        # SEMANTIC MOVEMENTS
        # -----------------------------------------------------

        "pull_up": "pull_up",
        "pullup": "pull_up",
        "pull_upward": "pull_up",

        "point_to_self": (
            "point_to_self"
        ),

        "point_self": (
            "point_to_self"
        ),

        "point_forward": (
            "point_forward"
        ),

        "point_to_other": (
            "point_forward"
        ),
    }

    # =========================================================
    # COMPILAR MOVIMIENTO
    # =========================================================

    def compile_movement(
        self,
        movement: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Compila un movimiento conceptual.

        Entrada:

            {
                "path": "up"
            }

        Salida:

            {
                "path": "up",
                "points": [...]
            }
        """

        if not isinstance(
            movement,
            dict,
        ):
            raise TypeError(
                "movement debe ser un diccionario."
            )

        path_name = movement.get(
            "path",
            movement.get(
                "type",
                "none",
            ),
        )

        path_name = str(
            path_name
        ).strip().lower()

        normalized = self.ALIASES.get(
            path_name,
            path_name,
        )

        if normalized not in self.MOVEMENTS:

            raise ValueError(
                f"Movimiento no soportado: "
                f"{path_name}"
            )

        definition = self.MOVEMENTS[
            normalized
        ]

        points = [
            {
                "position": list(
                    point["position"]
                )
            }
            for point
            in definition["path"]
        ]

        result = {
            "path": normalized,

            "points": points,
        }

        # -----------------------------------------------------
        # Duración opcional
        # -----------------------------------------------------

        if "duration" in movement:

            duration = float(
                movement[
                    "duration"
                ]
            )

            if duration <= 0:

                raise ValueError(
                    "La duración del movimiento "
                    "debe ser mayor que 0."
                )

            result[
                "duration"
            ] = duration

        return result

    # =========================================================
    # OBTENER PUNTOS
    # =========================================================

    def get_points(
        self,
        movement: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Devuelve únicamente los puntos
        del movimiento compilado.
        """

        compiled = (
            self.compile_movement(
                movement
            )
        )

        return compiled[
            "points"
        ]

    # =========================================================
    # SOPORTE
    # =========================================================

    def get_supported_movements(
        self,
    ) -> List[str]:
        """
        Devuelve los movimientos soportados.
        """

        return sorted(
            self.MOVEMENTS.keys()
        )

    def is_supported(
        self,
        movement: str,
    ) -> bool:
        """
        Comprueba si un movimiento está soportado.
        """

        if not isinstance(
            movement,
            str,
        ):
            return False

        normalized = self.ALIASES.get(
            movement.strip().lower(),
            movement.strip().lower(),
        )

        return (
            normalized
            in self.MOVEMENTS
        )


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    compiler = MovementCompiler()

    print(
        "=== SIGNMUSIC MOVEMENT COMPILER ==="
    )

    tests = (
        "none",
        "down",
        "up",
        "forward",
        "backward",
        "left",
        "right",
        "front_to_center",
        "center_to_upper",
        "pull_up",
        "point_to_self",
        "point_forward",
    )

    for movement_name in tests:

        result = compiler.compile_movement(
            {
                "path": movement_name,
            }
        )

        print()
        print(
            f"{movement_name}:"
        )

        print(
            result
        )

    # ---------------------------------------------------------
    # ALIAS TESTS
    # ---------------------------------------------------------

    print()
    print(
        "=== ALIAS TESTS ==="
    )

    alias_tests = (
        "neutral",
        "upward",
        "front",
        "back",
        "pullup",
        "point_self",
        "point_to_other",
    )

    for alias in alias_tests:

        print(
            f"{alias} → "
            f"{compiler.ALIASES.get(alias)}"
        )

    # ---------------------------------------------------------
    # SUPPORTED
    # ---------------------------------------------------------

    print()
    print(
        "Supported:"
    )

    print(
        compiler.get_supported_movements()
    )

    print()
    print(
        "Status: OK"
    )