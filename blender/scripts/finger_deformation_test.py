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
    "finger_deformation_test.blend",
)

BONE_NAME = "mixamorig7:RightHandIndex1"


# ============================================================
# LIMPIAR ESCENA
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
    "=== SIGNMUSIC FINGER DEFORMATION TEST ==="
)

print(
    f"Importando: {FBX_PATH}"
)

bpy.ops.import_scene.fbx(
    filepath=FBX_PATH
)


# ============================================================
# BUSCAR ARMATURE
# ============================================================

armature = bpy.data.objects.get(
    "Armature"
)

if armature is None:
    raise RuntimeError(
        "No se encontró el Armature."
    )

print(
    f"Armature: {armature.name}"
)


# ============================================================
# BUSCAR HUESO
# ============================================================

bone = armature.pose.bones.get(
    BONE_NAME
)

if bone is None:
    raise RuntimeError(
        f"No se encontró: {BONE_NAME}"
    )

print(
    f"Hueso: {BONE_NAME}"
)


# ============================================================
# POSICIÓN NEUTRA
# ============================================================

scene = bpy.context.scene

scene.frame_start = 1
scene.frame_end = 2

scene.frame_set(1)

bone.rotation_mode = "XYZ"

bone.rotation_euler = (
    0.0,
    0.0,
    0.0,
)


# ============================================================
# ROTAR DIRECTAMENTE EL HUESO
# ============================================================

scene.frame_set(2)

bone.rotation_euler = (
    math.radians(45.0),
    0.0,
    0.0,
)

print(
    "Rotación aplicada: X = 45°"
)


# ============================================================
# ACTUALIZAR ESCENA
# ============================================================

bpy.context.view_layer.update()


# ============================================================
# INFORMACIÓN DEL HUESO
# ============================================================

print(
    "Rotation Euler:",
    tuple(
        round(
            value,
            6
        )
        for value
        in bone.rotation_euler
    )
)


# ============================================================
# BUSCAR MESHES
# ============================================================

print()
print(
    "=== MESHES ==="
)

for obj in bpy.context.scene.objects:

    if obj.type != "MESH":
        continue

    print(
        f"Mesh: {obj.name}"
    )

    armature_modifiers = [
        modifier
        for modifier in obj.modifiers
        if modifier.type == "ARMATURE"
    ]

    print(
        f"  Armature modifiers: "
        f"{len(armature_modifiers)}"
    )

    for modifier in armature_modifiers:

        print(
            f"  → Armature: "
            f"{modifier.object.name if modifier.object else None}"
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
    "=== TEST COMPLETE ==="
)

print(
    f"Archivo: {OUTPUT_PATH}"
)

bpy.ops.wm.quit_blender()