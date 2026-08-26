from typing import List, Dict
import json

class KeyframeGenerator:
    """Genera keyframes de animación para el avatar basado en signos DGS"""
    
    # Huesos clave para lenguaje de signos
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
    
    # Definiciones de gestos DGS
    # Cada gesto es una secuencia de keyframes
    DGS_GESTURES = {
        "SAVE": {
            "duration": 0.8,
            "description": "Movimiento de rescate/protección",
            "keyframes": [
                {
                    "frame": 0,
                    "time": 0.0,
                    "bones": {
                        "LeftArm": {"rotation": [0, 0, 0], "position": [0, 0, 0]},
                        "RightArm": {"rotation": [0, 0, 0], "position": [0, 0, 0]},
                        "LeftHand": {"rotation": [0, 0, 0]},
                        "RightHand": {"rotation": [0, 0, 0]},
                    }
                },
                {
                    "frame": 10,
                    "time": 0.4,
                    "bones": {
                        "LeftArm": {"rotation": [90, 0, 0], "position": [0, 0.3, 0]},
                        "RightArm": {"rotation": [90, 0, 0], "position": [0, 0.3, 0]},
                        "LeftHand": {"rotation": [45, 0, 0]},
                        "RightHand": {"rotation": [45, 0, 0]},
                    }
                },
                {
                    "frame": 20,
                    "time": 0.8,
                    "bones": {
                        "LeftArm": {"rotation": [0, 0, 0], "position": [0, 0, 0]},
                        "RightArm": {"rotation": [0, 0, 0], "position": [0, 0, 0]},
                        "LeftHand": {"rotation": [0, 0, 0]},
                        "RightHand": {"rotation": [0, 0, 0]},
                    }
                }
            ]
        },
        "HELP": {
            "duration": 0.7,
            "description": "Gesto de ayuda/soporte",
            "keyframes": [
                {
                    "frame": 0,
                    "time": 0.0,
                    "bones": {
                        "LeftArm": {"rotation": [45, 0, 0]},
                        "RightArm": {"rotation": [45, 0, 0]},
                    }
                },
                {
                    "frame": 15,
                    "time": 0.35,
                    "bones": {
                        "LeftArm": {"rotation": [135, 0, 0]},
                        "RightArm": {"rotation": [135, 0, 0]},
                    }
                },
                {
                    "frame": 30,
                    "time": 0.7,
                    "bones": {
                        "LeftArm": {"rotation": [45, 0, 0]},
                        "RightArm": {"rotation": [45, 0, 0]},
                    }
                }
            ]
        },
        "LOVE": {
            "duration": 0.6,
            "description": "Gesto del corazón/amor",
            "keyframes": [
                {
                    "frame": 0,
                    "time": 0.0,
                    "bones": {
                        "LeftHand": {"rotation": [0, 0, 0], "position": [-0.2, 0, 0]},
                        "RightHand": {"rotation": [0, 0, 0], "position": [0.2, 0, 0]},
                    }
                },
                {
                    "frame": 10,
                    "time": 0.3,
                    "bones": {
                        "LeftHand": {"rotation": [45, 0, 0], "position": [-0.15, 0.1, 0]},
                        "RightHand": {"rotation": [-45, 0, 0], "position": [0.15, 0.1, 0]},
                    }
                },
                {
                    "frame": 20,
                    "time": 0.6,
                    "bones": {
                        "LeftHand": {"rotation": [0, 0, 0], "position": [-0.2, 0, 0]},
                        "RightHand": {"rotation": [0, 0, 0], "position": [0.2, 0, 0]},
                    }
                }
            ]
        }
    }
    
    def get_gesture(self, concept: str) -> Dict:
        """
        Obtiene los keyframes para un concepto DGS
        
        Args:
            concept: concepto en mayúsculas (ej: "SAVE", "HELP")
        
        Returns:
            dict con keyframes y metadata
        """
        gesture = self.DGS_GESTURES.get(concept.upper(), None)
        
        if gesture is None:
            return {
                "concept": concept,
                "gesture": None,
                "status": "not_defined",
                "confidence": 0.0
            }
        
        return {
            "concept": concept,
            "gesture": gesture,
            "status": "defined",
            "confidence": 1.0,
            "duration": gesture["duration"],
            "keyframes_count": len(gesture["keyframes"])
        }
    
    def generate_animation_sequence(self, concepts: List[str], bpm: int = 120) -> Dict:
        """
        Genera una secuencia de animación para una lista de conceptos
        
        Args:
            concepts: lista de conceptos DGS
            bpm: beats por minuto de la canción (para sincronización)
        
        Returns:
            dict con la secuencia de animación completa
        """
        beat_duration = 60 / bpm  # duración de un beat en segundos
        
        sequence = {
            "bpm": bpm,
            "beat_duration": beat_duration,
            "total_duration": 0.0,
            "animations": []
        }
        
        current_time = 0.0
        
        for concept in concepts:
            gesture = self.get_gesture(concept)
            
            if gesture["status"] == "defined":
                animation = {
                    "concept": concept,
                    "start_time": current_time,
                    "duration": gesture["duration"],
                    "end_time": current_time + gesture["duration"],
                    "keyframes": gesture["gesture"]["keyframes"]
                }
                sequence["animations"].append(animation)
                current_time += gesture["duration"]
            else:
                # Gesto no definido, usar pausa
                sequence["animations"].append({
                    "concept": concept,
                    "start_time": current_time,
                    "duration": 0.5,
                    "end_time": current_time + 0.5,
                    "status": "undefined",
                    "keyframes": []
                })
                current_time += 0.5
        
        sequence["total_duration"] = current_time
        return sequence
    
    def save_animation_to_json(self, sequence: Dict, output_path: str) -> None:
        """Guarda la secuencia de animación en JSON"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(sequence, f, indent=2, ensure_ascii=False)
        print(f"✅ Animación guardada en: {output_path}")