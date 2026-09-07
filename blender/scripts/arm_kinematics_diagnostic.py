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
    "arm_kinematics_diagnostic.blend",
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
# IMPORTAR
# ============================================================

print(
    "=== SIGNMUSIC ARM KINEMATICS DIAGNOSTIC ==="
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


print(
    f"Armature: {armature.name}"
)


pose_shoulder = armature.pose.bones.get(
    SHOULDER
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

for name, bone in (
    (SHOULDER, pose_shoulder),
    (ARM, pose_arm),
    (FOREARM, pose_forearm),
    (HAND, pose_hand),
):

    if bone is None:
        raise RuntimeError(
            f"No se encontró {name}"
        )

    print(
        f"OK: {name}"
    )


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = FPS

scene.frame_start = 1

scene.frame_end = 150


# ============================================================
# ACTION
# ============================================================

action = bpy.data.actions.new(
    name="ArmKinematicsDiagnostic"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# RESET
# ============================================================

def reset_pose(frame):

    scene.frame_set(frame)

    for bone in (
        pose_shoulder,
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
# ROTACIÓN
# ============================================================

def rotate(
    bone,
    frame,
    x=0.0,
    y=0.0,
    z=0.0,
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
# POSICIÓN MUNDIAL DE LA MANO
# ============================================================

def get_hand_world_position():

    bpy.context.view_layer.update()

    matrix = (
        armature.matrix_world
        @ pose_hand.matrix
    )

    position = matrix.translation

    return [
        float(position.x),
        float(position.y),
        float(position.z),
    ]


# ============================================================
# FUNCIÓN DE MEDICIÓN
# ============================================================

def measure(label, frame):

    scene.frame_set(frame)

    bpy.context.view_layer.update()

    position = get_hand_world_position()

    print()
    print(
        f"{label}"
    )

    print(
        f"Frame: {frame}"
    )

    print(
        "Hand world position:"
    )

    print(
        f"  X = {position[0]:.6f}"
    )

    print(
        f"  Y = {position[1]:.6f}"
    )

    print(
        f"  Z = {position[2]:.6f}"
    )

    return position


# ============================================================
# NEUTRAL
# ============================================================

reset_pose(1)

neutral_position = measure(
    "NEUTRAL",
    1,
)


# ============================================================
# PRUEBA A
# ============================================================

reset_pose(20)

rotate(
    pose_arm,
    20,
    x=25,
)

position_a = measure(
    "PRUEBA A: ARM X +25",
    20,
)


# ============================================================
# RESET
# ============================================================

reset_pose(40)


# ============================================================
# PRUEBA B
# ============================================================

rotate(
    pose_arm,
    50,
    y=25,
)

position_b = measure(
    "PRUEBA B: ARM Y +25",
    50,
)


# ============================================================
# RESET
# ============================================================

reset_pose(70)


# ============================================================
# PRUEBA C
# ============================================================

rotate(
    pose_arm,
    80,
    z=25,
)

position_c = measure(
    "PRUEBA C: ARM Z +25",
    80,
)


# ============================================================
# RESET
# ============================================================

reset_pose(100)


# ============================================================
# PRUEBA D
# ============================================================

rotate(
    pose_forearm,
    110,
    x=45,
)

position_d = measure(
    "PRUEBA D: FOREARM X +45",
    110,
)


# ============================================================
# RESET
# ============================================================

reset_pose(125)


# ============================================================
# PRUEBA E
# ============================================================

rotate(
    pose_forearm,
    135,
    y=45,
)

position_e = measure(
    "PRUEBA E: FOREARM Y +45",
    135,
)


# ============================================================
# RESET
# ============================================================

reset_pose(145)


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
    "=== ARM KINEMATICS DIAGNOSTIC COMPLETE ==="
)

print()
print(
    "NEUTRAL:",
    neutral_position
)

print(
    "A:",
    position_a
)

print(
    "B:",
    position_b
)

print(
    "C:",
    position_c
)

print(
    "D:",
    position_d
)

print(
    "E:",
    position_e
)

print()
print(
    f"Archivo: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()