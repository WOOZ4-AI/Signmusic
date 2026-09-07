from typing import List, Dict

try:
    from .signs.lexicon import get_sign
except ImportError:
    from signs.lexicon import get_sign


class SignGenerator:
    """
    Convierte conceptos lingüísticos en definiciones de signos.

    La responsabilidad de esta clase es únicamente la capa
    lingüística/intermedia.

    La animación del avatar pertenece a KeyframeGenerator.
    """

    def concept_to_sign(
        self,
        concept: str,
        language: str = "DGS",
    ) -> Dict:

        if not isinstance(
            concept,
            str,
        ):
            raise TypeError(
                "concept debe ser un string."
            )

        normalized_concept = (
            concept.strip().upper()
        )

        if not normalized_concept:
            raise ValueError(
                "concept no puede estar vacío."
            )

        sign = get_sign(
            normalized_concept
        )

        if sign is None:
            return {
                "concept": normalized_concept,
                "sign": None,
                "confidence": 0.0,
                "status": "unknown",
                "language": language,
            }

        return {
            "concept": normalized_concept,
            "sign": sign.to_dict(),
            "confidence": 1.0,
            "status": "mapped",
            "language": language,
        }

    def generate_sequence(
        self,
        concepts: List[str],
        language: str = "DGS",
    ) -> List[Dict]:
        """
        Genera una secuencia de signos para una lista
        de conceptos.
        """

        if not isinstance(
            concepts,
            list,
        ):
            raise TypeError(
                "concepts debe ser una lista."
            )

        return [
            self.concept_to_sign(
                concept,
                language,
            )
            for concept in concepts
            if isinstance(
                concept,
                str,
            )
        ]


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    generator = SignGenerator()

    print(
        "=== SIGNMUSIC SIGN GENERATOR ==="
    )

    result = generator.generate_sequence(
        [
            "SAVE",
            "ME",
        ],
        language="DGS",
    )

    for item in result:
        print()
        print(
            item
        )

    print()
    print(
        "Status: OK"
    )