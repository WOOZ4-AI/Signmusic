import re
from typing import List, Dict


class SemanticAnalyzer:
    """Analiza semánticamente una línea de una canción."""

    def __init__(self):
        # Conceptos canónicos utilizados por Signmusic.
        #
        # IMPORTANTE:
        # Estos conceptos son la interfaz entre el análisis semántico
        # y el sistema de lenguaje de señas.
        self.concept_map = {
            "save": ["SAVE"],
            "me": ["ME"],
            "you": ["YOU"],
            "help": ["HELP"],
            "love": ["LOVE"],
            "life": ["LIFE"],
        }

    def tokenize_line(self, line: str) -> List[str]:
        """Divide una línea en palabras normalizadas."""

        line = re.sub(r"[^\w\s]", "", line.lower())

        return line.split()

    def extract_concepts(self, line: str) -> Dict[str, List[str]]:
        """Extrae conceptos canónicos de una línea."""

        tokens = self.tokenize_line(line)

        concepts = {}

        for token in tokens:
            if token in self.concept_map:
                concepts[token] = self.concept_map[token]

        return concepts

    def analyze_line(self, line: str) -> dict:
        """Realiza el análisis completo de una línea."""

        tokens = self.tokenize_line(line)
        concepts = self.extract_concepts(line)

        extracted_concepts = []

        for word_concepts in concepts.values():
            extracted_concepts.extend(word_concepts)

        return {
            "original": line,
            "tokens": tokens,
            "concepts": concepts,
            "normalized_concepts": extracted_concepts,
            "confidence": 1.0 if extracted_concepts else 0.0,
        }