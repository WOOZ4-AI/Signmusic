from typing import Any, Dict, List, Optional

from bone_mapper import BoneMapper


class BlenderRenderer:
    """
    Renderer lógico de Signmusic para Blender.

    Este módulo NO importa bpy.
    Puede ejecutarse con Python normal.

    Responsabilidades:

    1. Validar una secuencia.
    2. Convertir huesos lógicos a huesos Mixamo.
    3. Convertir tiempos a frames.
    4. Preparar una secuencia lista para el adaptador de Blender.
    5. Proporcionar información sobre el renderer.
    """

    def __init__(
        self,
        bone_mapper: Optional[BoneMapper] = None,
    ):
        self.bone_mapper = (
            bone_mapper
            or BoneMapper()
        )

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    def validate_sequence(
        self,
        sequence: Dict[str, Any],
    ) -> List[str]:
        """
        Comprueba la estructura mínima de una secuencia.
        """

        errors: List[str] = []

        if not isinstance(sequence, dict):
            return [
                "La secuencia debe ser un diccionario."
            ]

        if "animations" not in sequence:
            errors.append(
                "Falta 'animations'."
            )
            return errors

        animations = sequence["animations"]

        if not isinstance(animations, list):
            errors.append(
                "'animations' debe ser una lista."
            )
            return errors

        fps = sequence.get("fps", 25)

        if not isinstance(fps, (int, float)):
            errors.append(
                "'fps' debe ser numérico."
            )
        elif fps <= 0:
            errors.append(
                "'fps' debe ser mayor que 0."
            )

        for index, animation in enumerate(
            animations
        ):

            if not isinstance(
                animation,
                dict,
            ):
                errors.append(
                    f"Animación {index} inválida."
                )
                continue

            if not animation.get("concept"):
                errors.append(
                    f"Animación {index}: "
                    "falta 'concept'."
                )

            if "keyframes" not in animation:
                errors.append(
                    f"Animación {index}: "
                    "falta 'keyframes'."
                )
                continue

            keyframes = animation["keyframes"]

            if not isinstance(
                keyframes,
                list,
            ):
                errors.append(
                    f"Animación {index}: "
                    "'keyframes' debe ser una lista."
                )
                continue

            for keyframe_index, keyframe in enumerate(
                keyframes
            ):

                if not isinstance(
                    keyframe,
                    dict,
                ):
                    errors.append(
                        f"Animación {index}, "
                        f"keyframe {keyframe_index}: "
                        "debe ser un diccionario."
                    )
                    continue

                if "time" not in keyframe:
                    errors.append(
                        f"Animación {index}, "
                        f"keyframe {keyframe_index}: "
                        "falta 'time'."
                    )

                if "bones" not in keyframe:
                    errors.append(
                        f"Animación {index}, "
                        f"keyframe {keyframe_index}: "
                        "falta 'bones'."
                    )

        return errors

    # =========================================================
    # CONVERSIÓN DE KEYFRAME
    # =========================================================

    def convert_keyframe(
        self,
        keyframe: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Convierte un keyframe de nombres lógicos
        a nombres reales del rig Mixamo.
        """

        if not isinstance(
            keyframe,
            dict,
        ):
            raise TypeError(
                "keyframe debe ser un diccionario."
            )

        bones = keyframe.get(
            "bones",
            {},
        )

        if not isinstance(
            bones,
            dict,
        ):
            raise TypeError(
                "'bones' debe ser un diccionario."
            )

        mapped_bones = (
            self.bone_mapper.map_transforms(
                bones
            )
        )

        return {
            **keyframe,
            "bones": mapped_bones,
        }

    # =========================================================
    # TIME → FRAME
    # =========================================================

    def time_to_frame(
        self,
        time: float,
        fps: int,
        frame_start: int = 1,
    ) -> int:
        """
        Convierte segundos a frame de Blender.

        Ejemplo:

            0.0s @ 25 FPS → frame 1
            0.4s @ 25 FPS → frame 11
            0.8s @ 25 FPS → frame 21
        """

        if fps <= 0:
            raise ValueError(
                "FPS debe ser mayor que 0."
            )

        if time < 0:
            raise ValueError(
                "El tiempo no puede ser negativo."
            )

        return (
            round(
                float(time) * fps
            )
            + frame_start
        )

    # =========================================================
    # CONVERSIÓN DE ANIMACIÓN
    # =========================================================

    def convert_animation(
        self,
        animation: Dict[str, Any],
        fps: int,
    ) -> Dict[str, Any]:
        """
        Convierte una animación completa.

        Además de mapear los huesos, calcula
        explícitamente el frame de Blender
        para cada keyframe.
        """

        if not isinstance(
            animation,
            dict,
        ):
            raise TypeError(
                "animation debe ser un diccionario."
            )

        result = dict(animation)

        start_time = float(
            animation.get(
                "start_time",
                0.0,
            )
        )

        duration = float(
            animation.get(
                "duration",
                0.0,
            )
        )

        converted_keyframes = []

        for keyframe in animation.get(
            "keyframes",
            [],
        ):

            converted = self.convert_keyframe(
                keyframe
            )

            local_time = float(
                converted.get(
                    "time",
                    0.0,
                )
            )

            absolute_time = (
                start_time
                + local_time
            )

            frame = self.time_to_frame(
                absolute_time,
                fps,
            )

            converted["time"] = local_time
            converted["absolute_time"] = (
                absolute_time
            )
            converted["frame"] = frame

            converted_keyframes.append(
                converted
            )

        result["keyframes"] = (
            converted_keyframes
        )

        result["start_frame"] = (
            self.time_to_frame(
                start_time,
                fps,
            )
        )

        result["end_frame"] = (
            self.time_to_frame(
                start_time + duration,
                fps,
            )
        )

        return result

    # =========================================================
    # PREPARAR SECUENCIA
    # =========================================================

    def prepare_sequence(
        self,
        sequence: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Prepara una secuencia completa para Blender.
        """

        errors = self.validate_sequence(
            sequence
        )

        if errors:
            raise ValueError(
                "Secuencia inválida: "
                + "; ".join(errors)
            )

        fps = int(
            sequence.get(
                "fps",
                25,
            )
        )

        prepared = dict(sequence)

        prepared["fps"] = fps

        prepared["animations"] = [
            self.convert_animation(
                animation,
                fps,
            )
            for animation in sequence[
                "animations"
            ]
        ]

        prepared["renderer"] = {
            "type": "blender",
            "skeleton": "Mixamo",
            "status": "prepared",
        }

        return prepared

    # =========================================================
    # CONFIGURACIÓN DEL RENDERER
    # =========================================================

    def get_renderer_configuration(
        self,
    ) -> Dict[str, Any]:
        """
        Devuelve la configuración esperada
        por el renderer de Blender.
        """

        supported_bones = (
            self.bone_mapper
            .get_supported_bones()
        )

        return {
            "renderer": "Blender",
            "skeleton": "Mixamo",
            "bone_count": len(
                supported_bones
            ),
            "bones": supported_bones,
            "status": "prepared",
        }


# =============================================================
# PRUEBA DIRECTA
# =============================================================

if __name__ == "__main__":

    renderer = BlenderRenderer()

    sequence = {
        "bpm": 120,
        "fps": 25,
        "animations": [
            {
                "concept": "SAVE",
                "start_time": 0.0,
                "duration": 0.8,
                "status": "defined",
                "keyframes": [
                    {
                        "time": 0.0,
                        "bones": {
                            "right_arm": {
                                "rotation": [
                                    0,
                                    0,
                                    0,
                                ],
                            },
                            "right_hand": {
                                "rotation": [
                                    0,
                                    0,
                                    0,
                                ],
                            },
                            "right_index_1": {
                                "rotation": [
                                    0,
                                    0,
                                    0,
                                ],
                            },
                        },
                    },
                    {
                        "time": 0.4,
                        "bones": {
                            "right_arm": {
                                "rotation": [
                                    25,
                                    0,
                                    0,
                                ],
                            },
                            "right_hand": {
                                "rotation": [
                                    15,
                                    0,
                                    0,
                                ],
                            },
                            "right_index_1": {
                                "rotation": [
                                    20,
                                    0,
                                    0,
                                ],
                            },
                        },
                    },
                    {
                        "time": 0.8,
                        "bones": {
                            "right_arm": {
                                "rotation": [
                                    0,
                                    0,
                                    0,
                                ],
                            },
                            "right_hand": {
                                "rotation": [
                                    0,
                                    0,
                                    0,
                                ],
                            },
                            "right_index_1": {
                                "rotation": [
                                    0,
                                    0,
                                    0,
                                ],
                            },
                        },
                    },
                ],
            },
        ],
    }

    print(
        "=== SIGNMUSIC BLENDER RENDERER ==="
    )

    print(
        "\nValidation:"
    )

    print(
        renderer.validate_sequence(
            sequence
        )
        or "OK"
    )

    print(
        "\nPrepared sequence:"
    )

    prepared = (
        renderer.prepare_sequence(
            sequence
        )
    )

    print(
        prepared
    )

    print(
        "\nRenderer configuration:"
    )

    print(
        renderer.get_renderer_configuration()
    )