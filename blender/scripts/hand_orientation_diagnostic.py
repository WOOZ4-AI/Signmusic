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

OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "blender",
    "output",
    "hand_orientation_diagnostic.blend",
)

ARMATURE_NAME = "Armature"
HAND_BONE = "mixamorig7:RightHand"

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
    "=== SIGNMUSIC HAND ORIENTATION DIAGNOSTIC ==="
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


hand = armature.pose.bones.get(
    HAND_BONE
)

if hand is None:
    raise RuntimeError(
        f"No se encontró {HAND_BONE}"
    )


print(
    f"Armature: {armature.name}"
)

print(
    f"Hueso probado: {HAND_BONE}"
)


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = FPS

scene.frame_start = 1

scene.frame_end = 100


# ============================================================
# ACTION
# ============================================================

action = bpy.data.actions.new(
    name="HandOrientationDiagnostic"
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

    hand.rotation_mode = "XYZ"

    hand.rotation_euler = (
        math.radians(x),
        math.radians(y),
        math.radians(z),
    )

    hand.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
    )


# ============================================================
# NEUTRAL
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
# PRUEBA A
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
# NEUTRAL
# ============================================================

set_rotation(
    30,
    0,
    0,
    0,
)


# ============================================================
# PRUEBA B
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
# NEUTRAL
# ============================================================

set_rotation(
    55,
    0,
    0,
    0,
)


# ============================================================
# PRUEBA C
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
# NEUTRAL FINAL
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
    os.path.dirname(
        OUTPUT_PATH
    ),
    exist_ok=True
)

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


# ============================================================
# RESULTADO
# ============================================================

print()
print(
    "=== HAND ORIENTATION DIAGNOSTIC COMPLETE ==="
)

print(
    "Frame 1  → posición normal"
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