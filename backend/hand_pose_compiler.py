from typing import Any, Dict


class HandPoseCompiler:
    """
    Compilador de posturas de mano para Signmusic.

    Esta capa es independiente de Blender.

    Separa:

        descripción conceptual de la mano
                ↓
        calibración del avatar
                ↓
        huesos lógicos de Signmusic

    IMPORTANTE:

    Los valores de calibración utilizados aquí describen
    el comportamiento del rig de prueba.

    NO representan todavía datos lingüísticos verificados
    de DGS, ASL ni de otra lengua de signos.
    """

    # =========================================================
    # DEDOS
    # =========================================================

    FINGERS = {
        "thumb",
        "index",
        "middle",
        "ring",
        "pinky",
    }

    # =========================================================
    # CALIBRACIÓN DE FLEXIÓN
    # =========================================================
    #
    # Para los cuatro dedos largos:
    #
    # flexion = 60
    #
    # se distribuye como:
    #
    # segment_1 = 60
    # segment_2 = 40
    # segment_3 = 20
    #
    # Esto es una calibración inicial del avatar.
    # =========================================================

    FLEXION_DISTRIBUTION = {
        "segment_1": 1.0,
        "segment_2": 2.0 / 3.0,
        "segment_3": 1.0 / 3.0,
    }

    # =========================================================
    # CALIBRACIÓN DEL PULGAR
    # =========================================================
    #
    # La prueba visual mostró que la rotación equivalente
    # a la prueba C mueve el pulgar hacia la palma.
    #
    # Por ello:
    #
    # opposition = 45
    #
    # produce aproximadamente:
    #
    # thumb_1 = 45
    # thumb_2 = 30
    # thumb_3 = 15
    #
    # El eje utilizado es Z.
    #
    # Estos valores NO son datos lingüísticos.
    # =========================================================

    THUMB_OPPOSITION_DISTRIBUTION = {
        "segment_1": 1.0,
        "segment_2": 2.0 / 3.0,
        "segment_3": 1.0 / 3.0,
    }

    # =========================================================
    # COMPILAR UNA MANO
    # =========================================================

    def compile_hand(
        self,
        hand_shape: Dict[str, Any],
        side: str,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compila una mano completa.

        side:
            "left"
            "right"
        """

        if not isinstance(
            hand_shape,
            dict,
        ):
            raise TypeError(
                "hand_shape debe ser un diccionario."
            )

        side = side.strip().lower()

        if side not in {
            "left",
            "right",
        }:
            raise ValueError(
                "side debe ser 'left' o 'right'."
            )

        fingers = hand_shape.get(
            "fingers",
            {},
        )

        if not isinstance(
            fingers,
            dict,
        ):
            raise TypeError(
                "hand_shape['fingers'] debe ser un diccionario."
            )

        result = {}

        for finger_name, definition in (
            fingers.items()
        ):

            normalized_finger = (
                str(finger_name)
                .strip()
                .lower()
            )

            if normalized_finger not in self.FINGERS:
                continue

            result.update(
                self._compile_finger(
                    side=side,
                    finger=normalized_finger,
                    definition=definition,
                )
            )

        return result

    # =========================================================
    # COMPILAR DEDO
    # =========================================================

    def _compile_finger(
        self,
        side: str,
        finger: str,
        definition: Any,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compila un dedo.

        Formatos soportados:

        1. flexion:
            {
                "flexion": 60
            }

        2. opposition para pulgar:
            {
                "opposition": 45
            }

        3. segmentos explícitos:
            {
                "segment_1": {...},
                "segment_2": {...},
                "segment_3": {...}
            }

        4. formato legacy:
            {
                "rotation": [30, 20, 10]
            }
        """

        if not isinstance(
            definition,
            dict,
        ):
            raise TypeError(
                f"La configuración de {finger} "
                "debe ser un diccionario."
            )

        prefix = (
            f"{side}_{finger}"
        )

        # -----------------------------------------------------
        # PULGAR → OPOSICIÓN
        # -----------------------------------------------------

        if (
            finger == "thumb"
            and "opposition" in definition
        ):

            opposition = float(
                definition["opposition"]
            )

            return self._compile_thumb_opposition(
                prefix=prefix,
                opposition=opposition,
            )

        # -----------------------------------------------------
        # DEDOS → FLEXIÓN
        # -----------------------------------------------------

        if "flexion" in definition:

            flexion = float(
                definition["flexion"]
            )

            return self._compile_flexion(
                prefix=prefix,
                flexion=flexion,
            )

        # -----------------------------------------------------
        # SEGMENTOS EXPLÍCITOS
        # -----------------------------------------------------

        result = {}

        for index in range(1, 4):

            key = (
                f"segment_{index}"
            )

            data = definition.get(
                key
            )

            if data is None:
                continue

            if not isinstance(
                data,
                dict,
            ):
                raise TypeError(
                    f"{finger}.{key} "
                    "debe ser un diccionario."
                )

            bone_name = (
                f"{prefix}_{index}"
            )

            result[bone_name] = dict(
                data
            )

        if result:
            return result

        # -----------------------------------------------------
        # LEGACY → ROTACIÓN
        # -----------------------------------------------------

        rotation = definition.get(
            "rotation"
        )

        if rotation is not None:

            if not isinstance(
                rotation,
                (list, tuple),
            ):
                raise TypeError(
                    f"rotation de {finger} "
                    "debe ser una lista."
                )

            if len(rotation) != 3:
                raise ValueError(
                    f"rotation de {finger} "
                    "debe tener 3 valores."
                )

            for index, angle in enumerate(
                rotation,
                start=1,
            ):

                bone_name = (
                    f"{prefix}_{index}"
                )

                result[bone_name] = {
                    "rotation": [
                        float(angle),
                        0.0,
                        0.0,
                    ]
                }

        return result

    # =========================================================
    # COMPILAR FLEXIÓN
    # =========================================================

    def _compile_flexion(
        self,
        prefix: str,
        flexion: float,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compila flexión para los dedos largos.

        El eje calibrado para estos dedos es X.
        """

        if flexion < 0:
            raise ValueError(
                "flexion no puede ser negativa."
            )

        result = {}

        for index in range(1, 4):

            factor = (
                self.FLEXION_DISTRIBUTION[
                    f"segment_{index}"
                ]
            )

            angle = (
                flexion
                * factor
            )

            bone_name = (
                f"{prefix}_{index}"
            )

            result[bone_name] = {
                "rotation": [
                    float(angle),
                    0.0,
                    0.0,
                ]
            }

        return result

    # =========================================================
    # COMPILAR OPOSICIÓN DEL PULGAR
    # =========================================================

    def _compile_thumb_opposition(
        self,
        prefix: str,
        opposition: float,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compila oposición del pulgar.

        El eje Z corresponde a la calibración visual
        obtenida con el avatar de prueba.
        """

        if opposition < 0:
            raise ValueError(
                "opposition no puede ser negativa."
            )

        result = {}

        for index in range(1, 4):

            factor = (
                self.THUMB_OPPOSITION_DISTRIBUTION[
                    f"segment_{index}"
                ]
            )

            angle = (
                opposition
                * factor
            )

            bone_name = (
                f"{prefix}_{index}"
            )

            result[bone_name] = {
                "rotation": [
                    0.0,
                    0.0,
                    float(angle),
                ]
            }

        return result

    # =========================================================
    # COMPILAR DOS MANOS
    # =========================================================

    def compile_hands(
        self,
        left_hand: Dict[str, Any] | None = None,
        right_hand: Dict[str, Any] | None = None,
    ) -> Dict[str, Dict[str, Any]]:

        result = {}

        if left_hand is not None:

            result.update(
                self.compile_hand(
                    left_hand,
                    "left",
                )
            )

        if right_hand is not None:

            result.update(
                self.compile_hand(
                    right_hand,
                    "right",
                )
            )

        return result


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    compiler = HandPoseCompiler()

    test_hand = {
        "shape": "test",

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
    }

    print(
        "=== SIGNMUSIC HAND POSE COMPILER ==="
    )

    print(
        "\nConfiguración conceptual:"
    )

    print(
        test_hand
    )

    result = compiler.compile_hand(
        test_hand,
        "right",
    )

    print(
        "\nCompiled hand:"
    )

    for bone, transform in (
        result.items()
    ):

        print(
            f"  {bone}: {transform}"
        )

    print(
        "\nTotal finger bones:",
        len(result),
    )

    print(
        "\nStatus: OK"
    )