from typing import Dict, List, Any
import re


class SongProcessor:
    """
    Procesa la información básica de una canción antes de enviarla
    al sistema de generación de animaciones de Signmusic.

    Responsabilidades:

    1. Validar los datos de la canción.
    2. Normalizar la letra.
    3. Separar la letra en palabras.
    4. Mantener el orden original de las palabras.
    5. Preparar una estructura que pueda utilizar posteriormente
       KeyframeGenerator.

    IMPORTANTE:
    Esta clase NO traduce todavía la letra a lengua de signos.
    Esa capa se implementará posteriormente.
    """

    def create_animation_input(self, processed_song):
        """
        Convierte una canción procesada en el formato
        necesario para generar una animación.
        """

        if not processed_song:
            raise ValueError("La canción procesada está vacía.")

        concepts = processed_song.get("concepts", [])

        if not concepts:
            raise ValueError(
                "La canción no contiene conceptos para animar."
            )

        return {
            "title": processed_song.get("title", "Untitled"),
            "concepts": concepts,
            "concept_count": len(concepts),
            "status": "ready_for_keyframe_generation",
        }

    # =========================================================
    # INICIALIZACIÓN
    # =========================================================

    def __init__(self):
        pass

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    def validate_song(
        self,
        song: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Valida la estructura básica de una canción.
        """

        errors: List[str] = []

        if not isinstance(song, dict):
            return {
                "valid": False,
                "errors": [
                    "La canción debe ser un objeto"
                ],
            }

        title = song.get("title")
        lyrics = song.get("lyrics")

        if title is None:
            errors.append("Falta 'title'")

        elif not isinstance(title, str):
            errors.append("'title' debe ser texto")

        elif not title.strip():
            errors.append("'title' no puede estar vacío")

        if lyrics is None:
            errors.append("Falta 'lyrics'")

        elif not isinstance(lyrics, str):
            errors.append("'lyrics' debe ser texto")

        elif not lyrics.strip():
            errors.append("'lyrics' no puede estar vacía")

        return {
            "valid": len(errors) == 0,
            "errors": errors,
        }

    # =========================================================
    # NORMALIZACIÓN
    # =========================================================

    def normalize_lyrics(
        self,
        lyrics: str,
    ) -> str:
        """
        Normaliza una letra sin modificar su contenido
        lingüístico de forma significativa.

        Se eliminan espacios innecesarios y se normalizan
        los saltos de línea.
        """

        if not isinstance(lyrics, str):
            raise TypeError(
                "lyrics debe ser texto"
            )

        # Normalizar saltos de línea
        normalized = lyrics.replace(
            "\r\n",
            "\n",
        )

        normalized = normalized.replace(
            "\r",
            "\n",
        )

        # Eliminar espacios al principio/final
        lines = [
            line.strip()
            for line in normalized.split("\n")
        ]

        # Eliminar líneas completamente vacías
        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(lines)

    # =========================================================
    # TOKENIZACIÓN
    # =========================================================

    def tokenize_lyrics(
        self,
        lyrics: str,
    ) -> List[str]:
        """
        Divide la letra en palabras manteniendo su orden.

        La puntuación se elimina de los extremos de las palabras,
        pero se conserva el contenido textual.
        """

        if not isinstance(lyrics, str):
            raise TypeError(
                "lyrics debe ser texto"
            )

        normalized = self.normalize_lyrics(
            lyrics
        )

        # Detectar secuencias de caracteres alfanuméricos,
        # incluyendo letras Unicode.
        tokens = re.findall(
            r"[^\W_]+(?:['’-][^\W_]+)*",
            normalized,
            flags=re.UNICODE,
        )

        return tokens

    # =========================================================
    # PROCESAMIENTO DE CANCIÓN
    # =========================================================

    def process_song(
        self,
        song: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Procesa una canción completa.

        Devuelve una estructura preparada para las siguientes
        capas del sistema.
        """

        validation = self.validate_song(
            song
        )

        if not validation["valid"]:
            raise ValueError(
                "Canción inválida: "
                + "; ".join(
                    validation["errors"]
                )
            )

        title = song["title"].strip()

        normalized_lyrics = (
            self.normalize_lyrics(
                song["lyrics"]
            )
        )

        words = self.tokenize_lyrics(
            normalized_lyrics
        )

        return {
            "title": title,
            "original_lyrics": song["lyrics"],
            "normalized_lyrics": normalized_lyrics,
            "words": words,
            "word_count": len(words),
            "status": "processed",
        }

    # =========================================================
    # PREPARACIÓN PARA KEYFRAME GENERATOR
    # =========================================================

    def prepare_for_animation(
        self,
        processed_song: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Prepara las palabras procesadas para la futura capa
        de traducción y generación de animaciones.

        Actualmente las palabras se conservan como conceptos
        experimentales.

        La traducción real a lengua de signos se implementará
        posteriormente.
        """

        if not isinstance(
            processed_song,
            dict,
        ):
            raise TypeError(
                "processed_song debe ser un objeto"
            )

        words = processed_song.get(
            "words",
            [],
        )

        if not isinstance(words, list):
            raise ValueError(
                "'words' debe ser una lista"
            )

        concepts = []

        for word in words:

            if not isinstance(
                word,
                str,
            ):
                continue

            concept = word.upper().strip()

            if concept:
                concepts.append(
                    concept
                )

        return {
            "title": processed_song.get(
                "title"
            ),
            "concepts": concepts,
            "concept_count": len(
                concepts
            ),
            "status": "ready_for_animation",
        }