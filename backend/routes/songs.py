from flask import Blueprint, request

from semantic_analyzer import SemanticAnalyzer
from translation.dgs_translator import DGSTranslator
from sign_generator import SignGenerator
from keyframe_generator import KeyframeGenerator
from avatar_animation import AvatarAnimation
from avatar_player import AvatarPlayer


songs_bp = Blueprint("songs", __name__)

semantic_analyzer = SemanticAnalyzer()
dgs_translator = DGSTranslator()
sign_generator = SignGenerator()
keyframe_generator = KeyframeGenerator()
avatar_animation = AvatarAnimation()
avatar_player = AvatarPlayer()


# =========================================================
# SEARCH
# =========================================================

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


# =========================================================
# PROCESS SONG
# =========================================================

@songs_bp.route("/process", methods=["POST"])
def process():
    """
    Procesa una letra y genera:

    1. Análisis semántico línea por línea
    2. Traducción intermedia DGS línea por línea
    3. Signos DGS
    4. Keyframes de animación
    5. Preparación de huesos del avatar
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
    # 5. Generar keyframes
    # ---------------------------------------------------------

    animation = keyframe_generator.generate_animation_sequence(
        unique_concepts,
        bpm=bpm
    )

    # ---------------------------------------------------------
    # 6. Preparar huesos del avatar
    # ---------------------------------------------------------

    animation = avatar_animation.prepare_sequence(
        animation
    )

    # ---------------------------------------------------------
    # 7. Conceptos traducidos
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
    # 8. Respuesta final
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


# =========================================================
# AVATAR STATE
# =========================================================

@songs_bp.route("/avatar-state", methods=["POST"])
def avatar_state():
    """
    Devuelve el estado del avatar en un instante concreto
    de una letra procesada.

    Recibe:

        lyrics: letra de la canción
        bpm: BPM de la canción
        time: instante en segundos

    Devuelve:

        Estado interpolado de todos los huesos del avatar.
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
    time = data.get("time", 0.0)

    # ---------------------------------------------------------
    # 1. Validar BPM
    # ---------------------------------------------------------

    try:
        bpm = int(bpm)

        if bpm <= 0:
            raise ValueError

    except (TypeError, ValueError):
        return {
            "error": "El campo 'bpm' debe ser un número entero mayor que 0"
        }, 400

    # ---------------------------------------------------------
    # 2. Validar tiempo
    # ---------------------------------------------------------

    try:
        time = float(time)

        if time < 0:
            raise ValueError

    except (TypeError, ValueError):
        return {
            "error": "El campo 'time' debe ser un número mayor o igual que 0"
        }, 400

    # ---------------------------------------------------------
    # 3. Analizar letra
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
    # 4. Traducir a DGS
    # ---------------------------------------------------------

    translation = dgs_translator.translate_lines(
        analyses,
        language="DGS"
    )

    # ---------------------------------------------------------
    # 5. Extraer conceptos
    # ---------------------------------------------------------

    concepts = []

    for analysis in analyses:
        concepts.extend(
            analysis.get(
                "normalized_concepts",
                []
            )
        )

    unique_concepts = list(
        dict.fromkeys(concepts)
    )

    # ---------------------------------------------------------
    # 6. Generar signos
    # ---------------------------------------------------------

    signs = sign_generator.generate_sequence(
        unique_concepts,
        language="DGS"
    )

    # ---------------------------------------------------------
    # 7. Generar keyframes
    # ---------------------------------------------------------

    animation = keyframe_generator.generate_animation_sequence(
        unique_concepts,
        bpm=bpm
    )

    # ---------------------------------------------------------
    # 8. Preparar avatar
    # ---------------------------------------------------------

    prepared_animation = avatar_animation.prepare_sequence(
        animation
    )

    # ---------------------------------------------------------
    # 9. Obtener estado del avatar
    # ---------------------------------------------------------

    state = avatar_player.get_avatar_state(
        prepared_animation,
        time
    )

    # ---------------------------------------------------------
    # 10. Respuesta
    # ---------------------------------------------------------

    return {
        "status": "success",
        "language": "en",
        "sign_language": "DGS",
        "bpm": bpm,
        "time": time,
        "lyrics": lyrics,
        "concepts": unique_concepts,
        "signs": signs,
        "avatar": state,
    }, 200