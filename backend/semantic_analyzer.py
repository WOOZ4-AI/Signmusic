import re
from typing import List, Dict

class SemanticAnalyzer:
    """Analiza el significado semántico de la letra"""
    
    def __init__(self):
        # Mapeos básicos de palabras a conceptos
        self.concept_map = {
            "save": ["RESCUE", "PROTECT", "HELP"],
            "me": ["SELF", "PERSON"],
            "you": ["OTHER", "PERSON"],
            "life": ["EXISTENCE", "LIVING"],
            "love": ["EMOTION", "FEELING"],
            "heart": ["EMOTION", "ORGAN"],
            "hand": ["BODY_PART", "ACTION_TOOL"],
            "light": ["BRIGHTNESS", "HOPE"],
            "dark": ["DARKNESS", "SADNESS"],
            "fall": ["MOVEMENT_DOWN", "FAILURE"],
            "rise": ["MOVEMENT_UP", "SUCCESS"],
        }
    
    def tokenize_line(self, line: str) -> List[str]:
        """Divide una línea en palabras"""
        # Elimina puntuación y convierte a minúsculas
        line = re.sub(r'[^\w\s]', '', line.lower())
        return line.split()
    
    def extract_concepts(self, line: str) -> Dict[str, List[str]]:
        """Extrae conceptos semánticos de una línea"""
        tokens = self.tokenize_line(line)
        concepts = {}
        
        for token in tokens:
            if token in self.concept_map:
                concepts[token] = self.concept_map[token]
        
        return concepts
    
    def analyze_line(self, line: str) -> dict:
        """Análisis completo de una línea"""
        return {
            "original": line,
            "tokens": self.tokenize_line(line),
            "concepts": self.extract_concepts(line),
            "confidence": 0.5  # Placeholder
        }