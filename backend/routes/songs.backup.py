from flask import Blueprint, request

from semantic_analyzer import SemanticAnalyzer
from translation.dgs_translator import DGSTranslator
from sign_generator import SignGenerator
from keyframe_generator import KeyframeGenerator


songs_bp = Blueprint("songs", __name__)

semantic_analyzer = SemanticAnalyzer()
dgs_translator = DGSTranslator()
sign_generator = SignGenerator()
keyframe_generator = KeyframeGenerator()


@songs_bp.route("/search", methods=["GET"])
def search():
    """
    Buscar canciones.

    Por ahora devuelve una respuesta estructurada.
    La búsqueda real se conectará posteriormente con la base de datos
    y/o una fuente externa.
    """
    query = request.args.get("q", "").strip()

    if not query:
        return {
            "error": "Debes proporcionar un término de búsqueda"
        }, 400

    return {
        "query": query,
        "results": [],
        "message": "Búsqueda preparada; fuente de canciones pendiente"
    }, 200


@songs_bp.route("/process", methods=["POST"])
def process():
    """
    Procesa una letra y genera:

    1. Análisis semántico línea por línea
    2. Traducción intermedia DGS línea por línea
    3. Signos DGS
    4. Keyframes de animación
    """

    data = request.get_json(silent=True)

    if not data:
        return {
            "error": "El cuerpo de la petición debe ser JSON"
        }, 400

    lyrics = data.get("lyrics")

    if not lyrics or not isinstance(lyrics, str):
        return {
            "error": "El campo 'lyrics' es obligatorio"
        }, 400

    bpm = data.get("bpm", 120)

    try:
        bpm = int(bpm)

        if bpm <= 0:
            raise ValueError

    except (TypeError, ValueError):
        return {
            "error": "El campo 'bpm' debe ser un número entero mayor que 0"
        }, 400

    # ---------------------------------------------------------
    # 1. Analizar la letra línea por línea
    # ---------------------------------------------------------

    lines = [
        line.strip()
        for line in lyrics.splitlines()
        if line.strip()
    ]

    if not lines:
        return {
            "error": "La letra no contiene líneas válidas"
        }, 400

    analyses = []

    for line in lines:
        analysis = semantic_analyzer.analyze_line(line)
        analyses.append(analysis)

    # ---------------------------------------------------------
    # 2. Traducir línea por línea
    # ---------------------------------------------------------

    translation = dgs_translator.translate_lines(
        analyses,
        language="DGS"
    )

    # ---------------------------------------------------------
    # 3. Extraer conceptos globales
    # ---------------------------------------------------------

    concepts = []

    for analysis in analyses:
        concepts.extend(
            analysis.get("normalized_concepts", [])
        )

    unique_concepts = list(
        dict.fromkeys(concepts)
    )

    # ---------------------------------------------------------
    # 4. Generar signos
    # ---------------------------------------------------------

    signs = sign_generator.generate_sequence(
        unique_concepts,
        language="DGS"
    )

    # ---------------------------------------------------------
    # 5. Generar animación
    # ---------------------------------------------------------

    animation = keyframe_generator.generate_animation_sequence(
    unique_concepts,
    bpm=bpm
    )

    # ---------------------------------------------------------
    # 6. Conceptos traducidos
    # ---------------------------------------------------------

    translated_concepts = [
        unit["concept"]
        for line in translation["lines"]
        for unit in line["translation_units"]
    ]

    translated_concepts = list(
        dict.fromkeys(translated_concepts)
    )

    # ---------------------------------------------------------
    # 7. Respuesta final
    # ---------------------------------------------------------

    return {
        "status": "success",
        "language": "en",
        "sign_language": "DGS",
        "bpm": bpm,
        "lyrics": lyrics,

        "lines": analyses,

        "concepts": unique_concepts,

        "translation": translation,

        "translated_concepts": translated_concepts,

        "signs": signs,

        "animation": animation,
    }, 200