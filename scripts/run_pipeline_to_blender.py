import json
import os
import sys
from pathlib import Path


# ============================================================
# ROOT DEL PROYECTO
# ============================================================

PROJECT_ROOT = Path(
    __file__
).resolve().parent.parent

BACKEND_DIR = (
    PROJECT_ROOT
    / "backend"
)

BLENDER_DIR = (
    PROJECT_ROOT
    / "blender"
)

BLENDER_SCRIPTS_DIR = (
    BLENDER_DIR
    / "scripts"
)

OUTPUT_DIR = (
    BLENDER_DIR
    / "output"
)

SEQUENCE_PATH = (
    OUTPUT_DIR
    / "pipeline_sequence.json"
)

OUTPUT_BLEND = (
    OUTPUT_DIR
    / "signmusic_pipeline_generated.blend"
)

BLENDER_SCRIPT = (
    BLENDER_SCRIPTS_DIR
    / "execute_pipeline_sequence.py"
)


# ============================================================
# PYTHON PATH
# ============================================================

if str(BACKEND_DIR) not in sys.path:

    sys.path.insert(
        0,
        str(BACKEND_DIR),
    )


# ============================================================
# IMPORTAR BACKEND
# ============================================================

from pipeline import SignMusicPipeline
from blender_bridge import BlenderBridge


# ============================================================
# CANCIÓN DE PRUEBA
# ============================================================

SONG = {
    "title": "Save Me, Save You",

    "lyrics": (
        "Save me, save you"
    ),
}


BPM = 120


# ============================================================
# INICIO
# ============================================================

print(
    "=== SIGNMUSIC PIPELINE → BLENDER ==="
)


print()
print(
    "Proyecto:"
)

print(
    PROJECT_ROOT
)


# ============================================================
# CREAR DIRECTORIOS
# ============================================================

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


# ============================================================
# PROCESAR PIPELINE
# ============================================================

print()
print(
    "=== PROCESANDO CANCIÓN ==="
)

pipeline = SignMusicPipeline()

result = pipeline.process_song(
    SONG,
    bpm=BPM,
)


print()
print(
    "Pipeline:",
    result[
        "pipeline_status"
    ],
)

print(
    "Conceptos:",
    [
        item[
            "concept"
        ]
        for item
        in result[
            "concepts"
        ]
    ],
)

print(
    "Animaciones:",
    len(
        result[
            "animations"
        ]
    ),
)

print(
    "Duración:",
    result[
        "total_duration"
    ],
)


# ============================================================
# GUARDAR SECUENCIA JSON
# ============================================================

print()
print(
    "=== GUARDANDO SECUENCIA ==="
)


with open(
    SEQUENCE_PATH,
    "w",
    encoding="utf-8",
) as file:

    json.dump(
        result,
        file,
        ensure_ascii=False,
        indent=4,
    )


print(
    f"Sequence JSON: {SEQUENCE_PATH}"
)


# ============================================================
# CREAR SCRIPT DE BLENDER SI NO EXISTE
# ============================================================

if not BLENDER_SCRIPT.exists():

    raise FileNotFoundError(
        "No existe el ejecutor de Blender:\n"
        f"{BLENDER_SCRIPT}"
    )


# ============================================================
# BLENDER BRIDGE
# ============================================================

print()
print(
    "=== EJECUTANDO BLENDER ==="
)

bridge = BlenderBridge()

version = bridge.get_version()

print()
print(
    "Blender:"
)

print(
    version
)


# ============================================================
# EJECUTAR BLENDER
# ============================================================

output = bridge.run_script(
    script_path=str(
        BLENDER_SCRIPT
    )
)


# ============================================================
# MOSTRAR LOG
# ============================================================

print()
print(
    "=== BLENDER OUTPUT ==="
)

print(
    output
)


# ============================================================
# VALIDAR RESULTADO
# ============================================================

print()
print(
    "=== VALIDACIÓN ==="
)


if OUTPUT_BLEND.exists():

    print(
        "✅ Blender generó el archivo:"
    )

    print(
        OUTPUT_BLEND
    )

else:

    print(
        "❌ Blender terminó pero no "
        "se encontró el archivo esperado:"
    )

    print(
        OUTPUT_BLEND
    )

    raise RuntimeError(
        "No se generó el .blend esperado."
    )


print()
print(
    "=== PIPELINE COMPLETO FINALIZADO ==="
)

print(
    f"Output: {OUTPUT_BLEND}"
)