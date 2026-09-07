from typing import Any, Dict


class SignToMotionCompiler:
    """
    Convierte una definición semántica experimental de Signmusic
    en una descripción motora estructurada que puede consumir
    MotionGenerator.

    IMPORTANTE:

    Esta capa NO afirma que las definiciones representen DGS real.
    Son mapeos experimentales para el desarrollo del pipeline.
    """

    # =========================================================
    # FORMAS DE MANO EXPERIMENTALES
    # =========================================================

    HAND_SHAPES = {
        "open_hand": {
            "shape": "open_hand",
            "fingers": {
                "thumb": {
                    "opposition": 30,
                },
                "index": {
                    "flexion": 0,
                },
                "middle": {
                    "flexion": 0,
                },
                "ring": {
                    "flexion": 0,
                },
                "pinky": {
                    "flexion": 0,
                },
            },
        },

        "pointing": {
            "shape": "pointing",
            "fingers": {
                "thumb": {
                    "opposition": 45,
                },
                "index": {
                    "flexion": 0,
                },
                "middle": {
                    "flexion": 85,
                },
                "ring": {
                    "flexion": 85,
                },
                "pinky": {
                    "flexion": 85,
                },
            },
        },

        "bent_fingers": {
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

        "curved_hands": {
            "shape": "curved_hands",
            "fingers": {
                "thumb": {
                    "opposition": 35,
                },
                "index": {
                    "flexion": 45,
                },
                "middle": {
                    "flexion": 40,
                },
                "ring": {
                    "flexion": 40,
                },
                "pinky": {
                    "flexion": 35,
                },
            },
        },
    }

    # =========================================================
    # MOVIMIENTOS EXPERIMENTALES
    # =========================================================

    MOVEMENTS = {
        "none": {
            "path": "none",
        },

        "pull_up": {
            "path": "up",
        },

        "point_to_self": {
            "path": "center_to_upper",
        },

        "point_forward": {
            "path": "forward",
        },

        "support_up": {
            "path": "up",
        },

        "hug_self": {
            "path": "center_to_upper",
        },

        "upward_spiral": {
            "path": "up",
        },
    }

    # =========================================================
    # UBICACIONES EXPERIMENTALES
    # =========================================================

    LOCATIONS = {
        "chest": "center",
        "center": "center",
        "body": "center",
    }

    # =========================================================
    # CONSTRUCTOR
    # =========================================================

    def __init__(self):
        pass

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    @staticmethod
    def _normalize(
        value: Any,
    ) -> str:

        if value is None:
            return ""

        return str(
            value
        ).strip().lower()

    # =========================================================
    # COMPILAR FORMA DE MANO
    # =========================================================

    def compile_hand_shape(
        self,
        hand_shape_name: str,
    ) -> Dict[str, Any]:

        normalized = self._normalize(
            hand_shape_name
        )

        definition = self.HAND_SHAPES.get(
            normalized
        )

        if definition is None:

            raise ValueError(
                "Forma de mano experimental "
                f"no soportada: {hand_shape_name}"
            )

        # Devolver copia independiente
        return {
            "shape": definition["shape"],

            "fingers": {
                finger: {
                    key: value
                    for key, value
                    in finger_data.items()
                }
                for finger, finger_data
                in definition["fingers"].items()
            },
        }

    # =========================================================
    # COMPILAR MOVIMIENTO
    # =========================================================

    def compile_movement(
        self,
        movement_name: str,
    ) -> Dict[str, Any]:

        normalized = self._normalize(
            movement_name
        )

        definition = self.MOVEMENTS.get(
            normalized
        )

        if definition is None:

            raise ValueError(
                "Movimiento experimental "
                f"no soportado: {movement_name}"
            )

        return dict(
            definition
        )

    # =========================================================
    # COMPILAR UBICACIÓN
    # =========================================================

    def compile_location(
        self,
        location_name: str,
    ) -> Dict[str, Any]:

        normalized = self._normalize(
            location_name
        )

        location = self.LOCATIONS.get(
            normalized
        )

        if location is None:

            raise ValueError(
                "Ubicación experimental "
                f"no soportada: {location_name}"
            )

        return {
            "target": location,
        }

    # =========================================================
    # COMPILAR SIGNO
    # =========================================================

    def compile_sign(
        self,
        sign: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not isinstance(
            sign,
            dict,
        ):
            raise TypeError(
                "sign debe ser un diccionario."
            )

        concept = str(
            sign.get(
                "concept",
                "UNKNOWN",
            )
        ).strip().upper()

        hand_shape_name = sign.get(
            "hand_shape"
        )

        movement_name = sign.get(
            "movement",
            "none",
        )

        location_name = sign.get(
            "location",
            "center",
        )

        if not hand_shape_name:
            raise ValueError(
                f"{concept}: falta hand_shape."
            )

        hand_shape = (
            self.compile_hand_shape(
                hand_shape_name
            )
        )

        movement = (
            self.compile_movement(
                movement_name
            )
        )

        location = (
            self.compile_location(
                location_name
            )
        )

        return {
            "concept": concept,

            "hand_shape": hand_shape,

            "orientation": {
                "palm": "neutral",
            },

            "location": location,

            "movement": movement,

            "non_manual": {},

            "status": "compiled_experimental",
        }


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    compiler = SignToMotionCompiler()

    test_signs = [
        {
            "concept": "SAVE",
            "hand_shape": "bent_fingers",
            "movement": "pull_up",
            "location": "chest",
        },

        {
            "concept": "ME",
            "hand_shape": "pointing",
            "movement": "point_to_self",
            "location": "chest",
        },

        {
            "concept": "YOU",
            "hand_shape": "pointing",
            "movement": "point_forward",
            "location": "center",
        },
    ]

    print(
        "=== SIGNMUSIC SIGN TO MOTION COMPILER ==="
    )

    for sign in test_signs:

        print()

        print(
            f"{sign['concept']}:"
        )

        result = compiler.compile_sign(
            sign
        )

        print(
            result
        )

    print()
    print(
        "Status: OK"
    )