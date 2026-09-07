from typing import List, Dict
import json


class KeyframeGenerator:
    """
    Motor de generación de keyframes para el avatar de Signmusic.

    IMPORTANTE:
    Los gestos incluidos actualmente son EXPERIMENTALES.
    No representan todavía una implementación lingüística
    validada oficialmente de DGS.

    Arquitectura:

        concepto
            ↓
        gesto DGS experimental
            ↓
        keyframes
            ↓
        secuencia temporal
            ↓
        animación del avatar
    """

    FPS = 25

    SIGN_BONES = {
        "LeftArm": "mixamorig7:LeftArm",
        "LeftForeArm": "mixamorig7:LeftForeArm",
        "LeftHand": "mixamorig7:LeftHand",
        "RightArm": "mixamorig7:RightArm",
        "RightForeArm": "mixamorig7:RightForeArm",
        "RightHand": "mixamorig7:RightHand",
        "Spine": "mixamorig7:Spine",
        "Head": "mixamorig7:Head",
    }

    # =========================================================
    # GESTOS EXPERIMENTALES
    # =========================================================

    DGS_GESTURES = {

        "SAVE": {
            "duration": 0.8,
            "description": "Movimiento experimental de rescate/protección",
            "keyframes": [
                {
                    "frame": 0,
                    "time": 0.0,
                    "bones": {
                        "LeftArm": {
                            "rotation": [0, 0, 0],
                            "position": [0, 0, 0],
                        },
                        "RightArm": {
                            "rotation": [0, 0, 0],
                            "position": [0, 0, 0],
                        },
                        "LeftHand": {
                            "rotation": [0, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [0, 0, 0],
                        },
                    },
                },
                {
                    "frame": 10,
                    "time": 0.4,
                    "bones": {
                        "LeftArm": {
                            "rotation": [90, 0, 0],
                            "position": [0, 0.3, 0],
                        },
                        "RightArm": {
                            "rotation": [90, 0, 0],
                            "position": [0, 0.3, 0],
                        },
                        "LeftHand": {
                            "rotation": [45, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [45, 0, 0],
                        },
                    },
                },
                {
                    "frame": 20,
                    "time": 0.8,
                    "bones": {
                        "LeftArm": {
                            "rotation": [0, 0, 0],
                            "position": [0, 0, 0],
                        },
                        "RightArm": {
                            "rotation": [0, 0, 0],
                            "position": [0, 0, 0],
                        },
                        "LeftHand": {
                            "rotation": [0, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [0, 0, 0],
                        },
                    },
                },
            ],
        },

        "ME": {
            "duration": 0.45,
            "description": "Movimiento experimental de referencia hacia el propio cuerpo",
            "keyframes": [
                {
                    "frame": 0,
                    "time": 0.0,
                    "bones": {
                        "RightArm": {
                            "rotation": [0, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [0, 0, 0],
                        },
                    },
                },
                {
                    "frame": 6,
                    "time": 0.24,
                    "bones": {
                        "RightArm": {
                            "rotation": [25, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [15, 0, 0],
                        },
                    },
                },
                {
                    "frame": 12,
                    "time": 0.45,
                    "bones": {
                        "RightArm": {
                            "rotation": [0, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [0, 0, 0],
                        },
                    },
                },
            ],
        },

        "YOU": {
            "duration": 0.45,
            "description": "Movimiento experimental de referencia hacia otra persona",
            "keyframes": [
                {
                    "frame": 0,
                    "time": 0.0,
                    "bones": {
                        "RightArm": {
                            "rotation": [0, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [0, 0, 0],
                        },
                    },
                },
                {
                    "frame": 6,
                    "time": 0.24,
                    "bones": {
                        "RightArm": {
                            "rotation": [10, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [0, 0, 0],
                            "position": [0, 0, 0.25],
                        },
                    },
                },
                {
                    "frame": 12,
                    "time": 0.45,
                    "bones": {
                        "RightArm": {
                            "rotation": [0, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [0, 0, 0],
                            "position": [0, 0, 0],
                        },
                    },
                },
            ],
        },

        "HELP": {
            "duration": 0.7,
            "description": "Movimiento experimental de ayuda/soporte",
            "keyframes": [
                {
                    "frame": 0,
                    "time": 0.0,
                    "bones": {
                        "LeftArm": {
                            "rotation": [45, 0, 0],
                        },
                        "RightArm": {
                            "rotation": [45, 0, 0],
                        },
                    },
                },
                {
                    "frame": 15,
                    "time": 0.35,
                    "bones": {
                        "LeftArm": {
                            "rotation": [135, 0, 0],
                        },
                        "RightArm": {
                            "rotation": [135, 0, 0],
                        },
                    },
                },
                {
                    "frame": 30,
                    "time": 0.7,
                    "bones": {
                        "LeftArm": {
                            "rotation": [45, 0, 0],
                        },
                        "RightArm": {
                            "rotation": [45, 0, 0],
                        },
                    },
                },
            ],
        },

        "LOVE": {
            "duration": 0.6,
            "description": "Movimiento experimental de afecto",
            "keyframes": [
                {
                    "frame": 0,
                    "time": 0.0,
                    "bones": {
                        "LeftHand": {
                            "rotation": [0, 0, 0],
                            "position": [-0.2, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [0, 0, 0],
                            "position": [0.2, 0, 0],
                        },
                    },
                },
                {
                    "frame": 10,
                    "time": 0.3,
                    "bones": {
                        "LeftHand": {
                            "rotation": [45, 0, 0],
                            "position": [-0.15, 0.1, 0],
                        },
                        "RightHand": {
                            "rotation": [-45, 0, 0],
                            "position": [0.15, 0.1, 0],
                        },
                    },
                },
                {
                    "frame": 20,
                    "time": 0.6,
                    "bones": {
                        "LeftHand": {
                            "rotation": [0, 0, 0],
                            "position": [-0.2, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [0, 0, 0],
                            "position": [0.2, 0, 0],
                        },
                    },
                },
            ],
        },

        "LIFE": {
            "duration": 0.7,
            "description": "Movimiento experimental ascendente",
            "keyframes": [
                {
                    "frame": 0,
                    "time": 0.0,
                    "bones": {
                        "LeftHand": {
                            "rotation": [0, 0, 0],
                            "position": [-0.15, 0, 0],
                        },
                        "RightHand": {
                            "rotation": [0, 0, 0],
                            "position": [0.15, 0, 0],
                        },
                    },
                },
                {
                    "frame": 10,
                    "time": 0.35,
                    "bones": {
                        "LeftHand": {
                            "rotation": [20, 0, 0],
                            "position": [-0.1, 0.15, 0],
                        },
                        "RightHand": {
                            "rotation": [-20, 0, 0],
                            "position": [0.1, 0.15, 0],
                        },
                    },
                },
                {
                    "frame": 20,
                    "time": 0.7,
                    "bones": {
                        "LeftHand": {
                            "rotation": [40, 0, 0],
                            "position": [-0.05, 0.3, 0],
                        },
                        "RightHand": {
                            "rotation": [-40, 0, 0],
                            "position": [0.05, 0.3, 0],
                        },
                    },
                },
            ],
        },
    }

    # =========================================================
    # API DEL MOTOR
    # =========================================================

    def get_gesture(self, concept: str) -> Dict:
        """
        Devuelve la definición de un gesto.
        """

        if not isinstance(concept, str):
            raise TypeError("concept debe ser un string")

        normalized_concept = concept.strip().upper()

        gesture = self.DGS_GESTURES.get(normalized_concept)

        if gesture is None:
            return {
                "concept": normalized_concept,
                "gesture": None,
                "status": "not_defined",
                "confidence": 0.0,
            }

        return {
            "concept": normalized_concept,
            "gesture": gesture,
            "status": "defined",
            "confidence": 1.0,
            "duration": gesture["duration"],
            "keyframes_count": len(gesture["keyframes"]),
        }

    def generate_animation_sequence(
        self,
        concepts: List[str],
        bpm: int = 120,
    ) -> Dict:
        """
        Genera una secuencia temporal de animaciones.

        Cada concepto recibe un gesto definido o, si todavía
        no existe, una pausa marcada como undefined.
        """

        if not isinstance(concepts, list):
            raise TypeError("concepts debe ser una lista")

        try:
            bpm = int(bpm)
        except (TypeError, ValueError):
            raise ValueError("bpm debe ser un número")

        if bpm <= 0:
            raise ValueError("bpm debe ser mayor que 0")

        beat_duration = 60 / bpm

        sequence = {
            "bpm": bpm,
            "fps": self.FPS,
            "beat_duration": beat_duration,
            "total_duration": 0.0,
            "animations": [],
        }

        current_time = 0.0

        for concept in concepts:

            gesture = self.get_gesture(concept)

            if gesture["status"] == "defined":

                animation = {
                    "concept": gesture["concept"],
                    "start_time": current_time,
                    "duration": gesture["duration"],
                    "end_time": current_time + gesture["duration"],
                    "status": "defined",
                    "confidence": gesture["confidence"],
                    "keyframes": gesture["gesture"]["keyframes"],
                }

                sequence["animations"].append(animation)

                current_time += gesture["duration"]

            else:

                duration = beat_duration

                sequence["animations"].append({
                    "concept": gesture["concept"],
                    "start_time": current_time,
                    "duration": duration,
                    "end_time": current_time + duration,
                    "status": "undefined",
                    "confidence": 0.0,
                    "keyframes": [],
                })

                current_time += duration

        sequence["total_duration"] = current_time

        return sequence

    def get_supported_concepts(self) -> List[str]:
        """
        Devuelve todos los conceptos que actualmente
        tienen un gesto experimental definido.
        """

        return sorted(self.DGS_GESTURES.keys())

    def is_supported(self, concept: str) -> bool:
        """
        Comprueba si existe un gesto para un concepto.
        """

        if not isinstance(concept, str):
            return False

        return concept.strip().upper() in self.DGS_GESTURES

    def save_animation_to_json(
        self,
        sequence: Dict,
        output_path: str,
    ) -> None:
        """
        Guarda una secuencia de animación como JSON.
        """

        with open(
            output_path,
            "w",
            encoding="utf-8",
        ) as f:
            json.dump(
                sequence,
                f,
                indent=2,
                ensure_ascii=False,
            )

        print(f"✅ Animación guardada en: {output_path}")