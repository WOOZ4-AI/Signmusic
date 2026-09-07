from typing import Dict, List, Any


class AvatarAnimation:
    """
    Capa de adaptación entre el motor de keyframes y el avatar 3D.

    Responsabilidades:

    1. Validar una secuencia de animación.
    2. Convertir nombres lógicos de huesos a nombres del esqueleto.
    3. Preparar una estructura independiente del renderer.
    4. Mantener separada la lógica lingüística de la representación 3D.

    IMPORTANTE:
    Los movimientos recibidos siguen siendo experimentales.
    Esta clase NO determina si un signo es lingüísticamente correcto.
    """

    BONE_MAP = {
    # =========================================================
    # CUERPO
    # =========================================================

    "Hips": "mixamorig7:Hips",

    "Spine": "mixamorig7:Spine",
    "Spine1": "mixamorig7:Spine1",
    "Spine2": "mixamorig7:Spine2",

    "Neck": "mixamorig7:Neck",
    "Head": "mixamorig7:Head",

    # =========================================================
    # BRAZO IZQUIERDO
    # =========================================================

    "LeftShoulder": "mixamorig7:LeftShoulder",
    "LeftArm": "mixamorig7:LeftArm",
    "LeftForeArm": "mixamorig7:LeftForeArm",
    "LeftHand": "mixamorig7:LeftHand",

    # =========================================================
    # MANO IZQUIERDA - PULGAR
    # =========================================================

    "LeftHandThumb1": "mixamorig7:LeftHandThumb1",
    "LeftHandThumb2": "mixamorig7:LeftHandThumb2",
    "LeftHandThumb3": "mixamorig7:LeftHandThumb3",

    # =========================================================
    # MANO IZQUIERDA - ÍNDICE
    # =========================================================

    "LeftHandIndex1": "mixamorig7:LeftHandIndex1",
    "LeftHandIndex2": "mixamorig7:LeftHandIndex2",
    "LeftHandIndex3": "mixamorig7:LeftHandIndex3",

    # =========================================================
    # MANO IZQUIERDA - MEDIO
    # =========================================================

    "LeftHandMiddle1": "mixamorig7:LeftHandMiddle1",
    "LeftHandMiddle2": "mixamorig7:LeftHandMiddle2",
    "LeftHandMiddle3": "mixamorig7:LeftHandMiddle3",

    # =========================================================
    # MANO IZQUIERDA - ANULAR
    # =========================================================

    "LeftHandRing1": "mixamorig7:LeftHandRing1",
    "LeftHandRing2": "mixamorig7:LeftHandRing2",
    "LeftHandRing3": "mixamorig7:LeftHandRing3",

    # =========================================================
    # MANO IZQUIERDA - MEÑIQUE
    # =========================================================

    "LeftHandPinky1": "mixamorig7:LeftHandPinky1",
    "LeftHandPinky2": "mixamorig7:LeftHandPinky2",
    "LeftHandPinky3": "mixamorig7:LeftHandPinky3",

    # =========================================================
    # BRAZO DERECHO
    # =========================================================

    "RightShoulder": "mixamorig7:RightShoulder",
    "RightArm": "mixamorig7:RightArm",
    "RightForeArm": "mixamorig7:RightForeArm",
    "RightHand": "mixamorig7:RightHand",

    # =========================================================
    # MANO DERECHA - PULGAR
    # =========================================================

    "RightHandThumb1": "mixamorig7:RightHandThumb1",
    "RightHandThumb2": "mixamorig7:RightHandThumb2",
    "RightHandThumb3": "mixamorig7:RightHandThumb3",

    # =========================================================
    # MANO DERECHA - ÍNDICE
    # =========================================================

    "RightHandIndex1": "mixamorig7:RightHandIndex1",
    "RightHandIndex2": "mixamorig7:RightHandIndex2",
    "RightHandIndex3": "mixamorig7:RightHandIndex3",

    # =========================================================
    # MANO DERECHA - MEDIO
    # =========================================================

    "RightHandMiddle1": "mixamorig7:RightHandMiddle1",
    "RightHandMiddle2": "mixamorig7:RightHandMiddle2",
    "RightHandMiddle3": "mixamorig7:RightHandMiddle3",

    # =========================================================
    # MANO DERECHA - ANULAR
    # =========================================================

    "RightHandRing1": "mixamorig7:RightHandRing1",
    "RightHandRing2": "mixamorig7:RightHandRing2",
    "RightHandRing3": "mixamorig7:RightHandRing3",

    # =========================================================
    # MANO DERECHA - MEÑIQUE
    # =========================================================

    "RightHandPinky1": "mixamorig7:RightHandPinky1",
    "RightHandPinky2": "mixamorig7:RightHandPinky2",
    "RightHandPinky3": "mixamorig7:RightHandPinky3",
}

    SUPPORTED_TRANSFORMS = {
        "rotation",
        "position",
        "scale",
    }

    def __init__(self, bone_map: Dict[str, str] | None = None):
        self.bone_map = bone_map or self.BONE_MAP.copy()

    # =========================================================
    # HUESOS
    # =========================================================

    def resolve_bone(self, logical_name: str) -> str | None:
        """
        Convierte un nombre lógico de hueso en el nombre real
        utilizado por el avatar.
        """

        if not isinstance(logical_name, str):
            return None

        return self.bone_map.get(logical_name)

    def get_supported_bones(self) -> List[str]:
        """
        Devuelve los nombres lógicos de huesos soportados.
        """

        return sorted(self.bone_map.keys())

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    def validate_keyframe(self, keyframe: Dict[str, Any]) -> Dict[str, Any]:
        """
        Valida un keyframe individual.

        No intenta determinar si el movimiento es correcto
        desde el punto de vista lingüístico.
        """

        errors = []

        if not isinstance(keyframe, dict):
            return {
                "valid": False,
                "errors": ["El keyframe debe ser un objeto"],
            }

        if "frame" not in keyframe:
            errors.append("Falta 'frame'")

        if "time" not in keyframe:
            errors.append("Falta 'time'")

        bones = keyframe.get("bones")

        if bones is None:
            errors.append("Falta 'bones'")

        elif not isinstance(bones, dict):
            errors.append("'bones' debe ser un objeto")

        else:
            for logical_bone, transforms in bones.items():

                if logical_bone not in self.bone_map:
                    errors.append(
                        f"Hueso no soportado: {logical_bone}"
                    )
                    continue

                if not isinstance(transforms, dict):
                    errors.append(
                        f"Transformaciones inválidas para {logical_bone}"
                    )
                    continue

                for transform in transforms:

                    if transform not in self.SUPPORTED_TRANSFORMS:
                        errors.append(
                            f"Transformación no soportada: "
                            f"{logical_bone}.{transform}"
                        )

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    # =========================================================
    # CONVERSIÓN DE KEYFRAMES
    # =========================================================

    def convert_keyframe(
        self,
        keyframe: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convierte un keyframe lógico en uno compatible con
        el esqueleto real del avatar.
        """

        validation = self.validate_keyframe(keyframe)

        if not validation["valid"]:
            raise ValueError(
                "Keyframe inválido: "
                + "; ".join(validation["errors"])
            )

        converted_bones = {}

        for logical_bone, transforms in keyframe["bones"].items():

            real_bone = self.resolve_bone(logical_bone)

            converted_bones[real_bone] = transforms.copy()

        return {
            "frame": keyframe["frame"],
            "time": keyframe["time"],
            "bones": converted_bones,
        }

    # =========================================================
    # ANIMACIONES
    # =========================================================

    def convert_animation(
        self,
        animation: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convierte una animación completa.
        """

        if not isinstance(animation, dict):
            raise TypeError("animation debe ser un objeto")

        keyframes = animation.get("keyframes", [])

        if not isinstance(keyframes, list):
            raise ValueError(
                "'keyframes' debe ser una lista"
            )

        converted_keyframes = []

        for keyframe in keyframes:
            converted_keyframes.append(
                self.convert_keyframe(keyframe)
            )

        result = animation.copy()
        result["keyframes"] = converted_keyframes

        return result

    # =========================================================
    # SECUENCIA COMPLETA
    # =========================================================

    def prepare_sequence(
        self,
        sequence: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Prepara una secuencia completa para el avatar.

        La salida sigue siendo independiente del renderer.
        """

        if not isinstance(sequence, dict):
            raise TypeError("sequence debe ser un objeto")

        animations = sequence.get("animations", [])

        if not isinstance(animations, list):
            raise ValueError(
                "'animations' debe ser una lista"
            )

        prepared_animations = []

        for animation in animations:

            if animation.get("status") == "undefined":
                prepared_animations.append(
                    animation.copy()
                )
                continue

            prepared_animations.append(
                self.convert_animation(animation)
            )

        return {
            "bpm": sequence.get("bpm"),
            "fps": sequence.get("fps", 25),
            "beat_duration": sequence.get(
                "beat_duration"
            ),
            "total_duration": sequence.get(
                "total_duration"
            ),
            "animations": prepared_animations,
        }

    # =========================================================
    # INFORMACIÓN DEL AVATAR
    # =========================================================

    def get_avatar_configuration(self) -> Dict[str, Any]:
        """
        Devuelve información que el frontend puede utilizar
        para conocer el esqueleto soportado.
        """

        return {
            "skeleton": "Mixamo",
            "bone_map": self.bone_map.copy(),
            "supported_transforms": sorted(
                self.SUPPORTED_TRANSFORMS
            ),
            "fps": 25,
        }