from typing import List, Dict

class SignGenerator:
    """Genera representaciones de lenguaje de señas"""
    
    # Diccionario básico de signos DGS (Deutsche Gebärdensprache)
    DGS_SIGNS = {
        "SAVE": {"movement": "pull_up", "hand_shape": "bent_fingers", "location": "chest"},
        "ME": {"movement": "point_to_self", "hand_shape": "pointing", "location": "chest"},
        "YOU": {"movement": "point_forward", "hand_shape": "pointing", "location": "center"},
        "HELP": {"movement": "support_up", "hand_shape": "open_hand", "location": "chest"},
        "LOVE": {"movement": "hug_self", "hand_shape": "curved_hands", "location": "chest"},
        "LIFE": {"movement": "upward_spiral", "hand_shape": "bent_fingers", "location": "body"},
    }
    
    def concept_to_sign(self, concept: str, language: str = "DGS") -> Dict:
        """Convierte un concepto en un signo"""
        sign = self.DGS_SIGNS.get(concept.upper(), None)
        
        if sign is None:
            return {
                "concept": concept,
                "sign": None,
                "confidence": 0.0,
                "status": "unknown"
            }
        
        return {
            "concept": concept,
            "sign": sign,
            "confidence": 1.0,
            "status": "mapped",
            "language": language
        }
    
    def generate_sequence(self, concepts: List[str], language: str = "DGS") -> List[Dict]:
        """Genera una secuencia de signos para una línea"""
        return [self.concept_to_sign(concept, language) for concept in concepts]