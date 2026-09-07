from typing import Any, Dict


class HandLocationCompiler:
    """
    Convierte una ubicación conceptual de la mano
    en transformaciones lógicas de brazo/antebrazo/mano.

    Esta clase NO depende de Blender.

    IMPORTANTE:
    Los valores actuales son una calibración experimental
    del avatar. No representan todavía una descripción
    lingüística validada de DGS, ASL u otra lengua de signos.
    """

    # =========================================================
    # CALIBRACIÓN INICIAL
    # =========================================================

    LOCATIONS = {
        "neutral": {
            "arm": {
                "rotation": [0.0, 0.0, 0.0],
            },
            "forearm": {
                "rotation": [0.0, 0.0, 0.0],
            },
        },

        "lower": {
            "arm": {
                "rotation": [20.0, 0.0, 0.0],
            },
            "forearm": {
                "rotation": [35.0, 0.0, 0.0],
            },
        },

        "upper": {
            "arm": {
                "rotation": [-35.0, 0.0, 0.0],
            },
            "forearm": {
                "rotation": [-65.0, 0.0, 0.0],
            },
        },

        "center": {
            "arm": {
                "rotation": [0.0, 0.0, -55.0],
            },
            "forearm": {
                "rotation": [25.0, 0.0, 0.0],
            },
        },

        "front": {
            "arm": {
                "rotation": [15.0, 0.0, 0.0],
            },
            "forearm": {
                "rotation": [-75.0, 0.0, 0.0],
            },
        },
    }

    # =========================================================
    # ALIAS
    # =========================================================

    ALIASES = {
        "neutral": "neutral",
        "normal": "neutral",

        "lower": "lower",
        "down": "lower",
        "below": "lower",

        "upper": "upper",
        "up": "upper",
        "above": "upper",

        "center": "center",
        "centre": "center",
        "middle": "center",

        "front": "front",
        "forward": "front",
        "ahead": "front",
    }

    # =========================================================
    # COMPILAR
    # =========================================================

    def compile_location(
        self,
        location: Dict[str, Any],
        side: str = "right",
    ) -> Dict[str, Dict[str, Any]]:
        """
        Convierte una ubicación conceptual en huesos lógicos.

        Ejemplo:

            {
                "region": "front"
            }

        produce transformaciones para:

            right_arm
            right_forearm
        """

        if not isinstance(
            location,
            dict,
        ):
            raise TypeError(
                "location debe ser un diccionario."
            )

        side = side.strip().lower()

        if side not in {
            "left",
            "right",
        }:
            raise ValueError(
                "side debe ser 'left' o 'right'."
            )

        region = location.get(
            "region",
            "neutral",
        )

        region = str(
            region
        ).strip().lower()

        normalized = self.ALIASES.get(
            region,
            region,
        )

        if normalized not in self.LOCATIONS:
            raise ValueError(
                f"Ubicación no soportada: {region}"
            )

        definition = self.LOCATIONS[
            normalized
        ]

        result = {}

        result[
            f"{side}_arm"
        ] = dict(
            definition["arm"]
        )

        result[
            f"{side}_forearm"
        ] = dict(
            definition["forearm"]
        )

        return result

    # =========================================================
    # SOPORTE
    # =========================================================

    def get_supported_locations(self):
        """
        Devuelve las ubicaciones conceptuales disponibles.
        """

        return sorted(
            self.LOCATIONS.keys()
        )

    def is_supported(
        self,
        location: str,
    ) -> bool:
        """
        Comprueba si una ubicación está soportada.
        """

        if not isinstance(
            location,
            str,
        ):
            return False

        normalized = self.ALIASES.get(
            location.strip().lower(),
            location.strip().lower(),
        )

        return (
            normalized
            in self.LOCATIONS
        )


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    compiler = HandLocationCompiler()

    print(
        "=== SIGNMUSIC HAND LOCATION COMPILER ==="
    )

    for location in (
        "neutral",
        "lower",
        "upper",
        "center",
        "front",
    ):

        result = compiler.compile_location(
            {
                "region": location,
            },
            "right",
        )

        print()
        print(
            f"{location}:"
        )

        print(
            result
        )

    print()
    print(
        "Supported:"
    )

    print(
        compiler.get_supported_locations()
    )

    print(
        "\nStatus: OK"
    )