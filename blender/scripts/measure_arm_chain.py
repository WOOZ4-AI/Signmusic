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

ARMATURE_NAME = "Armature"

BONES = [
    "mixamorig7:RightShoulder",
    "mixamorig7:RightArm",
    "mixamorig7:RightForeArm",
    "mixamorig7:RightHand",
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
    "=== SIGNMUSIC ARM CHAIN MEASUREMENT ==="
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

print(
    f"Armature: {armature.name}"
)


# ============================================================
# MEDIR HUESOS
# ============================================================

print()
print(
    "=== BONE CHAIN ==="
)

for bone_name in BONES:

    bone = armature.data.bones.get(
        bone_name
    )

    if bone is None:

        raise RuntimeError(
            f"No se encontró {bone_name}"
        )

    head = (
        armature.matrix_world
        @ bone.head_local
    )

    tail = (
        armature.matrix_world
        @ bone.tail_local
    )

    vector = tail - head

    length = vector.length

    print()
    print(
        bone_name
    )

    print(
        f"  Parent: "
        f"{bone.parent.name if bone.parent else None}"
    )

    print(
        f"  Head:"
        f" X={head.x:.6f}"
        f" Y={head.y:.6f}"
        f" Z={head.z:.6f}"
    )

    print(
        f"  Tail:"
        f" X={tail.x:.6f}"
        f" Y={tail.y:.6f}"
        f" Z={tail.z:.6f}"
    )

    print(
        f"  Length: {length:.6f}"
    )


# ============================================================
# REST POSE GLOBAL
# ============================================================

shoulder = armature.data.bones.get(
    "mixamorig7:RightShoulder"
)

arm = armature.data.bones.get(
    "mixamorig7:RightArm"
)

forearm = armature.data.bones.get(
    "mixamorig7:RightForeArm"
)

hand = armature.data.bones.get(
    "mixamorig7:RightHand"
)


print()
print(
    "=== GLOBAL CHAIN POSITIONS ==="
)

for label, bone in (
    ("SHOULDER", shoulder),
    ("ARM", arm),
    ("FOREARM", forearm),
    ("HAND", hand),
):

    position = (
        armature.matrix_world
        @ bone.head_local
    )

    print(
        f"{label}: "
        f"X={position.x:.6f} "
        f"Y={position.y:.6f} "
        f"Z={position.z:.6f}"
    )


# ============================================================
# RESULTADO
# ============================================================

print()
print(
    "=== ARM CHAIN MEASUREMENT COMPLETE ==="
)

print(
    "Usaremos estas medidas para construir"
)

print(
    "la cinemática inversa del brazo."
)

bpy.ops.wm.quit_blender()