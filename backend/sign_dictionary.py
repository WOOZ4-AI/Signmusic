import json
import os
from typing import Dict, Optional, Tuple

from sign_model import SignModel


class SignDictionary:
    """
    Diccionario central de signos de Signmusic.

    Los signos se cargan desde:

        data/signs/<language>/*.json

    La clave interna es:

        (language, concept)

    Esto evita que un signo ASL pueda sobrescribir
    accidentalmente un signo DGS con el mismo concepto.
    """

    DEFAULT_LANGUAGE = "DGS"

    def __init__(
        self,
    ):

        self._signs: Dict[
            Tuple[str, str],
            SignModel,
        ] = {}

        self.project_root = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
            )
        )

        self.signs_root = os.path.join(
            self.project_root,
            "data",
            "signs",
        )

        self.load_from_disk()

    # =========================================================
    # NORMALIZAR IDIOMA
    # =========================================================

    @staticmethod
    def _normalize_language(
        language: Optional[str],
    ) -> str:

        if language is None:
            return SignDictionary.DEFAULT_LANGUAGE

        normalized = str(
            language
        ).strip().upper()

        if not normalized:
            return SignDictionary.DEFAULT_LANGUAGE

        return normalized

    # =========================================================
    # NORMALIZAR CONCEPTO
    # =========================================================

    @staticmethod
    def _normalize_concept(
        concept: str,
    ) -> str:

        return str(
            concept
        ).strip().upper()

    # =========================================================
    # CLAVE
    # =========================================================

    def _make_key(
        self,
        language: str,
        concept: str,
    ) -> Tuple[str, str]:

        return (
            self._normalize_language(
                language
            ),
            self._normalize_concept(
                concept
            ),
        )

    # =========================================================
    # CARGAR SIGNOS
    # =========================================================

    def load_from_disk(
        self,
    ) -> None:
        """
        Carga todos los JSON encontrados en:

            data/signs/<language>/
        """

        if not os.path.exists(
            self.signs_root
        ):
            return

        for language in os.listdir(
            self.signs_root
        ):

            language_path = os.path.join(
                self.signs_root,
                language,
            )

            if not os.path.isdir(
                language_path
            ):
                continue

            language_code = (
                self._normalize_language(
                    language
                )
            )

            for filename in os.listdir(
                language_path
            ):

                if not filename.lower().endswith(
                    ".json"
                ):
                    continue

                filepath = os.path.join(
                    language_path,
                    filename,
                )

                self._load_file(
                    filepath,
                    language_code,
                )

    # =========================================================
    # CARGAR ARCHIVO
    # =========================================================

    def _load_file(
        self,
        filepath: str,
        directory_language: str,
    ) -> None:

        try:

            with open(
                filepath,
                "r",
                encoding="utf-8",
            ) as file:

                data = json.load(
                    file
                )

            sign = (
                SignModel.from_dict(
                    data
                )
            )

            errors = sign.validate()

            if errors:

                print(
                    f"WARNING: signo inválido "
                    f"en {filepath}"
                )

                for error in errors:

                    print(
                        f"  - {error}"
                    )

                return

            # -------------------------------------------------
            # El idioma declarado dentro del JSON tiene
            # prioridad sobre el nombre de carpeta.
            # -------------------------------------------------

            language = (
                self._normalize_language(
                    sign.language
                    or directory_language
                )
            )

            sign.language = language

            self.register_sign(
                sign
            )

            print(
                f"Signo cargado: "
                f"{sign.concept} "
                f"({sign.language})"
            )

        except Exception as exc:

            print(
                f"ERROR cargando "
                f"{filepath}: {exc}"
            )

    # =========================================================
    # REGISTRO
    # =========================================================

    def register_sign(
        self,
        sign: SignModel,
    ) -> None:

        if not isinstance(
            sign,
            SignModel,
        ):
            raise TypeError(
                "sign debe ser una instancia "
                "de SignModel."
            )

        concept = (
            self._normalize_concept(
                sign.concept
            )
        )

        language = (
            self._normalize_language(
                sign.language
            )
        )

        sign.concept = concept
        sign.language = language

        key = self._make_key(
            language,
            concept,
        )

        self._signs[
            key
        ] = sign

    # =========================================================
    # CONSULTA
    # =========================================================

    def get_sign(
        self,
        concept: str,
        language: str = DEFAULT_LANGUAGE,
    ) -> Optional[SignModel]:

        if not concept:
            return None

        key = self._make_key(
            language,
            concept,
        )

        return self._signs.get(
            key
        )

    # =========================================================
    # EXISTENCIA
    # =========================================================

    def has_sign(
        self,
        concept: str,
        language: str = DEFAULT_LANGUAGE,
    ) -> bool:

        return (
            self.get_sign(
                concept,
                language,
            )
            is not None
        )

    # =========================================================
    # ESTADO
    # =========================================================

    def get_status(
        self,
        concept: str,
        language: str = DEFAULT_LANGUAGE,
    ) -> str:

        sign = self.get_sign(
            concept,
            language,
        )

        if sign is None:
            return "unavailable"

        return sign.status

    # =========================================================
    # IDIOMAS DISPONIBLES
    # =========================================================

    def get_supported_languages(self):

        languages = {
            language
            for language, _ in self._signs.keys()
        }

        return sorted(
            languages
        )

    # =========================================================
    # CONCEPTOS DE UN IDIOMA
    # =========================================================

    def get_supported_concepts(
        self,
        language: str = DEFAULT_LANGUAGE,
    ):

        normalized_language = (
            self._normalize_language(
                language
            )
        )

        return sorted(
            concept
            for (
                stored_language,
                concept
            )
            in self._signs.keys()
            if stored_language
            == normalized_language
        )

    # =========================================================
    # SERIALIZACIÓN
    # =========================================================

    def export_all(
        self,
        language: Optional[str] = None,
    ):

        if language is None:

            return {
                f"{stored_language}:{concept}":
                    sign.to_dict()
                for (
                    stored_language,
                    concept
                ), sign
                in self._signs.items()
            }

        normalized_language = (
            self._normalize_language(
                language
            )
        )

        return {
            concept: sign.to_dict()
            for (
                stored_language,
                concept
            ), sign
            in self._signs.items()
            if stored_language
            == normalized_language
        }


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    dictionary = SignDictionary()

    print(
        "\n=== SIGNMUSIC SIGN DICTIONARY ==="
    )

    print(
        "Idiomas:",
        dictionary.get_supported_languages(),
    )

    print(
        "\nConceptos DGS:",
        dictionary.get_supported_concepts(
            "DGS"
        ),
    )

    print(
        "Conceptos ASL:",
        dictionary.get_supported_concepts(
            "ASL"
        ),
    )

    dgs_save = (
        dictionary.get_sign(
            "SAVE",
            "DGS",
        )
    )

    asl_save = (
        dictionary.get_sign(
            "SAVE",
            "ASL",
        )
    )

    print(
        "\nDGS SAVE:"
    )

    print(
        dgs_save.to_dict()
        if dgs_save
        else None
    )

    print(
        "\nASL SAVE:"
    )

    print(
        asl_save.to_dict()
        if asl_save
        else None
    )

    print(
        "\nEstado DGS SAVE:",
        dictionary.get_status(
            "SAVE",
            "DGS",
        ),
    )

    print(
        "Estado DGS YOU:",
        dictionary.get_status(
            "YOU",
            "DGS",
        ),
    )

    print(
        "Estado ASL YOU:",
        dictionary.get_status(
            "YOU",
            "ASL",
        ),
    )

    print(
        "\nStatus: OK"
    )