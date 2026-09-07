import bpy
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


# ============================================================
# INICIO
# ============================================================

print("=== SIGNMUSIC AVATAR RIG VALIDATOR ===")


# ============================================================
# LIMPIAR ESCENA
# ============================================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


# ============================================================
# COMPROBAR FBX
# ============================================================

if not os.path.exists(FBX_PATH):
    raise FileNotFoundError(
        f"No se encontró el avatar:\n{FBX_PATH}"
    )


print(
    f"Importando avatar: {FBX_PATH}"
)


bpy.ops.import_scene.fbx(
    filepath=FBX_PATH
)


# ============================================================
# BUSCAR ARMATURE
# ============================================================

armatures = [
    obj
    for obj in bpy.context.scene.objects
    if obj.type == "ARMATURE"
]


if not armatures:
    raise RuntimeError(
        "No se encontró ningún Armature."
    )


armature = armatures[0]


print(
    f"Armature encontrado: {armature.name}"
)


# ============================================================
# OBTENER HUESOS
# ============================================================

bone_names = [
    bone.name
    for bone in armature.data.bones
]


print(
    f"\nTotal de huesos: {len(bone_names)}"
)


# ============================================================
# HUESOS QUE NECESITA SIGNMUSIC
# ============================================================

required_bones = [
    "mixamorig7:LeftArm",
    "mixamorig7:RightArm",
    "mixamorig7:LeftHand",
    "mixamorig7:RightHand",
    "mixamorig7:LeftForeArm",
    "mixamorig7:RightForeArm",
    "mixamorig7:LeftShoulder",
    "mixamorig7:RightShoulder",
    "mixamorig7:Head",
    "mixamorig7:Neck",
    "mixamorig7:Spine",
    "mixamorig7:Spine1",
    "mixamorig7:Spine2",
]


# ============================================================
# VALIDACIÓN
# ============================================================

print(
    "\n=== VALIDACIÓN DE HUESOS ==="
)


found = []
missing = []


for bone_name in required_bones:

    if bone_name in bone_names:

        found.append(
            bone_name
        )

        print(
            f"OK      {bone_name}"
        )

    else:

        missing.append(
            bone_name
        )

        print(
            f"MISSING {bone_name}"
        )


# ============================================================
# RESUMEN
# ============================================================

print(
    "\n=== RESUMEN ==="
)

print(
    f"Huesos encontrados: {len(found)}"
)

print(
    f"Huesos faltantes: {len(missing)}"
)


if missing:

    print(
        "\nHuesos faltantes:"
    )

    for bone_name in missing:
        print(
            f"  - {bone_name}"
        )


print(
    "\n=== SIGNMUSIC AVATAR RIG VALIDATION COMPLETE ==="
)


bpy.ops.wm.quit_blender()