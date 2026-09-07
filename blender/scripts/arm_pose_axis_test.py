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
    "arm_pose_axis_test.blend",
)


print(
    "=== SIGNMUSIC ARM POSE AXIS TEST ==="
)


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
    "Armature"
)

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


print(
    f"Armature: {armature.name}"
)


# ============================================================
# HUESOS
# ============================================================

arm = armature.pose.bones.get(
    "mixamorig7:RightArm"
)

forearm = armature.pose.bones.get(
    "mixamorig7:RightForeArm"
)

if arm is None:
    raise RuntimeError(
        "No existe mixamorig7:RightArm"
    )

if forearm is None:
    raise RuntimeError(
        "No existe mixamorig7:RightForeArm"
    )


print(
    "RightArm / RightForeArm: OK"
)


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = 25

scene.frame_start = 1
scene.frame_end = 121


# ============================================================
# ACTION
# ============================================================

action = bpy.data.actions.new(
    name="ArmPoseAxisTest"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# INSERTAR POSE
# ============================================================

def insert_pose(
    frame,
    arm_x=0.0,
    arm_y=0.0,
    arm_z=0.0,
    forearm_x=0.0,
    forearm_y=0.0,
    forearm_z=0.0,
):

    scene.frame_set(
        frame
    )

    # --------------------------------------------------------
    # BRAZO
    # --------------------------------------------------------

    arm.rotation_mode = "XYZ"

    arm.rotation_euler = (
        math.radians(
            arm_x
        ),
        math.radians(
            arm_y
        ),
        math.radians(
            arm_z
        ),
    )

    arm.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
        group="RightArm",
    )

    # --------------------------------------------------------
    # ANTEBRAZO
    # --------------------------------------------------------

    forearm.rotation_mode = "XYZ"

    forearm.rotation_euler = (
        math.radians(
            forearm_x
        ),
        math.radians(
            forearm_y
        ),
        math.radians(
            forearm_z
        ),
    )

    forearm.keyframe_insert(
        data_path="rotation_euler",
        frame=frame,
        group="RightForeArm",
    )


# ============================================================
# POSES
# ============================================================

print(
    "\n=== POSE TESTS ==="
)


print(
    "Frame 1  → NEUTRAL"
)

insert_pose(
    frame=1
)


print(
    "Frame 21 → ARM X +20"
)

insert_pose(
    frame=21,
    arm_x=20
)


print(
    "Frame 41 → ARM X -20"
)

insert_pose(
    frame=41,
    arm_x=-20
)


print(
    "Frame 61 → ARM Z +20"
)

insert_pose(
    frame=61,
    arm_z=20
)


print(
    "Frame 81 → ARM Z -20"
)

insert_pose(
    frame=81,
    arm_z=-20
)


print(
    "Frame 101 → FOREARM X +30"
)

insert_pose(
    frame=101,
    forearm_x=30
)


print(
    "Frame 121 → NEUTRAL"
)

insert_pose(
    frame=121
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
    "=== ARM POSE AXIS TEST COMPLETE ==="
)

print(
    f"Output: {OUTPUT_PATH}"
)

bpy.ops.wm.quit_blender()