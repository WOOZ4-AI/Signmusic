import json
import os
from typing import Any, Dict


class AnimationLoader:
    """
    Carga animaciones de Signmusic desde JSON.

    Esta clase normaliza formatos externos al formato
    canónico utilizado internamente por Signmusic.
    """

    # =========================================================
    # CONSTRUCTOR
    # =========================================================

    def __init__(self, fps: int = 25):
        if fps <= 0:
            raise ValueError(
                "fps debe ser mayor que 0."
            )

        self.fps = fps

    # =========================================================
    # CARGAR ARCHIVO
    # =========================================================

    def load_file(
        self,
        path: str,
    ) -> Dict[str, Any]:

        if not isinstance(path, str):
            raise TypeError(
                "path debe ser un string."
            )

        if not os.path.exists(path):
            raise FileNotFoundError(
                f"No existe el archivo: {path}"
            )

        with open(
            path,
            "r",
            encoding="utf-8",
        ) as file:

            data = json.load(file)

        return self.normalize(
            data
        )

    # =========================================================
    # NORMALIZAR
    # =========================================================

    def normalize(
        self,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:

        if not isinstance(data, dict):
            raise TypeError(
                "La animación debe ser un diccionario."
            )

        fps = int(
            data.get(
                "fps",
                self.fps,
            )
        )

        animations = data.get(
            "animations",
            [],
        )

        if not isinstance(
            animations,
            list,
        ):
            raise ValueError(
                "'animations' debe ser una lista."
            )

        normalized_animations = []

        current_time = 0.0

        for animation in animations:

            if not isinstance(
                animation,
                dict,
            ):
                raise ValueError(
                    "Cada animación debe ser un diccionario."
                )

            concept = str(
                animation.get(
                    "concept",
                    "UNKNOWN",
                )
            ).strip().upper()

            duration = float(
                animation.get(
                    "duration",
                    0.0,
                )
            )

            if duration <= 0:
                continue

            start_time = float(
                animation.get(
                    "start_time",
                    current_time,
                )
            )

            keyframes = []

            for keyframe in animation.get(
                "keyframes",
                [],
            ):

                local_time = float(
                    keyframe.get(
                        "time",
                        0.0,
                    )
                )

                phase = self._detect_phase(
                    local_time,
                    duration,
                )

                bones = self._normalize_bones(
                    keyframe.get(
                        "bones",
                        {},
                    )
                )

                keyframes.append(
                    {
                        "time": local_time,
                        "phase": phase,
                        "bones": bones,
                    }
                )

            normalized_animations.append(
                {
                    "concept": concept,
                    "start_time": start_time,
                    "duration": duration,
                    "end_time": (
                        start_time
                        + duration
                    ),
                    "status": animation.get(
                        "status",
                        "defined",
                    ),
                    "confidence": float(
                        animation.get(
                            "confidence",
                            0.0,
                        )
                    ),
                    "keyframes": keyframes,
                }
            )

            current_time = (
                start_time
                + duration
            )

        total_duration = float(
            data.get(
                "total_duration",
                current_time,
            )
        )

        return {
            "bpm": data.get(
                "bpm"
            ),
            "fps": fps,
            "beat_duration": data.get(
                "beat_duration"
            ),
            "total_duration": total_duration,
            "animations": normalized_animations,
            "format": "signmusic-canonical-v1",
        }

    # =========================================================
    # NORMALIZAR HUESOS
    # =========================================================

    @staticmethod
    def _normalize_bones(
        bones: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Dict[str, Any]]:

        if not isinstance(
            bones,
            dict,
        ):
            return {}

        aliases = {
            "LeftShoulder": "left_shoulder",
            "LeftArm": "left_arm",
            "LeftForeArm": "left_forearm",
            "LeftHand": "left_hand",

            "RightShoulder": "right_shoulder",
            "RightArm": "right_arm",
            "RightForeArm": "right_forearm",
            "RightHand": "right_hand",

            "Head": "head",
            "Neck": "neck",

            "Spine": "spine",
            "Spine1": "spine1",
            "Spine2": "spine2",

            "LeftHandThumb1": "left_thumb_1",
            "LeftHandThumb2": "left_thumb_2",
            "LeftHandThumb3": "left_thumb_3",

            "LeftHandIndex1": "left_index_1",
            "LeftHandIndex2": "left_index_2",
            "LeftHandIndex3": "left_index_3",

            "LeftHandMiddle1": "left_middle_1",
            "LeftHandMiddle2": "left_middle_2",
            "LeftHandMiddle3": "left_middle_3",

            "LeftHandRing1": "left_ring_1",
            "LeftHandRing2": "left_ring_2",
            "LeftHandRing3": "left_ring_3",

            "LeftHandPinky1": "left_pinky_1",
            "LeftHandPinky2": "left_pinky_2",
            "LeftHandPinky3": "left_pinky_3",

            "RightHandThumb1": "right_thumb_1",
            "RightHandThumb2": "right_thumb_2",
            "RightHandThumb3": "right_thumb_3",

            "RightHandIndex1": "right_index_1",
            "RightHandIndex2": "right_index_2",
            "RightHandIndex3": "right_index_3",

            "RightHandMiddle1": "right_middle_1",
            "RightHandMiddle2": "right_middle_2",
            "RightHandMiddle3": "right_middle_3",

            "RightHandRing1": "right_ring_1",
            "RightHandRing2": "right_ring_2",
            "RightHandRing3": "right_ring_3",

            "RightHandPinky1": "right_pinky_1",
            "RightHandPinky2": "right_pinky_2",
            "RightHandPinky3": "right_pinky_3",
        }

        normalized = {}

        for bone_name, transform in bones.items():

            logical_name = aliases.get(
                bone_name,
                bone_name,
            )

            normalized[
                logical_name
            ] = dict(transform)

        return normalized

    # =========================================================
    # DETECTAR FASE
    # =========================================================

    @staticmethod
    def _detect_phase(
        time: float,
        duration: float,
    ) -> str:

        if time <= 0:
            return "start"

        if time >= duration:
            return "end"

        return "motion"


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    loader = AnimationLoader()

    project_root = os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
        )
    )

    path = os.path.join(
        project_root,
        "data",
        "sample_sequence.json",
    )

    animation = loader.load_file(
        path
    )

    print(
        "=== SIGNMUSIC ANIMATION LOADER ==="
    )

    print(
        "Format:",
        animation["format"],
    )

    print(
        "FPS:",
        animation["fps"],
    )

    print(
        "Animations:",
        len(animation["animations"]),
    )

    for item in animation["animations"]:

        print(
            f"{item['concept']}: "
            f"{len(item['keyframes'])} keyframes"
        )

    print(
        "Status: OK"
    )