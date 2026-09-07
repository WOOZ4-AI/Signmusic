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
    "hand_location_diagnostic.blend",
)

ARMATURE_NAME = "Armature"

ARM_BONE = "mixamorig7:RightArm"
FOREARM_BONE = "mixamorig7:RightForeArm"
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
    "=== SIGNMUSIC HAND LOCATION DIAGNOSTIC ==="
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


arm_bone = armature.pose.bones.get(
    ARM_BONE
)

forearm_bone = armature.pose.bones.get(
    FOREARM_BONE
)

hand_bone = armature.pose.bones.get(
    HAND_BONE
)

if arm_bone is None:
    raise RuntimeError(
        f"No se encontró {ARM_BONE}"
    )

if forearm_bone is None:
    raise RuntimeError(
        f"No se encontró {FOREARM_BONE}"
    )

if hand_bone is None:
    raise RuntimeError(
        f"No se encontró {HAND_BONE}"
    )


print(
    f"Armature: {armature.name}"
)

print(
    "Arm bones: OK"
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
    name="HandLocationDiagnostic"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# FUNCIÓN NEUTRAL
# ============================================================

def neutral(frame):

    scene.frame_set(frame)

    for bone in (
        arm_bone,
        forearm_bone,
        hand_bone,
    ):

        bone.rotation_mode = "XYZ"

        bone.rotation_euler = (
            0.0,
            0.0,
            0.0,
        )

        bone.location = (
            0.0,
            0.0,
            0.0,
        )

        bone.keyframe_insert(
            data_path="rotation_euler",
            frame=frame,
        )

        bone.keyframe_insert(
            data_path="location",
            frame=frame,
        )


# ============================================================
# FUNCIÓN PARA ROTACIÓN
# ============================================================

def set_rotation(
    frame,
    bone,
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
# FUNCIÓN PARA POSICIÓN
# ============================================================

def set_position(
    frame,
    bone,
    x,
    y,
    z,
):

    scene.frame_set(frame)

    bone.location = (
        float(x),
        float(y),
        float(z),
    )

    bone.keyframe_insert(
        data_path="location",
        frame=frame,
    )


# ============================================================
# POSICIÓN NORMAL
# ============================================================

neutral(1)

print(
    "\nFrame 1 → posición normal"
)


# ============================================================
# PRUEBA A
# ============================================================
#
# Mover hombro/brazo en X
# ============================================================

set_rotation(
    20,
    arm_bone,
    25,
    0,
    0,
)

print(
    "Frame 20 → PRUEBA A"
)


# ============================================================
# NEUTRAL
# ============================================================

neutral(30)


# ============================================================
# PRUEBA B
# ============================================================
#
# Mover brazo en Y
# ============================================================

set_rotation(
    45,
    arm_bone,
    0,
    25,
    0,
)

print(
    "Frame 45 → PRUEBA B"
)


# ============================================================
# NEUTRAL
# ============================================================

neutral(55)


# ============================================================
# PRUEBA C
# ============================================================
#
# Mover brazo en Z
# ============================================================

set_rotation(
    70,
    arm_bone,
    0,
    0,
    25,
)

print(
    "Frame 70 → PRUEBA C"
)


# ============================================================
# NEUTRAL
# ============================================================

neutral(80)


# ============================================================
# PRUEBA D
# ============================================================
#
# Movimiento directo de la mano en X
# ============================================================

set_position(
    90,
    hand_bone,
    0.5,
    0.0,
    0.0,
)

print(
    "Frame 90 → PRUEBA D"
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
    "=== HAND LOCATION DIAGNOSTIC COMPLETE ==="
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
    "Frame 90 → PRUEBA D"
)

print(
    f"Archivo: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()