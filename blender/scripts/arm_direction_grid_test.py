import bpy
import os
import math


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
    "arm_direction_grid_test.blend",
)


print("=== SIGNMUSIC ARM DIRECTION GRID TEST ===")


# ============================================================
# LIMPIAR
# ============================================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


# ============================================================
# IMPORTAR
# ============================================================

if not os.path.exists(FBX_PATH):
    raise FileNotFoundError(FBX_PATH)

print(f"Importando: {FBX_PATH}")

bpy.ops.import_scene.fbx(
    filepath=FBX_PATH
)


# ============================================================
# ARMATURE
# ============================================================

armature = bpy.data.objects.get("Armature")

if armature is None:

    armatures = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "ARMATURE"
    ]

    if len(armatures) == 1:
        armature = armatures[0]

if armature is None:
    raise RuntimeError(
        "No se encontró el Armature."
    )


arm = armature.pose.bones.get(
    "mixamorig7:RightArm"
)

forearm = armature.pose.bones.get(
    "mixamorig7:RightForeArm"
)

hand = armature.pose.bones.get(
    "mixamorig7:RightHand"
)

if arm is None:
    raise RuntimeError(
        "No existe RightArm"
    )

if forearm is None:
    raise RuntimeError(
        "No existe RightForeArm"
    )

print("RightArm / RightForeArm / RightHand: OK")


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = 25
scene.frame_start = 1
scene.frame_end = 181


# ============================================================
# ACTION
# ============================================================

action = bpy.data.actions.new(
    name="ArmDirectionGridTest"
)

armature.animation_data_create()
armature.animation_data.action = action


# ============================================================
# INSERTAR POSE
# ============================================================

def insert_pose(
    frame,
    arm_x,
    arm_z,
    forearm_x,
    forearm_z,
):

    scene.frame_set(frame)

    # --------------------------------------------------------
    # IMPORTANTE:
    # TODAS las componentes se escriben explícitamente.
    # Así cada prueba parte de neutral real.
    # --------------------------------------------------------

    arm.rotation_mode = "XYZ"

    arm.rotation_euler = (
        math.radians(arm_x),
        0.0,
        math.radians(arm_z),
    )

    arm.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
        group="RightArm",
    )

    forearm.rotation_mode = "XYZ"

    forearm.rotation_euler = (
        math.radians(forearm_x),
        0.0,
        math.radians(forearm_z),
    )

    forearm.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
        group="RightForeArm",
    )


# ============================================================
# POSES
# ============================================================

tests = [

    # 1
    ("NEUTRAL", 0, 0, 0, 0),

    # 2
    ("X +10", 10, 0, 0, 0),

    # 3
    ("X -10", -10, 0, 0, 0),

    # 4
    ("Z +10", 0, 10, 0, 0),

    # 5
    ("Z -10", 0, -10, 0, 0),

    # 6
    ("X +10 Z +10", 10, 10, 0, 0),

    # 7
    ("X +10 Z -10", 10, -10, 0, 0),

    # 8
    ("X -10 Z +10", -10, 10, 0, 0),

    # 9
    ("X -10 Z -10", -10, -10, 0, 0),

    # 10
    ("X +20 Z +20", 20, 20, 0, 0),

    # 11
    ("X +20 Z -20", 20, -20, 0, 0),

    # 12
    ("X -20 Z +20", -20, 20, 0, 0),

    # 13
    ("X -20 Z -20", -20, -20, 0, 0),

    # 14
    ("FOREARM X +20", 0, 0, 20, 0),

    # 15
    ("FOREARM X -20", 0, 0, -20, 0),

    # 16
    ("FOREARM X +20 Z +10", 0, 0, 20, 10),

    # 17
    ("FOREARM X -20 Z -10", 0, 0, -20, -10),
]


frame = 1

for name, arm_x, arm_z, forearm_x, forearm_z in tests:

    print(
        f"Frame {frame:3d} → {name}"
    )

    insert_pose(
        frame,
        arm_x,
        arm_z,
        forearm_x,
        forearm_z,
    )

    frame += 10


# ============================================================
# RETURN TO NEUTRAL
# ============================================================

insert_pose(
    frame,
    0,
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
    exist_ok=True,
)

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


print()
print(
    "=== ARM DIRECTION GRID TEST COMPLETE ==="
)

print(
    f"Output: {OUTPUT_PATH}"
)

bpy.ops.wm.quit_blender()