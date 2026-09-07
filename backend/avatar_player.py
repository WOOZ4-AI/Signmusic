from typing import Dict, Any, List


class AvatarPlayer:
    """
    Calcula el estado del avatar en cualquier instante
    a partir de una secuencia de keyframes.

    No renderiza el avatar todavía.
    Su función es convertir keyframes en transforms
    interpolados que posteriormente podrá consumir
    un motor 3D.
    """

    SUPPORTED_BONES = [
        "mixamorig7:Head",
        "mixamorig7:LeftArm",
        "mixamorig7:LeftForeArm",
        "mixamorig7:LeftHand",
        "mixamorig7:RightArm",
        "mixamorig7:RightForeArm",
        "mixamorig7:RightHand",
        "mixamorig7:Spine",
    ]

    def __init__(self, fps: int = 25):
        self.fps = fps

    # ---------------------------------------------------------
    # Utilidades de interpolación
    # ---------------------------------------------------------

    @staticmethod
    def interpolate_value(
        start: float,
        end: float,
        factor: float
    ) -> float:
        """Interpolación lineal entre dos valores."""

        return start + (end - start) * factor

    @classmethod
    def interpolate_vector(
        cls,
        start: List[float],
        end: List[float],
        factor: float
    ) -> List[float]:
        """Interpolación lineal de un vector 3D."""

        return [
            cls.interpolate_value(
                start[i],
                end[i],
                factor
            )
            for i in range(len(start))
        ]

    # ---------------------------------------------------------
    # Keyframes
    # ---------------------------------------------------------

    @staticmethod
    def find_keyframe_pair(
        keyframes: List[Dict[str, Any]],
        time: float
    ):
        """
        Encuentra los dos keyframes que rodean
        el tiempo solicitado.
        """

        if not keyframes:
            return None, None

        if time <= keyframes[0]["time"]:
            return keyframes[0], keyframes[0]

        if time >= keyframes[-1]["time"]:
            return keyframes[-1], keyframes[-1]

        for i in range(len(keyframes) - 1):

            current = keyframes[i]
            next_frame = keyframes[i + 1]

            if current["time"] <= time <= next_frame["time"]:
                return current, next_frame

        return keyframes[-1], keyframes[-1]

    # ---------------------------------------------------------
    # Bone interpolation
    # ---------------------------------------------------------

    def interpolate_bone(
        self,
        start_bone: Dict[str, Any],
        end_bone: Dict[str, Any],
        factor: float
    ) -> Dict[str, Any]:

        result = {}

        # -----------------------------
        # Rotation
        # -----------------------------

        if (
            "rotation" in start_bone
            and "rotation" in end_bone
        ):
            result["rotation"] = self.interpolate_vector(
                start_bone["rotation"],
                end_bone["rotation"],
                factor
            )

        elif "rotation" in start_bone:
            result["rotation"] = start_bone["rotation"]

        elif "rotation" in end_bone:
            result["rotation"] = end_bone["rotation"]

        # -----------------------------
        # Position
        # -----------------------------

        if (
            "position" in start_bone
            and "position" in end_bone
        ):
            result["position"] = self.interpolate_vector(
                start_bone["position"],
                end_bone["position"],
                factor
            )

        elif "position" in start_bone:
            result["position"] = start_bone["position"]

        elif "position" in end_bone:
            result["position"] = end_bone["position"]

        return result

    # ---------------------------------------------------------
    # Keyframe sampling
    # ---------------------------------------------------------

    def sample_keyframes(
        self,
        keyframes: List[Dict[str, Any]],
        time: float
    ) -> Dict[str, Any]:

        if not keyframes:
            return {}

        start, end = self.find_keyframe_pair(
            keyframes,
            time
        )

        if start is None or end is None:
            return {}

        start_time = start["time"]
        end_time = end["time"]

        if end_time == start_time:
            factor = 0.0
        else:
            factor = (
                (time - start_time)
                / (end_time - start_time)
            )

        factor = max(
            0.0,
            min(1.0, factor)
        )

        bones = {}

        start_bones = start.get("bones", {})
        end_bones = end.get("bones", {})

        all_bones = set(start_bones) | set(end_bones)

        for bone_name in all_bones:

            start_bone = start_bones.get(
                bone_name,
                end_bones.get(
                    bone_name,
                    {}
                )
            )

            end_bone = end_bones.get(
                bone_name,
                start_bones.get(
                    bone_name,
                    {}
                )
            )

            bones[bone_name] = self.interpolate_bone(
                start_bone,
                end_bone,
                factor
            )

        return bones

    # ---------------------------------------------------------
    # Animation sampling
    # ---------------------------------------------------------

    def sample_animation(
        self,
        animation: Dict[str, Any],
        time: float
    ) -> Dict[str, Any]:

        keyframes = animation.get(
            "keyframes",
            []
        )

        if not keyframes:
            return {
                "concept": animation.get("concept"),
                "time": time,
                "bones": {}
            }

        duration = animation.get(
            "duration",
            keyframes[-1]["time"]
        )

        local_time = max(
            0.0,
            min(time, duration)
        )

        return {
            "concept": animation.get("concept"),
            "time": local_time,
            "bones": self.sample_keyframes(
                keyframes,
                local_time
            )
        }

    # ---------------------------------------------------------
    # Complete sequence
    # ---------------------------------------------------------

    def sample_sequence(
        self,
        sequence: Dict[str, Any],
        time: float
    ) -> Dict[str, Any]:

        animations = sequence.get(
            "animations",
            []
        )

        if not animations:
            return {
                "time": time,
                "concept": None,
                "bones": {}
            }

        # Buscar la animación activa
        for animation in animations:

            start_time = animation.get(
                "start_time",
                0.0
            )

            end_time = animation.get(
                "end_time",
                start_time
                + animation.get(
                    "duration",
                    0.0
                )
            )

            if start_time <= time <= end_time:

                local_time = time - start_time

                result = self.sample_animation(
                    animation,
                    local_time
                )

                result["global_time"] = time
                result["start_time"] = start_time
                result["end_time"] = end_time

                return result

        # Antes de la primera animación
        if time < animations[0].get(
            "start_time",
            0.0
        ):
            return {
                "time": time,
                "concept": None,
                "bones": {}
            }

        # Después de la última animación
        last = animations[-1]

        return {
            "time": time,
            "concept": last.get("concept"),
            "bones": self.sample_animation(
                last,
                last.get(
                    "duration",
                    0.0
                )
            )["bones"]
        }

    # ---------------------------------------------------------
    # Complete avatar state
    # ---------------------------------------------------------

    def get_avatar_state(
        self,
        sequence: Dict[str, Any],
        global_time: float
    ) -> Dict[str, Any]:
        """
        Obtiene el estado completo del avatar
        en un instante determinado.

        Los huesos que no participan en el gesto
        permanecen en posición neutra.
        """

        sample = self.sample_sequence(
            sequence,
            global_time
        )

        bones = {}

        # Estado neutro para todos los huesos
        for bone_name in self.SUPPORTED_BONES:

            bones[bone_name] = {
                "rotation": [
                    0.0,
                    0.0,
                    0.0
                ],
                "position": [
                    0.0,
                    0.0,
                    0.0
                ]
            }

        # Sobrescribir con el estado de la animación
        for bone_name, transform in sample.get(
            "bones",
            {}
        ).items():

            bones[bone_name] = {
                "rotation": [
                    float(value)
                    for value in transform.get(
                        "rotation",
                        [0.0, 0.0, 0.0]
                    )
                ],
                "position": [
                    float(value)
                    for value in transform.get(
                        "position",
                        [0.0, 0.0, 0.0]
                    )
                ]
            }

        return {
            "concept": sample.get("concept"),
            "global_time": float(global_time),
            "start_time": sample.get("start_time"),
            "end_time": sample.get("end_time"),
            "bones": bones
        }

    # ---------------------------------------------------------
    # Frame sampling
    # ---------------------------------------------------------

    def sample_frame(
        self,
        sequence: Dict[str, Any],
        frame: int
    ) -> Dict[str, Any]:

        time = frame / self.fps

        result = self.sample_sequence(
            sequence,
            time
        )

        result["frame"] = frame

        return result