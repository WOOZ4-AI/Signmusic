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
    "thumb_diagnostic.blend",
)

ARMATURE_NAME = "Armature"

THUMB_BONES = [
    "mixamorig7:RightHandThumb1",
    "mixamorig7:RightHandThumb2",
    "mixamorig7:RightHandThumb3",
]

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
    "=== SIGNMUSIC THUMB DIAGNOSTIC ==="
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


# ============================================================
# COMPROBAR PULGAR
# ============================================================

pose_bones = []

for bone_name in THUMB_BONES:

    bone = armature.pose.bones.get(
        bone_name
    )

    if bone is None:
        raise RuntimeError(
            f"No se encontró {bone_name}"
        )

    pose_bones.append(
        bone
    )

    data_bone = (
        armature.data.bones.get(
            bone_name
        )
    )

    print()
    print(
        bone_name
    )

    print(
        "  use_deform:",
        data_bone.use_deform
    )

    print(
        "  parent:",
        data_bone.parent.name
        if data_bone.parent
        else None
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
    name="ThumbDiagnostic"
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

    for bone, rotation in zip(
        pose_bones,
        rotations,
    ):

        bone.rotation_mode = "XYZ"

        bone.rotation_euler = (
            math.radians(
                rotation[0]
            ),
            math.radians(
                rotation[1]
            ),
            math.radians(
                rotation[2]
            ),
        )

        bone.keyframe_insert(
            data_path="rotation_euler",
            frame=frame,
        )


# ============================================================
# NEUTRAL
# ============================================================

set_pose(
    1,
    [
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ],
)

print(
    "\nFrame 1 → pulgar normal"
)


# ============================================================
# PRUEBA A
# ============================================================

set_pose(
    20,
    [
        (45, 0, 0),
        (30, 0, 0),
        (15, 0, 0),
    ],
)

print(
    "Frame 20 → PRUEBA A"
)


# ============================================================
# NEUTRAL
# ============================================================

set_pose(
    30,
    [
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ],
)


# ============================================================
# PRUEBA B
# ============================================================

set_pose(
    45,
    [
        (0, 45, 0),
        (0, 30, 0),
        (0, 15, 0),
    ],
)

print(
    "Frame 45 → PRUEBA B"
)


# ============================================================
# NEUTRAL
# ============================================================

set_pose(
    55,
    [
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ],
)


# ============================================================
# PRUEBA C
# ============================================================

set_pose(
    70,
    [
        (0, 0, 45),
        (0, 0, 30),
        (0, 0, 15),
    ],
)

print(
    "Frame 70 → PRUEBA C"
)


# ============================================================
# FINAL
# ============================================================

set_pose(
    80,
    [
        (0, 0, 0),
        (0, 0, 0),
        (0, 0, 0),
    ],
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
    "=== THUMB DIAGNOSTIC COMPLETE ==="
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
    f"Archivo: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()