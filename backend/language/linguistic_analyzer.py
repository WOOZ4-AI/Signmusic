from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any

from .language_detector import LanguageDetector


# ---------------------------------------------------------------------------
# REGEX
# ---------------------------------------------------------------------------

WORD_RE = re.compile(
    r"\b[\wÀ-ÖØ-öø-ÿĀ-žḀ-ỹ'’-]+\b",
    re.UNICODE,
)

WHITESPACE_RE = re.compile(r"\s+")


# ---------------------------------------------------------------------------
# NON-LEXICAL VOCALIZATIONS
# ---------------------------------------------------------------------------

NON_LEXICAL_PATTERNS = (
    "yeah",
    "yea",
    "yep",
    "nah",
    "uh",
    "uhh",
    "uhm",
    "um",
    "umm",
    "ah",
    "ahh",
    "oh",
    "ooh",
    "oooh",
    "woah",
    "wow",
    "hey",
    "la",
    "lalala",
    "na",
    "nananana",
    "brr",
    "brrr",
    "mmm",
    "hmm",
    "hmmm",
)


# ---------------------------------------------------------------------------
# DATA STRUCTURES
# ---------------------------------------------------------------------------

@dataclass
class TokenInfo:
    text: str
    normalized: str
    index: int
    is_word: bool
    is_repetition: bool
    is_non_lexical: bool


@dataclass
class SegmentInfo:
    index: int
    text: str
    normalized_text: str
    segment_type: str
    tokens: list[TokenInfo]
    repeated: bool
    word_count: int


# ---------------------------------------------------------------------------
# ANALYZER
# ---------------------------------------------------------------------------

class LinguisticAnalyzer:
    """
    First linguistic-analysis layer of Signmusic.

    Responsibilities:

        - detect language
        - preserve lyric structure
        - segment lyrics
        - tokenize text
        - detect repetitions
        - flag probable non-lexical vocalizations
        - produce stable structured data

    This layer intentionally does NOT:

        - translate
        - infer artistic intent
        - assign semantic meaning
        - generate signs
        - choose a target sign language
        - generate avatar motion
    """

    def __init__(
        self,
        language_detector: LanguageDetector | None = None,
    ) -> None:

        self.language_detector = (
            language_detector
            or LanguageDetector()
        )

    # ------------------------------------------------------------------
    # PUBLIC API
    # ------------------------------------------------------------------

    def analyze(
        self,
        lyrics: str,
    ) -> dict[str, Any]:

        if not isinstance(lyrics, str):
            raise TypeError(
                "lyrics must be a string"
            )

        original = lyrics

        normalized = (
            self._normalize_full_text(
                lyrics
            )
        )

        # --------------------------------------------------------------
        # EMPTY INPUT
        # --------------------------------------------------------------

        if not normalized:

            return {
                "status": "empty",
                "language": None,
                "language_name": None,
                "language_confidence": 0.0,
                "language_status": "empty",
                "original_text": original,
                "normalized_text": "",
                "segments": [],
                "global_tokens": [],
                "metadata": {
                    "character_count": len(
                        original
                    ),
                    "normalized_character_count": 0,
                    "word_count": 0,
                    "segment_count": 0,
                    "repetition_count": 0,
                    "non_lexical_count": 0,
                },
            }

        # --------------------------------------------------------------
        # LANGUAGE DETECTION
        # --------------------------------------------------------------

        prediction = (
            self.language_detector.detect(
                normalized
            )
        )

        (
            language_code,
            language_name,
            language_confidence,
            language_status,
        ) = self._normalize_language_prediction(
            prediction
        )

        # --------------------------------------------------------------
        # SEGMENTATION
        # --------------------------------------------------------------

        segments = self._segment_lyrics(
            original
        )

        if not segments:

            segments = [
                {
                    "index": 0,
                    "text": original.strip(),
                    "segment_type": "line",
                }
            ]

        # --------------------------------------------------------------
        # SEGMENT ANALYSIS
        # --------------------------------------------------------------

        analyzed_segments: list[
            SegmentInfo
        ] = []

        for segment in segments:

            analyzed = (
                self._analyze_segment(
                    index=segment["index"],
                    text=segment["text"],
                    segment_type=segment[
                        "segment_type"
                    ],
                )
            )

            analyzed_segments.append(
                analyzed
            )

        # --------------------------------------------------------------
        # GLOBAL TOKENS
        # --------------------------------------------------------------

        global_tokens = (
            self._build_global_token_list(
                analyzed_segments
            )
        )

        repetition_count = sum(
            1
            for token in global_tokens
            if token.is_repetition
        )

        non_lexical_count = sum(
            1
            for token in global_tokens
            if token.is_non_lexical
        )

        word_count = sum(
            segment.word_count
            for segment in analyzed_segments
        )

        # --------------------------------------------------------------
        # FINAL STATUS
        # --------------------------------------------------------------

        status = (
            "ok"
            if language_status
            in {
                "ok",
                "detected",
            }
            else language_status
        )

        # --------------------------------------------------------------
        # RESULT
        # --------------------------------------------------------------

        return {
            "status": status,

            "language": language_code,

            "language_name": language_name,

            "language_confidence": (
                language_confidence
            ),

            "language_status": (
                language_status
            ),

            "original_text": original,

            "normalized_text": normalized,

            "segments": [
                self._segment_to_dict(
                    segment
                )
                for segment
                in analyzed_segments
            ],

            "global_tokens": [
                asdict(token)
                for token
                in global_tokens
            ],

            "metadata": {
                "character_count": len(
                    original
                ),
                "normalized_character_count": (
                    len(normalized)
                ),
                "word_count": word_count,
                "segment_count": (
                    len(analyzed_segments)
                ),
                "repetition_count": (
                    repetition_count
                ),
                "non_lexical_count": (
                    non_lexical_count
                ),
            },
        }

    # ------------------------------------------------------------------
    # LANGUAGE PREDICTION NORMALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_language_prediction(
        prediction: Any,
    ) -> tuple[
        str | None,
        str | None,
        float,
        str,
    ]:
        """
        Normalize all currently supported LanguageDetector outputs.

        Supported forms include:

            {
                "language": "en",
                "confidence": 0.99,
                "status": "detected"
            }

        and:

            {
                "language": {
                    "code": "fr",
                    "name": "Francés",
                    "confidence": 0.99
                },
                "confidence": 0.99,
                "status": "detected"
            }

        and dataclass/object equivalents.
        """

        # --------------------------------------------------------------
        # ROOT VALUES
        # --------------------------------------------------------------

        if isinstance(
            prediction,
            dict,
        ):

            root_language = prediction.get(
                "language"
            )

            root_confidence = prediction.get(
                "confidence",
                0.0,
            )

            root_status = prediction.get(
                "status",
                "unknown",
            )

        else:

            root_language = getattr(
                prediction,
                "language",
                None,
            )

            root_confidence = getattr(
                prediction,
                "confidence",
                0.0,
            )

            root_status = getattr(
                prediction,
                "status",
                "unknown",
            )

        # --------------------------------------------------------------
        # NESTED LANGUAGE OBJECT
        # --------------------------------------------------------------

        language_code: str | None = None

        language_name: str | None = None

        nested_confidence: float | None = None

        if isinstance(
            root_language,
            dict,
        ):

            language_code = (
                root_language.get(
                    "code"
                )
            )

            language_name = (
                root_language.get(
                    "name"
                )
            )

            nested_confidence = (
                root_language.get(
                    "confidence"
                )
            )

        else:

            language_code = (
                root_language
                if isinstance(
                    root_language,
                    str,
                )
                else None
            )

        # --------------------------------------------------------------
        # OBJECT LANGUAGE
        # --------------------------------------------------------------

        if (
            language_code is None
            and root_language is not None
        ):

            language_code = getattr(
                root_language,
                "code",
                None,
            )

            language_name = getattr(
                root_language,
                "name",
                None,
            )

            nested_confidence = getattr(
                root_language,
                "confidence",
                None,
            )

        # --------------------------------------------------------------
        # CONFIDENCE
        # --------------------------------------------------------------

        confidence_value = (
            root_confidence
        )

        if (
            confidence_value is None
            or not isinstance(
                confidence_value,
                (int, float),
            )
        ):

            confidence_value = (
                nested_confidence
                if nested_confidence
                is not None
                else 0.0
            )

        try:

            confidence = float(
                confidence_value
            )

        except (
            TypeError,
            ValueError,
        ):

            confidence = 0.0

        # --------------------------------------------------------------
        # STATUS
        # --------------------------------------------------------------

        if root_status is None:
            status = "unknown"
        else:
            status = str(
                root_status
            )

        return (
            language_code,
            language_name,
            confidence,
            status,
        )

    # ------------------------------------------------------------------
    # TEXT NORMALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_full_text(
        text: str,
    ) -> str:

        text = text.replace(
            "\r\n",
            "\n",
        )

        text = text.replace(
            "\r",
            "\n",
        )

        lines = [
            WHITESPACE_RE.sub(
                " ",
                line,
            ).strip()
            for line in text.split(
                "\n"
            )
        ]

        lines = [
            line
            for line in lines
            if line
        ]

        return "\n".join(
            lines
        )

    @staticmethod
    def _normalize_segment(
        text: str,
    ) -> str:

        return WHITESPACE_RE.sub(
            " ",
            text.strip(),
        )

    # ------------------------------------------------------------------
    # SEGMENTATION
    # ------------------------------------------------------------------

    def _segment_lyrics(
        self,
        lyrics: str,
    ) -> list[dict[str, Any]]:

        lyrics = lyrics.replace(
            "\r\n",
            "\n",
        )

        lyrics = lyrics.replace(
            "\r",
            "\n",
        )

        raw_lines = lyrics.split(
            "\n"
        )

        segments: list[
            dict[str, Any]
        ] = []

        index = 0

        for raw_line in raw_lines:

            line = (
                self._normalize_segment(
                    raw_line
                )
            )

            if not line:
                continue

            sentence_parts = (
                self._split_sentences(
                    line
                )
            )

            if len(sentence_parts) <= 1:

                segments.append(
                    {
                        "index": index,
                        "text": line,
                        "segment_type": "line",
                    }
                )

                index += 1

                continue

            for sentence in sentence_parts:

                sentence = (
                    self._normalize_segment(
                        sentence
                    )
                )

                if not sentence:
                    continue

                segments.append(
                    {
                        "index": index,
                        "text": sentence,
                        "segment_type": "sentence",
                    }
                )

                index += 1

        return segments

    @staticmethod
    def _split_sentences(
        text: str,
    ) -> list[str]:

        parts = re.split(
            r"(?<=[.!?…。！？])\s+",
            text,
        )

        return [
            part.strip()
            for part in parts
            if part.strip()
        ]

    # ------------------------------------------------------------------
    # SEGMENT ANALYSIS
    # ------------------------------------------------------------------

    def _analyze_segment(
        self,
        index: int,
        text: str,
        segment_type: str,
    ) -> SegmentInfo:

        normalized_text = (
            self._normalize_segment(
                text
            )
        )

        matches = list(
            WORD_RE.finditer(
                normalized_text
            )
        )

        normalized_words = [
            self._normalize_token(
                match.group(0)
            )
            for match in matches
        ]

        frequencies: dict[
            str,
            int,
        ] = {}

        for word in normalized_words:

            frequencies[word] = (
                frequencies.get(
                    word,
                    0,
                )
                + 1
            )

        tokens: list[
            TokenInfo
        ] = []

        for token_index, match in enumerate(
            matches
        ):

            raw_token = match.group(0)

            normalized_token = (
                self._normalize_token(
                    raw_token
                )
            )

            tokens.append(
                TokenInfo(
                    text=raw_token,
                    normalized=normalized_token,
                    index=token_index,
                    is_word=True,
                    is_repetition=(
                        frequencies.get(
                            normalized_token,
                            0,
                        )
                        > 1
                    ),
                    is_non_lexical=(
                        self._is_non_lexical(
                            normalized_token
                        )
                    ),
                )
            )

        repeated = any(
            token.is_repetition
            for token in tokens
        )

        return SegmentInfo(
            index=index,
            text=text,
            normalized_text=normalized_text,
            segment_type=segment_type,
            tokens=tokens,
            repeated=repeated,
            word_count=len(tokens),
        )

    # ------------------------------------------------------------------
    # TOKEN NORMALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def _normalize_token(
        token: str,
    ) -> str:

        token = token.strip().lower()

        token = token.replace(
            "’",
            "'",
        )

        return token

    # ------------------------------------------------------------------
    # NON-LEXICAL DETECTION
    # ------------------------------------------------------------------

    @staticmethod
    def _is_non_lexical(
        token: str,
    ) -> bool:

        if token in NON_LEXICAL_PATTERNS:
            return True

        if re.fullmatch(
            r"[aeiou]{3,}",
            token,
        ):
            return True

        if re.fullmatch(
            r"[mh]{3,}",
            token,
        ):
            return True

        return False

    # ------------------------------------------------------------------
    # GLOBAL TOKEN STREAM
    # ------------------------------------------------------------------

    @staticmethod
    def _build_global_token_list(
        segments: list[
            SegmentInfo
        ],
    ) -> list[TokenInfo]:

        global_tokens: list[
            TokenInfo
        ] = []

        global_index = 0

        for segment in segments:

            for token in segment.tokens:

                global_tokens.append(
                    TokenInfo(
                        text=token.text,
                        normalized=token.normalized,
                        index=global_index,
                        is_word=token.is_word,
                        is_repetition=(
                            token.is_repetition
                        ),
                        is_non_lexical=(
                            token.is_non_lexical
                        ),
                    )
                )

                global_index += 1

        return global_tokens

    # ------------------------------------------------------------------
    # SERIALIZATION
    # ------------------------------------------------------------------

    @staticmethod
    def _segment_to_dict(
        segment: SegmentInfo,
    ) -> dict[str, Any]:

        return {
            "index": segment.index,
            "text": segment.text,
            "normalized_text": (
                segment.normalized_text
            ),
            "segment_type": (
                segment.segment_type
            ),
            "tokens": [
                asdict(token)
                for token
                in segment.tokens
            ],
            "repeated": (
                segment.repeated
            ),
            "word_count": (
                segment.word_count
            ),
        }


# ---------------------------------------------------------------------------
# DEBUG OUTPUT
# ---------------------------------------------------------------------------

def _print_analysis(
    result: dict[str, Any],
) -> None:

    print("\n" + "=" * 72)

    print(
        "SIGNMUSIC LINGUISTIC ANALYZER"
    )

    print("=" * 72)

    print(
        f"Status:       "
        f"{result['status']}"
    )

    print(
        f"Language:     "
        f"{result['language']}"
    )

    print(
        f"Language name: "
        f"{result['language_name']}"
    )

    print(
        f"Confidence:   "
        f"{result['language_confidence']:.4f}"
    )

    print(
        f"Language status: "
        f"{result['language_status']}"
    )

    print("\nSegments:")

    for segment in result[
        "segments"
    ]:

        print(
            f"  [{segment['index']}] "
            f"{segment['segment_type']}: "
            f"{segment['text']}"
        )

        for token in segment[
            "tokens"
        ]:

            flags: list[str] = []

            if token[
                "is_repetition"
            ]:
                flags.append(
                    "repetition"
                )

            if token[
                "is_non_lexical"
            ]:
                flags.append(
                    "non_lexical"
                )

            flag_text = (
                f" ({', '.join(flags)})"
                if flags
                else ""
            )

            print(
                f"      - "
                f"{token['text']} "
                f"-> "
                f"{token['normalized']}"
                f"{flag_text}"
            )

    print("\nMetadata:")

    for key, value in result[
        "metadata"
    ].items():

        print(
            f"  {key}: {value}"
        )


# ---------------------------------------------------------------------------
# TEST
# ---------------------------------------------------------------------------

def main() -> None:

    analyzer = (
        LinguisticAnalyzer()
    )

    examples = [
        "Save me, save you.",
        "Me muero por ti.",
        "Brrr, bebé, ven aquí.",
        "Je t'aime, je t'aime encore.",
        (
            "I need you tonight, "
            "I need you by my side, "
            "because every time I see you "
            "I feel alive again."
        ),
    ]

    for lyrics in examples:

        print(
            f"\nTEXT: {lyrics}"
        )

        try:

            result = (
                analyzer.analyze(
                    lyrics
                )
            )

            _print_analysis(
                result
            )

        except Exception as exc:

            print(
                f"ERROR: "
                f"{type(exc).__name__}: "
                f"{exc}"
            )


if __name__ == "__main__":
    main()