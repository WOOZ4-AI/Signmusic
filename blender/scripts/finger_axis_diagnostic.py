import bpy
import math
import os


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

FBX_PATH = os.path.join(
    PROJECT_ROOT,
    "blender",
    "assets",
    "Ch08_nonPBR.fbx",
)

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "blender",
    "output",
)

OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "finger_axis_visual_test.blend",
)

ARMATURE_NAME = "Armature"

BONE_NAME = "mixamorig7:RightHandIndex1"

FPS = 25


# ============================================================
# LIMPIAR
# ============================================================

bpy.ops.object.select_all(
    action="SELECT"
)

bpy.ops.object.delete(
    use_global=False
)


# ============================================================
# IMPORTAR AVATAR
# ============================================================

print(
    "=== SIGNMUSIC FINGER VISUAL TEST ==="
)

print(
    f"Importando: {FBX_PATH}"
)

if not os.path.exists(FBX_PATH):
    raise FileNotFoundError(
        FBX_PATH
    )

bpy.ops.import_scene.fbx(
    filepath=FBX_PATH
)


# ============================================================
# ARMATURE
# ============================================================

armature = bpy.data.objects.get(
    ARMATURE_NAME
)

if armature is None:
    raise RuntimeError(
        "No se encontró Armature."
    )

bone = armature.pose.bones.get(
    BONE_NAME
)

if bone is None:
    raise RuntimeError(
        f"No se encontró {BONE_NAME}"
    )


print(
    f"Armature: {armature.name}"
)

print(
    f"Hueso probado: {BONE_NAME}"
)


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = FPS

scene.frame_start = 1

scene.frame_end = 80


# ============================================================
# ACTION
# ============================================================

action = bpy.data.actions.new(
    name="FingerVisualTest"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# FUNCIÓN
# ============================================================

def set_rotation(
    frame,
    x,
    y,
    z,
):
    scene.frame_set(frame)

    bone.rotation_mode = "XYZ"

    bone.rotation_euler = (
        math.radians(x),
        math.radians(y),
        math.radians(z),
    )

    bone.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
    )


# ============================================================
# 1 — NEUTRAL
# ============================================================

set_rotation(
    1,
    0,
    0,
    0,
)

print(
    "Frame 1 → posición normal"
)


# ============================================================
# 2 — PRUEBA A
# ============================================================

set_rotation(
    20,
    45,
    0,
    0,
)

print(
    "Frame 20 → PRUEBA A"
)


# ============================================================
# 3 — NEUTRAL
# ============================================================

set_rotation(
    30,
    0,
    0,
    0,
)


# ============================================================
# 4 — PRUEBA B
# ============================================================

set_rotation(
    45,
    0,
    45,
    0,
)

print(
    "Frame 45 → PRUEBA B"
)


# ============================================================
# 5 — NEUTRAL
# ============================================================

set_rotation(
    55,
    0,
    0,
    0,
)


# ============================================================
# 6 — PRUEBA C
# ============================================================

set_rotation(
    70,
    0,
    0,
    45,
)

print(
    "Frame 70 → PRUEBA C"
)


# ============================================================
# FINAL
# ============================================================

set_rotation(
    80,
    0,
    0,
    0,
)


# ============================================================
# GUARDAR
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


print()
print(
    "=== TEST COMPLETO ==="
)

print(
    "Frame 1  → normal"
)

print(
    "Frame 20 → PRUEBA A"
)

print(
    "Frame 45 → PRUEBA B"
)

print(
    "Frame 70 → PRUEBA C"
)

print(
    f"Archivo: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()