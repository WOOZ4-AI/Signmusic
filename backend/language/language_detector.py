from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import re


try:
    import torch
    from transformers import (
        AutoTokenizer,
        AutoModelForSequenceClassification,
    )
except ImportError:
    torch = None
    AutoTokenizer = None
    AutoModelForSequenceClassification = None


@dataclass
class LanguagePrediction:
    """
    Una predicción de idioma.

    code:
        Código interno ISO / normalizado.

    name:
        Nombre legible del idioma.

    confidence:
        Probabilidad aproximada producida por el modelo.
    """

    code: str
    name: str
    confidence: float

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LanguageDetector:
    """
    Detector multilingüe de idioma para Signmusic.

    Modelo utilizado:

        papluca/xlm-roberta-base-language-detection

    El modelo cubre 21 idiomas.

    IMPORTANTE
    ----------

    Este módulo únicamente responde:

        "¿En qué idioma parece estar escrito este texto?"

    NO intenta:

        - traducir
        - interpretar la canción
        - descubrir la intención artística
        - detectar emociones
        - convertir a lengua de signos
    """

    MODEL_NAME = (
        "papluca/"
        "xlm-roberta-base-language-detection"
    )

    # ---------------------------------------------------------
    # Etiquetas conocidas del modelo
    # ---------------------------------------------------------

    LANGUAGE_NAMES = {
        "ar": "Árabe",
        "bg": "Búlgaro",
        "de": "Alemán",
        "el": "Griego",
        "en": "Inglés",
        "es": "Español",
        "fr": "Francés",
        "hi": "Hindi",
        "it": "Italiano",
        "ja": "Japonés",
        "ko": "Coreano",
        "nl": "Neerlandés",
        "pl": "Polaco",
        "pt": "Portugués",
        "ru": "Ruso",
        "sw": "Suajili",
        "th": "Tailandés",
        "tr": "Turco",
        "ur": "Urdu",
        "vi": "Vietnamita",
        "zh": "Chino",
    }

    # Algunos modelos devuelven etiquetas diferentes.
    LABEL_ALIASES = {
        "arabic": "ar",
        "bulgarian": "bg",
        "german": "de",
        "greek": "el",
        "english": "en",
        "spanish": "es",
        "french": "fr",
        "hindi": "hi",
        "italian": "it",
        "japanese": "ja",
        "korean": "ko",
        "dutch": "nl",
        "polish": "pl",
        "portuguese": "pt",
        "russian": "ru",
        "swahili": "sw",
        "thai": "th",
        "turkish": "tr",
        "urdu": "ur",
        "vietnamese": "vi",
        "chinese": "zh",
    }

    # ---------------------------------------------------------
    # Constructor
    # ---------------------------------------------------------

    def __init__(
        self,
        model_name: str = MODEL_NAME,
        device: Optional[str] = None,
        min_characters: int = 20,
    ) -> None:

        if min_characters < 1:
            raise ValueError(
                "min_characters debe ser mayor que 0."
            )

        self.model_name = model_name
        self.min_characters = int(
            min_characters
        )

        self.tokenizer = None
        self.model = None

        self._loaded = False

        # -----------------------------------------------------
        # Device
        # -----------------------------------------------------

        if device is not None:

            self.device = device

        elif torch is not None and torch.cuda.is_available():

            self.device = "cuda"

        else:

            self.device = "cpu"

    # =========================================================
    # CARGA PEREZOSA DEL MODELO
    # =========================================================

    def _load_model(self) -> None:
        """
        Carga tokenizer + modelo únicamente cuando hacen falta.
        """

        if self._loaded:
            return

        if (
            torch is None
            or AutoTokenizer is None
            or AutoModelForSequenceClassification is None
        ):
            raise RuntimeError(
                "Faltan dependencias de Transformers/Torch."
            )

        self.tokenizer = (
            AutoTokenizer.from_pretrained(
                self.model_name
            )
        )

        self.model = (
            AutoModelForSequenceClassification
            .from_pretrained(
                self.model_name
            )
        )

        self.model.to(self.device)
        self.model.eval()

        self._loaded = True

    # =========================================================
    # NORMALIZACIÓN
    # =========================================================

    @staticmethod
    def normalize_text(
        text: str,
    ) -> str:
        """
        Normaliza texto sin destruir su contenido.
        """

        if not isinstance(
            text,
            str,
        ):
            raise TypeError(
                "text debe ser un string."
            )

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text.strip()

    # =========================================================
    # LONGITUD ÚTIL
    # =========================================================

    @staticmethod
    def _meaningful_character_count(
        text: str,
    ) -> int:
        """
        Cuenta caracteres alfanuméricos.

        Esto ayuda a no confiar demasiado en textos como:

            "brrr"
            "yeah"
            "uh"
        """

        return len(
            re.findall(
                r"\w",
                text,
                flags=re.UNICODE,
            )
        )

    # =========================================================
    # NORMALIZAR LABEL
    # =========================================================

    @classmethod
    def normalize_label(
        cls,
        label: str,
    ) -> str:
        """
        Convierte una etiqueta del modelo a un código interno.
        """

        if not isinstance(
            label,
            str,
        ):
            raise TypeError(
                "label debe ser un string."
            )

        normalized = (
            label
            .strip()
            .lower()
        )

        if normalized in cls.LANGUAGE_NAMES:
            return normalized

        if normalized in cls.LABEL_ALIASES:
            return cls.LABEL_ALIASES[
                normalized
            ]

        # Algunos clasificadores utilizan
        # prefijos como "LABEL_0". Los dejamos
        # explícitamente desconocidos.
        return normalized

    # =========================================================
    # NOMBRE DEL IDIOMA
    # =========================================================

    @classmethod
    def language_name(
        cls,
        code: str,
    ) -> str:

        normalized = cls.normalize_label(
            code
        )

        return cls.LANGUAGE_NAMES.get(
            normalized,
            normalized,
        )

    # =========================================================
    # PREDICCIÓN
    # =========================================================

    def detect(
        self,
        text: str,
        top_k: int = 3,
    ) -> Dict[str, Any]:
        """
        Detecta el idioma predominante del texto.

        Devuelve:

            {
                "language": {...},
                "alternatives": [...],
                "confidence": 0.98,
                "status": "detected"
            }
        """

        if not isinstance(
            text,
            str,
        ):
            raise TypeError(
                "text debe ser un string."
            )

        normalized_text = (
            self.normalize_text(
                text
            )
        )

        if not normalized_text:
            return {
                "language": None,
                "alternatives": [],
                "confidence": 0.0,
                "status": "empty",
            }

        meaningful_count = (
            self._meaningful_character_count(
                normalized_text
            )
        )

        if (
            meaningful_count
            < self.min_characters
        ):
            return {
                "language": None,
                "alternatives": [],
                "confidence": 0.0,
                "status": "insufficient_text",
            }

        if top_k < 1:
            raise ValueError(
                "top_k debe ser mayor que 0."
            )

        top_k = min(
            int(top_k),
            10,
        )

        # -----------------------------------------------------
        # Cargar modelo
        # -----------------------------------------------------

        self._load_model()

        # -----------------------------------------------------
        # Tokenización
        # -----------------------------------------------------

        inputs = self.tokenizer(
            normalized_text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
        )

        inputs = {
            key: value.to(
                self.device
            )
            for key, value in inputs.items()
        }

        # -----------------------------------------------------
        # Inferencia
        # -----------------------------------------------------

        with torch.no_grad():

            outputs = self.model(
                **inputs
            )

            probabilities = (
                torch.softmax(
                    outputs.logits,
                    dim=-1,
                )[0]
            )

        scores, indices = torch.topk(
            probabilities,
            k=min(
                top_k,
                probabilities.shape[-1],
            ),
        )

        predictions: List[
            LanguagePrediction
        ] = []

        # -----------------------------------------------------
        # Convertir resultados
        # -----------------------------------------------------

        for score, index in zip(
            scores.tolist(),
            indices.tolist(),
        ):

            raw_label = (
                self.model.config.id2label[
                    index
                ]
            )

            code = (
                self.normalize_label(
                    raw_label
                )
            )

            predictions.append(
                LanguagePrediction(
                    code=code,
                    name=self.language_name(
                        code
                    ),
                    confidence=float(
                        score
                    ),
                )
            )

        if not predictions:
            return {
                "language": None,
                "alternatives": [],
                "confidence": 0.0,
                "status": "undetected",
            }

        primary = predictions[0]

        return {
            "language": (
                primary.to_dict()
            ),
            "alternatives": [
                prediction.to_dict()
                for prediction
                in predictions[1:]
            ],
            "confidence": float(
                primary.confidence
            ),
            "status": "detected",
        }

    # =========================================================
    # DETECCIÓN SIMPLE
    # =========================================================

    def detect_code(
        self,
        text: str,
    ) -> Optional[str]:
        """
        Devuelve únicamente el código del idioma.
        """

        result = self.detect(
            text
        )

        language = result.get(
            "language"
        )

        if not language:
            return None

        return language.get(
            "code"
        )

    # =========================================================
    # DETECCIÓN DE VARIOS BLOQUES
    # =========================================================

    def detect_segments(
        self,
        segments: List[str],
    ) -> List[Dict[str, Any]]:
        """
        Detecta el idioma de múltiples segmentos.

        Esto será útil posteriormente para canciones
        con código alternado / frases multilingües.
        """

        if not isinstance(
            segments,
            list,
        ):
            raise TypeError(
                "segments debe ser una lista."
            )

        results = []

        for index, segment in enumerate(
            segments
        ):

            result = self.detect(
                segment
            )

            result["segment_index"] = index
            result["text"] = segment

            results.append(
                result
            )

        return results

    # =========================================================
    # INFORMACIÓN
    # =========================================================

    def get_configuration(
        self,
    ) -> Dict[str, Any]:

        return {
            "model": self.model_name,
            "device": self.device,
            "loaded": self._loaded,
            "supported_languages": sorted(
                self.LANGUAGE_NAMES.keys()
            ),
            "supported_language_count": len(
                self.LANGUAGE_NAMES
            ),
            "min_characters": (
                self.min_characters
            ),
        }


# =============================================================
# PRUEBA DIRECTA
# =============================================================

if __name__ == "__main__":

    print(
        "=== SIGNMUSIC LANGUAGE DETECTOR ==="
    )

    detector = LanguageDetector()

    print()
    print(
        "Configuration:"
    )

    print(
        detector.get_configuration()
    )

    tests = [
        (
            "Español",
            (
                "Esta canción habla de amor "
                "y de una noche que nunca termina."
            ),
        ),
        (
            "English",
            (
                "I still remember the night "
                "when everything changed."
            ),
        ),
        (
            "Deutsch",
            (
                "Ich werde dich niemals vergessen "
                "und immer an diese Nacht denken."
            ),
        ),
        (
            "Français",
            (
                "Je pense encore à toi "
                "chaque nuit quand je ferme les yeux."
            ),
        ),
        (
            "Italiano",
            (
                "Non riesco a smettere di pensare "
                "a te ogni giorno."
            ),
        ),
    ]

    for expected, text in tests:

        print()
        print(
            f"Expected: {expected}"
        )

        result = detector.detect(
            text
        )

        print(
            "Result:"
        )

        print(
            result
        )

    print()
    print(
        "Short text test:"
    )

    print(
        detector.detect(
            "yeah"
        )
    )

    print()
    print(
        "Status: OK"
    )