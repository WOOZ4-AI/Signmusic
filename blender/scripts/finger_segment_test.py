import bpy
import math
import os


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
    "finger_segment_test.blend",
)

ARMATURE_NAME = "Armature"

BONES = [
    "mixamorig7:RightHandIndex1",
    "mixamorig7:RightHandIndex2",
    "mixamorig7:RightHandIndex3",
]


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
    "=== SIGNMUSIC FINGER SEGMENT TEST ==="
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


pose_bones = []

for name in BONES:

    bone = armature.pose.bones.get(name)

    if bone is None:
        raise RuntimeError(
            f"No se encontró {name}"
        )

    pose_bones.append(bone)


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = 25

scene.frame_start = 1

scene.frame_end = 100


# ============================================================
# ACTION
# ============================================================

action = bpy.data.actions.new(
    name="FingerSegmentTest"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# FUNCIÓN
# ============================================================

def set_pose(
    frame,
    rotations,
):

    scene.frame_set(frame)

    for bone, angle in zip(
        pose_bones,
        rotations,
    ):

        bone.rotation_mode = "XYZ"

        bone.rotation_euler = (
            math.radians(angle),
            0.0,
            0.0,
        )

        bone.keyframe_insert(
            data_path="rotation_euler",
            frame=frame,
        )


# ============================================================
# POSE INICIAL
# ============================================================

set_pose(
    1,
    [0, 0, 0],
)

print(
    "Frame 1 → normal"
)


# ============================================================
# SOLO INDEX1
# ============================================================

set_pose(
    20,
    [45, 0, 0],
)

print(
    "Frame 20 → solo Index1"
)


# ============================================================
# NEUTRAL
# ============================================================

set_pose(
    30,
    [0, 0, 0],
)


# ============================================================
# SOLO INDEX2
# ============================================================

set_pose(
    45,
    [0, 45, 0],
)

print(
    "Frame 45 → solo Index2"
)


# ============================================================
# NEUTRAL
# ============================================================

set_pose(
    55,
    [0, 0, 0],
)


# ============================================================
# SOLO INDEX3
# ============================================================

set_pose(
    70,
    [0, 0, 45],
)

print(
    "Frame 70 → solo Index3"
)


# ============================================================
# FINAL
# ============================================================

set_pose(
    80,
    [0, 0, 0],
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


print()
print(
    "=== FINGER SEGMENT TEST COMPLETE ==="
)

print(
    f"Archivo: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()