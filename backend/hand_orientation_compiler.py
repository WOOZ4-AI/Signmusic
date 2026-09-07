from typing import Any, Dict


class HandOrientationCompiler:
    """
    Convierte una orientación conceptual de la mano
    en una rotación compatible con el rig de Signmusic.

    Esta clase NO depende de Blender.

    IMPORTANTE:
    Las orientaciones y ángulos utilizados aquí son una
    calibración experimental del avatar actual.

    No representan todavía una especificación lingüística
    oficial de ASL, DGS ni de otra lengua de signos.
    """

    # =========================================================
    # CALIBRACIÓN DEL AVATAR
    # =========================================================

    ORIENTATIONS = {
        "down": {
            "rotation": [45.0, 0.0, 0.0],
        },

        "side_up": {
            "rotation": [0.0, 45.0, 0.0],
        },

        "left": {
            "rotation": [0.0, 0.0, 45.0],
        },

        "neutral": {
            "rotation": [0.0, 0.0, 0.0],
        },
    }

    # Alias para permitir distintas formas de expresar
    # la misma intención.
    ALIASES = {
        "downward": "down",
        "palm_down": "down",
        "down": "down",

        "side_up": "side_up",
        "up_side": "side_up",
        "sideways_up": "side_up",

        "left": "left",
        "palm_left": "left",

        "neutral": "neutral",
        "normal": "neutral",
    }

    # =========================================================
    # COMPILAR
    # =========================================================

    def compile_orientation(
        self,
        orientation: Dict[str, Any],
        side: str = "right",
    ) -> Dict[str, Dict[str, Any]]:
        """
        Convierte una orientación conceptual
        en una transformación del hueso de la mano.

        Ejemplo:

            {
                "palm": "down"
            }

        →

            {
                "right_hand": {
                    "rotation": [...]
                }
            }
        """

        if not isinstance(
            orientation,
            dict,
        ):
            raise TypeError(
                "orientation debe ser un diccionario."
            )

        side = side.strip().lower()

        if side not in {
            "left",
            "right",
        }:
            raise ValueError(
                "side debe ser 'left' o 'right'."
            )

        palm = orientation.get(
            "palm",
            "neutral",
        )

        if palm is None:
            palm = "neutral"

        palm = str(
            palm
        ).strip().lower()

        normalized = self.ALIASES.get(
            palm,
            palm,
        )

        if normalized not in self.ORIENTATIONS:
            raise ValueError(
                f"Orientación no soportada: {palm}"
            )

        rotation = list(
            self.ORIENTATIONS[
                normalized
            ]["rotation"]
        )

        bone_name = (
            f"{side}_hand"
        )

        return {
            bone_name: {
                "rotation": rotation
            }
        }

    # =========================================================
    # ORIENTACIONES DISPONIBLES
    # =========================================================

    def get_supported_orientations(self):
        """
        Devuelve las orientaciones conceptuales
        actualmente calibradas.
        """

        return sorted(
            self.ORIENTATIONS.keys()
        )

    # =========================================================
    # COMPROBAR SOPORTE
    # =========================================================

    def is_supported(
        self,
        orientation: str,
    ) -> bool:
        """
        Comprueba si una orientación está soportada.
        """

        if not isinstance(
            orientation,
            str,
        ):
            return False

        normalized = self.ALIASES.get(
            orientation.strip().lower(),
            orientation.strip().lower(),
        )

        return (
            normalized
            in self.ORIENTATIONS
        )


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    compiler = HandOrientationCompiler()

    print(
        "=== SIGNMUSIC HAND ORIENTATION COMPILER ==="
    )

    for orientation in (
        "neutral",
        "down",
        "side_up",
        "left",
    ):

        result = compiler.compile_orientation(
            {
                "palm": orientation,
            },
            "right",
        )

        print()
        print(
            f"{orientation}:"
        )

        print(
            result
        )

    print()
    print(
        "Supported:"
    )

    print(
        compiler.get_supported_orientations()
    )

    print(
        "\nStatus: OK"
    )