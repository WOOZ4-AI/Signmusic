from typing import Dict, List


class DGSTranslator:
    """
    Capa de traducción intermedia hacia DGS.

    IMPORTANTE:
    Esta implementación es experimental.
    No pretende representar todavía una traducción lingüística
    oficial o validada de DGS.

    Su objetivo actual es separar:

        texto
        ↓
        análisis semántico
        ↓
        estructura de traducción
        ↓
        futura traducción lingüística DGS
    """

    def __init__(self):
        self.rules = [
            {
                "name": "simple_sequence",
                "description": "Mantener conceptos en una secuencia básica",
            }
        ]

    def normalize_concepts(self, concepts: List[str]) -> List[str]:
        """
        Normaliza una lista de conceptos.

        Elimina valores inválidos, espacios y duplicados,
        conservando el orden original.
        """

        if not isinstance(concepts, list):
            raise TypeError("concepts debe ser una lista")

        normalized = []

        for concept in concepts:
            if not isinstance(concept, str):
                continue

            concept = concept.strip().upper()

            if not concept:
                continue

            if concept not in normalized:
                normalized.append(concept)

        return normalized

    def translate(
        self,
        concepts: List[str],
        language: str = "DGS",
    ) -> Dict:
        """
        Convierte conceptos normalizados en una estructura
        intermedia de traducción.
        """

        normalized = self.normalize_concepts(concepts)

        translation_units = []

        for index, concept in enumerate(normalized):
            translation_units.append(
                {
                    "index": index,
                    "concept": concept,
                    "status": "pending_sign_validation",
                }
            )

        return {
            "source_language": "en",
            "target_language": language,
            "status": "experimental",
            "strategy": "simple_sequence",
            "concepts": normalized,
            "translation_units": translation_units,
        }

    def translate_lines(
        self,
        analyses: List[Dict],
        language: str = "DGS",
    ) -> Dict:
        """
        Traduce una canción línea por línea.

        Cada línea conserva su propia secuencia de conceptos.

        Esto será importante posteriormente para:

        - sincronización con la música
        - sincronización con BPM
        - animación del avatar
        - edición de traducciones
        - análisis lingüístico DGS
        """

        if not isinstance(analyses, list):
            raise TypeError("analyses debe ser una lista")

        translated_lines = []

        for line_index, analysis in enumerate(analyses):

            if not isinstance(analysis, dict):
                continue

            concepts = analysis.get("normalized_concepts", [])

            translation = self.translate(
                concepts,
                language=language,
            )

            translated_lines.append(
                {
                    "line_index": line_index,
                    "original": analysis.get("original", ""),
                    "tokens": analysis.get("tokens", []),
                    "concepts": translation["concepts"],
                    "translation_units": translation["translation_units"],
                    "status": translation["status"],
                }
            )

        return {
            "source_language": "en",
            "target_language": language,
            "status": "experimental",
            "strategy": "line_based_sequence",
            "lines": translated_lines,
        }