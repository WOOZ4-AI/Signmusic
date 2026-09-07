import bpy
import math
import os
from mathutils import Vector


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
    "arm_ik_test.blend",
)

ARMATURE_NAME = "Armature"

SHOULDER = "mixamorig7:RightShoulder"
ARM = "mixamorig7:RightArm"
FOREARM = "mixamorig7:RightForeArm"
HAND = "mixamorig7:RightHand"

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
    "=== SIGNMUSIC ARM IK TEST ==="
)

print(
    f"Importando: {FBX_PATH}"
)

if not os.path.exists(
    FBX_PATH
):
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

pose_arm = armature.pose.bones.get(
    ARM
)

pose_forearm = armature.pose.bones.get(
    FOREARM
)

pose_hand = armature.pose.bones.get(
    HAND
)

if pose_arm is None:
    raise RuntimeError(
        f"No se encontró {ARM}"
    )

if pose_forearm is None:
    raise RuntimeError(
        f"No se encontró {FOREARM}"
    )

if pose_hand is None:
    raise RuntimeError(
        f"No se encontró {HAND}"
    )


print(
    f"Armature: {armature.name}"
)

print(
    "RightArm / RightForeArm / RightHand: OK"
)


# ============================================================
# DATOS REST
# ============================================================

rest_arm = armature.data.bones.get(
    ARM
)

rest_forearm = armature.data.bones.get(
    FOREARM
)

rest_hand = armature.data.bones.get(
    HAND
)

if (
    rest_arm is None
    or rest_forearm is None
    or rest_hand is None
):
    raise RuntimeError(
        "No se pudo obtener la cadena rest."
    )


# Posiciones globales en reposo

shoulder_pos = (
    armature.matrix_world
    @ rest_arm.head_local
)

elbow_pos = (
    armature.matrix_world
    @ rest_forearm.head_local
)

wrist_pos = (
    armature.matrix_world
    @ rest_hand.head_local
)


# Longitudes

upper_length = (
    rest_arm.length
)

fore_length = (
    rest_forearm.length
)


print()
print(
    "=== DATOS REST ==="
)

print(
    f"Shoulder: "
    f"{shoulder_pos}"
)

print(
    f"Elbow: "
    f"{elbow_pos}"
)

print(
    f"Wrist: "
    f"{wrist_pos}"
)

print(
    f"Upper arm length: "
    f"{upper_length:.6f}"
)

print(
    f"Forearm length: "
    f"{fore_length:.6f}"
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
    name="ArmIKTest"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# UTILIDADES
# ============================================================

def get_wrist_position():

    bpy.context.view_layer.update()

    matrix = (
        armature.matrix_world
        @ pose_hand.matrix
    )

    return matrix.translation.copy()


def reset_pose(frame):

    scene.frame_set(
        frame
    )

    for bone in (
        pose_arm,
        pose_forearm,
        pose_hand,
    ):

        bone.rotation_mode = "XYZ"

        bone.rotation_euler = (
            0.0,
            0.0,
            0.0,
        )

        bone.keyframe_insert(
            data_path="rotation_euler",
            frame=frame,
        )


def rotate_arm(
    frame,
    x,
    y,
    z,
):

    scene.frame_set(
        frame
    )

    pose_arm.rotation_mode = (
        "XYZ"
    )

    pose_arm.rotation_euler = (
        math.radians(x),
        math.radians(y),
        math.radians(z),
    )

    pose_arm.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
    )


def rotate_forearm(
    frame,
    x,
    y,
    z,
):

    scene.frame_set(
        frame
    )

    pose_forearm.rotation_mode = (
        "XYZ"
    )

    pose_forearm.rotation_euler = (
        math.radians(x),
        math.radians(y),
        math.radians(z),
    )

    pose_forearm.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
    )


def measure(
    label,
    frame,
):

    scene.frame_set(
        frame
    )

    bpy.context.view_layer.update()

    position = get_wrist_position()

    print()
    print(
        label
    )

    print(
        f"Frame: {frame}"
    )

    print(
        "Wrist:"
    )

    print(
        f"  X = {position.x:.6f}"
    )

    print(
        f"  Y = {position.y:.6f}"
    )

    print(
        f"  Z = {position.z:.6f}"
    )


# ============================================================
# REST
# ============================================================

reset_pose(
    1
)

measure(
    "NEUTRAL",
    1,
)


# ============================================================
# TEST 1
# ============================================================

rotate_arm(
    20,
    25,
    0,
    0,
)

measure(
    "TEST 1 — ARM X +25",
    20,
)


# ============================================================
# RESET
# ============================================================

reset_pose(
    30
)


# ============================================================
# TEST 2
# ============================================================

rotate_arm(
    45,
    0,
    0,
    25,
)

rotate_forearm(
    45,
    35,
    0,
    0,
)

measure(
    "TEST 2 — ARM Z +25 + FOREARM X +35",
    45,
)


# ============================================================
# RESET
# ============================================================

reset_pose(
    55
)


# ============================================================
# TEST 3
# ============================================================

rotate_arm(
    70,
    0,
    0,
    -25,
)

rotate_forearm(
    70,
    -35,
    0,
    0,
)

measure(
    "TEST 3 — ARM Z -25 + FOREARM X -35",
    70,
)


# ============================================================
# RESET
# ============================================================

reset_pose(
    80
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
    "=== ARM IK TEST COMPLETE ==="
)

print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()