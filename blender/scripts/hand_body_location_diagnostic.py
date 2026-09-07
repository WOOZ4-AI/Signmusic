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
    "hand_body_location_diagnostic.blend",
)

ARMATURE_NAME = "Armature"

RIGHT_ARM = "mixamorig7:RightArm"
RIGHT_FOREARM = "mixamorig7:RightForeArm"
RIGHT_HAND = "mixamorig7:RightHand"

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
    "=== SIGNMUSIC HAND BODY LOCATION DIAGNOSTIC ==="
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
    RIGHT_ARM
)

forearm_bone = armature.pose.bones.get(
    RIGHT_FOREARM
)

hand_bone = armature.pose.bones.get(
    RIGHT_HAND
)

if arm_bone is None:
    raise RuntimeError(
        f"No se encontró {RIGHT_ARM}"
    )

if forearm_bone is None:
    raise RuntimeError(
        f"No se encontró {RIGHT_FOREARM}"
    )

if hand_bone is None:
    raise RuntimeError(
        f"No se encontró {RIGHT_HAND}"
    )


print(
    f"Armature: {armature.name}"
)

print(
    "RightArm / RightForeArm / RightHand: OK"
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
    name="HandBodyLocationDiagnostic"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# HELPERS
# ============================================================

def reset_pose(frame):
    """
    Devuelve brazo, antebrazo y mano a neutral.
    """

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


def rotate_bone(
    frame,
    bone,
    x=0.0,
    y=0.0,
    z=0.0,
):
    """
    Aplica rotación a un hueso.
    """

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
# POSICIÓN NORMAL
# ============================================================

reset_pose(1)

print(
    "\nFrame 1 → neutral"
)


# ============================================================
# A → PECHO
# ============================================================
#
# Intento de llevar la mano hacia el centro del torso.
# ============================================================

rotate_bone(
    20,
    arm_bone,
    20,
    0,
    0,
)

rotate_bone(
    20,
    forearm_bone,
    35,
    0,
    0,
)

print(
    "Frame 20 → PRUEBA A: PECHO"
)


# ============================================================
# RESET
# ============================================================

reset_pose(30)


# ============================================================
# B → CARA
# ============================================================
#
# Elevamos el brazo y flexionamos el antebrazo.
# ============================================================

rotate_bone(
    45,
    arm_bone,
    -35,
    0,
    0,
)

rotate_bone(
    45,
    forearm_bone,
    -65,
    0,
    0,
)

print(
    "Frame 45 → PRUEBA B: CARA"
)


# ============================================================
# RESET
# ============================================================

reset_pose(55)


# ============================================================
# C → HOMBRO
# ============================================================

rotate_bone(
    70,
    arm_bone,
    0,
    0,
    -55,
)

rotate_bone(
    70,
    forearm_bone,
    25,
    0,
    0,
)

print(
    "Frame 70 → PRUEBA C: HOMBRO"
)


# ============================================================
# RESET
# ============================================================

reset_pose(80)


# ============================================================
# D → ESPACIO DELANTE DEL CUERPO
# ============================================================

rotate_bone(
    90,
    arm_bone,
    15,
    0,
    0,
)

rotate_bone(
    90,
    forearm_bone,
    -75,
    0,
    0,
)

print(
    "Frame 90 → PRUEBA D: FRENTE"
)


# ============================================================
# GUARDAR
# ============================================================

os.makedirs(
    os.path.dirname(OUTPUT_PATH),
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
    "=== HAND BODY LOCATION DIAGNOSTIC COMPLETE ==="
)

print(
    "Frame 1  → neutral"
)

print(
    "Frame 20 → A: pecho"
)

print(
    "Frame 45 → B: cara"
)

print(
    "Frame 70 → C: hombro"
)

print(
    "Frame 90 → D: frente"
)

print(
    f"Archivo: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()