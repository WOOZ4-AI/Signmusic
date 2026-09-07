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
    "arm_ik_calibration.blend",
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
# IMPORTAR
# ============================================================

print(
    "=== SIGNMUSIC ARM IK CALIBRATION ==="
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
    ARM_BONE
)

pose_forearm = armature.pose.bones.get(
    FOREARM_BONE
)

pose_hand = armature.pose.bones.get(
    HAND_BONE
)

if pose_arm is None:
    raise RuntimeError(
        f"No se encontró {ARM_BONE}"
    )

if pose_forearm is None:
    raise RuntimeError(
        f"No se encontró {FOREARM_BONE}"
    )

if pose_hand is None:
    raise RuntimeError(
        f"No se encontró {HAND_BONE}"
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
    name="ArmIKCalibration"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# UTILIDADES
# ============================================================

def reset_pose(
    frame
):

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
    x=0.0,
    y=0.0,
    z=0.0,
):

    scene.frame_set(
        frame
    )

    pose_arm.rotation_mode = "XYZ"

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
    x=0.0,
    y=0.0,
    z=0.0,
):

    scene.frame_set(
        frame
    )

    pose_forearm.rotation_mode = "XYZ"

    pose_forearm.rotation_euler = (
        math.radians(x),
        math.radians(y),
        math.radians(z),
    )

    pose_forearm.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
    )


def get_hand_position():

    bpy.context.view_layer.update()

    matrix = (
        armature.matrix_world
        @ pose_hand.matrix
    )

    return matrix.translation.copy()


def print_measurement(
    label,
    frame,
):

    scene.frame_set(
        frame
    )

    bpy.context.view_layer.update()

    position = get_hand_position()

    print()
    print(
        label
    )

    print(
        f"Frame: {frame}"
    )

    print(
        f"X = {position.x:.6f}"
    )

    print(
        f"Y = {position.y:.6f}"
    )

    print(
        f"Z = {position.z:.6f}"
    )

    return position


# ============================================================
# NEUTRAL
# ============================================================

reset_pose(
    1
)

neutral = print_measurement(
    "NEUTRAL",
    1,
)


# ============================================================
# ARM X
# ============================================================

reset_pose(
    20
)

rotate_arm(
    20,
    x=20,
)

pos_arm_x = print_measurement(
    "ARM X +20",
    20,
)


# ============================================================
# RESET
# ============================================================

reset_pose(
    30
)


# ============================================================
# ARM Y
# ============================================================

rotate_arm(
    40,
    y=20,
)

pos_arm_y = print_measurement(
    "ARM Y +20",
    40,
)


# ============================================================
# RESET
# ============================================================

reset_pose(
    50
)


# ============================================================
# ARM Z
# ============================================================

rotate_arm(
    60,
    z=20,
)

pos_arm_z = print_measurement(
    "ARM Z +20",
    60,
)


# ============================================================
# RESET
# ============================================================

reset_pose(
    70
)


# ============================================================
# FOREARM X
# ============================================================

rotate_forearm(
    80,
    x=20,
)

pos_forearm_x = print_measurement(
    "FOREARM X +20",
    80,
)


# ============================================================
# RESET
# ============================================================

reset_pose(
    90
)


# ============================================================
# FOREARM Y
# ============================================================

rotate_forearm(
    95,
    y=20,
)

pos_forearm_y = print_measurement(
    "FOREARM Y +20",
    95,
)


# ============================================================
# RESET
# ============================================================

reset_pose(
    100
)


# ============================================================
# FOREARM Z
# ============================================================

rotate_forearm(
    100,
    z=20,
)

pos_forearm_z = print_measurement(
    "FOREARM Z +20",
    100,
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
    "=== ARM IK CALIBRATION COMPLETE ==="
)

print()
print(
    "NEUTRAL:",
    list(neutral)
)

print(
    "ARM X:",
    list(pos_arm_x)
)

print(
    "ARM Y:",
    list(pos_arm_y)
)

print(
    "ARM Z:",
    list(pos_arm_z)
)

print(
    "FOREARM X:",
    list(pos_forearm_x)
)

print(
    "FOREARM Y:",
    list(pos_forearm_y)
)

print(
    "FOREARM Z:",
    list(pos_forearm_z)
)

print()
print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()