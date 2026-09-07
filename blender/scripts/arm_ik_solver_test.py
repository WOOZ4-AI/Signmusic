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
    "arm_ik_solver_test.blend",
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
    "=== SIGNMUSIC ARM IK SOLVER TEST ==="
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
    name="ArmIKSolverTest"
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


def get_wrist_position():

    bpy.context.view_layer.update()

    matrix = (
        armature.matrix_world
        @ pose_hand.matrix
    )

    return matrix.translation.copy()


def print_position(
    label,
    position,
):

    print()

    print(
        label
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


def print_error(
    target,
    actual,
):

    error_vector = (
        actual
        - target
    )

    error_distance = (
        error_vector.length
    )

    print(
        "  Error X = "
        f"{error_vector.x:.6f}"
    )

    print(
        "  Error Y = "
        f"{error_vector.y:.6f}"
    )

    print(
        "  Error Z = "
        f"{error_vector.z:.6f}"
    )

    print(
        "  Error total = "
        f"{error_distance:.6f}"
    )


# ============================================================
# NEUTRAL
# ============================================================

reset_pose(
    1
)

neutral = get_wrist_position()

print()
print(
    "=== POSICIÓN NEUTRAL ==="
)

print_position(
    "Neutral wrist:",
    neutral
)


# ============================================================
# OBJETIVO 1
# ============================================================

target_1 = Vector(
    (
        neutral.x,
        neutral.y,
        neutral.z - 0.10,
    )
)

reset_pose(
    20
)

# Pequeña aproximación deliberada.
pose_arm.rotation_mode = "XYZ"

pose_arm.rotation_euler.x = math.radians(
    12.5
)

pose_forearm.rotation_mode = "XYZ"

pose_forearm.rotation_euler.x = math.radians(
    17.5
)

pose_arm.keyframe_insert(
    data_path="rotation_euler",
    frame=20,
)

pose_forearm.keyframe_insert(
    data_path="rotation_euler",
    frame=20,
)

actual_1 = get_wrist_position()

print()
print(
    "=== OBJETIVO 1 ==="
)

print_position(
    "Target:",
    target_1
)

print_position(
    "Actual:",
    actual_1
)

print(
    "Error:"
)

print_error(
    target_1,
    actual_1
)


# ============================================================
# RESET
# ============================================================

reset_pose(
    35
)


# ============================================================
# OBJETIVO 2
# ============================================================

target_2 = Vector(
    (
        neutral.x,
        neutral.y + 0.08,
        neutral.z + 0.05,
    )
)

reset_pose(
    50
)

pose_arm.rotation_mode = "XYZ"

pose_arm.rotation_euler.z = math.radians(
    10
)

pose_forearm.rotation_mode = "XYZ"

pose_forearm.rotation_euler.x = math.radians(
    -8
)

pose_arm.keyframe_insert(
    data_path="rotation_euler",
    frame=50,
)

pose_forearm.keyframe_insert(
    data_path="rotation_euler",
    frame=50,
)

actual_2 = get_wrist_position()

print()
print(
    "=== OBJETIVO 2 ==="
)

print_position(
    "Target:",
    target_2
)

print_position(
    "Actual:",
    actual_2
)

print(
    "Error:"
)

print_error(
    target_2,
    actual_2
)


# ============================================================
# RESET
# ============================================================

reset_pose(
    65
)


# ============================================================
# OBJETIVO 3
# ============================================================

target_3 = Vector(
    (
        neutral.x + 0.08,
        neutral.y,
        neutral.z - 0.05,
    )
)

reset_pose(
    80
)

pose_arm.rotation_mode = "XYZ"

pose_arm.rotation_euler.x = math.radians(
    8
)

pose_arm.rotation_euler.z = math.radians(
    -8
)

pose_forearm.rotation_mode = "XYZ"

pose_forearm.rotation_euler.x = math.radians(
    12
)

pose_arm.keyframe_insert(
    data_path="rotation_euler",
    frame=80,
)

pose_forearm.keyframe_insert(
    data_path="rotation_euler",
    frame=80,
)

actual_3 = get_wrist_position()

print()
print(
    "=== OBJETIVO 3 ==="
)

print_position(
    "Target:",
    target_3
)

print_position(
    "Actual:",
    actual_3
)

print(
    "Error:"
)

print_error(
    target_3,
    actual_3
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
    "=== ARM IK SOLVER TEST COMPLETE ==="
)

print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()