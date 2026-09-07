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

OUTPUT_DIR = os.path.join(
    PROJECT_ROOT,
    "blender",
    "output",
)

OUTPUT_PATH = os.path.join(
    OUTPUT_DIR,
    "finger_flexion_test.blend",
)

ARMATURE_NAME = "Armature"

INDEX_BONES = [
    "mixamorig7:RightHandIndex1",
    "mixamorig7:RightHandIndex2",
    "mixamorig7:RightHandIndex3",
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
    "=== SIGNMUSIC FINGER FLEXION TEST ==="
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


bones = []

for bone_name in INDEX_BONES:

    bone = armature.pose.bones.get(
        bone_name
    )

    if bone is None:
        raise RuntimeError(
            f"No se encontró {bone_name}"
        )

    bones.append(
        bone
    )


print(
    "Índice derecho: OK"
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
    name="FingerFlexionTest"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# FUNCIÓN
# ============================================================

def neutral(frame):

    scene.frame_set(frame)

    for bone in bones:

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


def pose(
    frame,
    rotations,
):

    scene.frame_set(frame)

    for bone, rotation in zip(
        bones,
        rotations,
    ):

        bone.rotation_mode = "XYZ"

        bone.rotation_euler = (
            math.radians(rotation[0]),
            math.radians(rotation[1]),
            math.radians(rotation[2]),
        )

        bone.keyframe_insert(
            data_path="rotation_euler",
            frame=frame,
        )


# ============================================================
# NORMAL
# ============================================================

neutral(1)


# ============================================================
# PRUEBA 1
# ============================================================
#
# Flexión progresiva usando una combinación
# fuerte de rotaciones.
#
# ============================================================

pose(
    20,
    [
        (45, 0, 0),
        (45, 0, 0),
        (45, 0, 0),
    ],
)

print(
    "Frame 20 → PRUEBA 1"
)


neutral(30)


# ============================================================
# PRUEBA 2
# ============================================================

pose(
    45,
    [
        (0, 45, 0),
        (0, 45, 0),
        (0, 45, 0),
    ],
)

print(
    "Frame 45 → PRUEBA 2"
)


neutral(55)


# ============================================================
# PRUEBA 3
# ============================================================

pose(
    70,
    [
        (0, 0, 45),
        (0, 0, 45),
        (0, 0, 45),
    ],
)

print(
    "Frame 70 → PRUEBA 3"
)


neutral(80)


# ============================================================
# FINAL
# ============================================================

scene.frame_set(1)

scene.frame_start = 1

scene.frame_end = 80


# ============================================================
# GUARDAR
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


print(
    "\n=== FINGER FLEXION TEST COMPLETE ==="
)

print(
    "Frame 1  → posición normal"
)

print(
    "Frame 20 → PRUEBA 1"
)

print(
    "Frame 45 → PRUEBA 2"
)

print(
    "Frame 70 → PRUEBA 3"
)

print(
    f"Archivo: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()