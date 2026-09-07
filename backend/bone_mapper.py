from typing import Dict, Optional


class BoneMapper:
    """
    Mapea los nombres lógicos de Signmusic
    a los huesos reales del avatar Mixamo.

    IMPORTANTE:

    El resto del backend utiliza exclusivamente
    nombres lógicos.

    Ejemplo:

        right_arm
        right_hand
        right_index_1

    Esta clase es la única responsable de convertirlos
    al rig real:

        mixamorig7:RightArm
        mixamorig7:RightHand
        mixamorig7:RightHandIndex1
    """

    # =========================================================
    # MAPA OFICIAL SIGNMUSIC → MIXAMO
    # =========================================================

    DEFAULT_MAPPING = {

        # -----------------------------------------------------
        # CUERPO
        # -----------------------------------------------------

        "hips": "mixamorig7:Hips",

        "spine": "mixamorig7:Spine",
        "spine1": "mixamorig7:Spine1",
        "spine2": "mixamorig7:Spine2",

        "neck": "mixamorig7:Neck",
        "head": "mixamorig7:Head",

        # -----------------------------------------------------
        # HOMBRO / BRAZO IZQUIERDO
        # -----------------------------------------------------

        "left_shoulder": "mixamorig7:LeftShoulder",
        "left_arm": "mixamorig7:LeftArm",
        "left_forearm": "mixamorig7:LeftForeArm",
        "left_hand": "mixamorig7:LeftHand",

        # -----------------------------------------------------
        # MANO IZQUIERDA - PULGAR
        # -----------------------------------------------------

        "left_thumb_1": "mixamorig7:LeftHandThumb1",
        "left_thumb_2": "mixamorig7:LeftHandThumb2",
        "left_thumb_3": "mixamorig7:LeftHandThumb3",

        # -----------------------------------------------------
        # MANO IZQUIERDA - ÍNDICE
        # -----------------------------------------------------

        "left_index_1": "mixamorig7:LeftHandIndex1",
        "left_index_2": "mixamorig7:LeftHandIndex2",
        "left_index_3": "mixamorig7:LeftHandIndex3",

        # -----------------------------------------------------
        # MANO IZQUIERDA - MEDIO
        # -----------------------------------------------------

        "left_middle_1": "mixamorig7:LeftHandMiddle1",
        "left_middle_2": "mixamorig7:LeftHandMiddle2",
        "left_middle_3": "mixamorig7:LeftHandMiddle3",

        # -----------------------------------------------------
        # MANO IZQUIERDA - ANULAR
        # -----------------------------------------------------

        "left_ring_1": "mixamorig7:LeftHandRing1",
        "left_ring_2": "mixamorig7:LeftHandRing2",
        "left_ring_3": "mixamorig7:LeftHandRing3",

        # -----------------------------------------------------
        # MANO IZQUIERDA - MEÑIQUE
        # -----------------------------------------------------

        "left_pinky_1": "mixamorig7:LeftHandPinky1",
        "left_pinky_2": "mixamorig7:LeftHandPinky2",
        "left_pinky_3": "mixamorig7:LeftHandPinky3",

        # -----------------------------------------------------
        # HOMBRO / BRAZO DERECHO
        # -----------------------------------------------------

        "right_shoulder": "mixamorig7:RightShoulder",
        "right_arm": "mixamorig7:RightArm",
        "right_forearm": "mixamorig7:RightForeArm",
        "right_hand": "mixamorig7:RightHand",

        # -----------------------------------------------------
        # MANO DERECHA - PULGAR
        # -----------------------------------------------------

        "right_thumb_1": "mixamorig7:RightHandThumb1",
        "right_thumb_2": "mixamorig7:RightHandThumb2",
        "right_thumb_3": "mixamorig7:RightHandThumb3",

        # -----------------------------------------------------
        # MANO DERECHA - ÍNDICE
        # -----------------------------------------------------

        "right_index_1": "mixamorig7:RightHandIndex1",
        "right_index_2": "mixamorig7:RightHandIndex2",
        "right_index_3": "mixamorig7:RightHandIndex3",

        # -----------------------------------------------------
        # MANO DERECHA - MEDIO
        # -----------------------------------------------------

        "right_middle_1": "mixamorig7:RightHandMiddle1",
        "right_middle_2": "mixamorig7:RightHandMiddle2",
        "right_middle_3": "mixamorig7:RightHandMiddle3",

        # -----------------------------------------------------
        # MANO DERECHA - ANULAR
        # -----------------------------------------------------

        "right_ring_1": "mixamorig7:RightHandRing1",
        "right_ring_2": "mixamorig7:RightHandRing2",
        "right_ring_3": "mixamorig7:RightHandRing3",

        # -----------------------------------------------------
        # MANO DERECHA - MEÑIQUE
        # -----------------------------------------------------

        "right_pinky_1": "mixamorig7:RightHandPinky1",
        "right_pinky_2": "mixamorig7:RightHandPinky2",
        "right_pinky_3": "mixamorig7:RightHandPinky3",
    }

    # =========================================================
    # CONSTRUCTOR
    # =========================================================

    def __init__(
        self,
        mapping: Optional[Dict[str, str]] = None,
    ):
        self.mapping = dict(
            mapping
            or self.DEFAULT_MAPPING
        )

    # =========================================================
    # OBTENER HUESO
    # =========================================================

    def get_bone(
        self,
        logical_name: str,
    ) -> Optional[str]:

        if not isinstance(
            logical_name,
            str,
        ):
            return None

        normalized_name = (
            logical_name
            .strip()
            .lower()
        )

        return self.mapping.get(
            normalized_name
        )

    # =========================================================
    # COMPROBAR EXISTENCIA
    # =========================================================

    def has_bone(
        self,
        logical_name: str,
    ) -> bool:

        return (
            self.get_bone(logical_name)
            is not None
        )

    # =========================================================
    # MAPEAR HUESOS
    # =========================================================

    def map_bones(
        self,
        logical_bones,
    ) -> Dict[str, str]:

        result = {}

        for logical_name in logical_bones:

            real_name = self.get_bone(
                logical_name
            )

            if real_name is not None:
                result[
                    logical_name
                ] = real_name

        return result

    # =========================================================
    # MAPEAR TRANSFORMACIONES
    # =========================================================

    def map_transforms(
        self,
        transforms: Dict[str, Dict],
    ) -> Dict[str, Dict]:
        """
        Convierte:

            {
                "right_arm": {
                    "rotation": [25, 0, 0]
                }
            }

        en:

            {
                "mixamorig7:RightArm": {
                    "rotation": [25, 0, 0]
                }
            }
        """

        if not isinstance(
            transforms,
            dict,
        ):
            raise TypeError(
                "transforms debe ser un diccionario"
            )

        result = {}

        for logical_name, transform in (
            transforms.items()
        ):

            real_name = self.get_bone(
                logical_name
            )

            if real_name is None:
                continue

            if not isinstance(
                transform,
                dict,
            ):
                raise ValueError(
                    f"Transformación inválida "
                    f"para {logical_name}"
                )

            result[
                real_name
            ] = dict(transform)

        return result

    # =========================================================
    # MAPEAR KEYFRAME
    # =========================================================

    def map_keyframe(
        self,
        keyframe: Dict,
    ) -> Dict:
        """
        Convierte un keyframe completo
        de nombres lógicos a nombres reales.
        """

        if not isinstance(
            keyframe,
            dict,
        ):
            raise TypeError(
                "keyframe debe ser un diccionario"
            )

        bones = keyframe.get(
            "bones",
            {},
        )

        return {
            **keyframe,
            "bones": self.map_transforms(
                bones
            ),
        }

    # =========================================================
    # MAPEAR ANIMACIÓN
    # =========================================================

    def map_animation(
        self,
        animation: Dict,
    ) -> Dict:
        """
        Convierte todos los keyframes
        de una animación.
        """

        if not isinstance(
            animation,
            dict,
        ):
            raise TypeError(
                "animation debe ser un diccionario"
            )

        result = dict(animation)

        keyframes = animation.get(
            "keyframes",
            [],
        )

        result["keyframes"] = [
            self.map_keyframe(keyframe)
            for keyframe in keyframes
        ]

        return result

    # =========================================================
    # VALIDAR MAPEO
    # =========================================================

    def validate_mapping(
        self,
        available_bones,
    ) -> Dict[str, list]:

        available = set(
            available_bones
        )

        valid = []
        missing = []

        for (
            logical_name,
            real_name,
        ) in self.mapping.items():

            if real_name in available:

                valid.append(
                    logical_name
                )

            else:

                missing.append({
                    "logical": logical_name,
                    "avatar": real_name,
                })

        return {
            "valid": valid,
            "missing": missing,
        }

    # =========================================================
    # INFORMACIÓN
    # =========================================================

    def get_supported_bones(self):

        return sorted(
            self.mapping.keys()
        )


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    mapper = BoneMapper()

    print(
        "=== SIGNMUSIC BONE MAPPER ==="
    )

    transforms = {

        "right_arm": {
            "rotation": [25, 0, 0],
        },

        "right_hand": {
            "rotation": [15, 0, 0],
        },

        "right_index_1": {
            "rotation": [20, 0, 0],
        },

        "left_arm": {
            "rotation": [10, 0, 0],
        },
    }

    print(
        "\nLogical transforms:"
    )

    print(
        transforms
    )

    mapped = mapper.map_transforms(
        transforms
    )

    print(
        "\nMapped transforms:"
    )

    print(
        mapped
    )

    print(
        "\nRight arm:"
    )

    print(
        mapper.get_bone(
            "right_arm"
        )
    )

    print(
        "\nRight index:"
    )

    print(
        mapper.get_bone(
            "right_index_1"
        )
    )

    print(
        "\nUnknown:"
    )

    print(
        mapper.get_bone(
            "unknown"
        )
    )

    print(
        "\nSupported bones:"
    )

    print(
        len(
            mapper.get_supported_bones()
        )
    )

    print(
        "\nValidation:"
    )

    validation = mapper.validate_mapping(
        mapper.DEFAULT_MAPPING.values()
    )

    print(
        validation
    )