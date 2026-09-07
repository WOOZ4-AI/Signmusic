import bpy
import os
import math


# ============================================================
# CONFIGURACIÓN
# ============================================================

FBX_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "assets",
        "Ch08_nonPBR.fbx",
    )
)

OUTPUT_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "output",
        "finger_test.blend",
    )
)

ARMATURE_NAME = "Armature"

INDEX_BONES = [
    ("mixamorig7:RightHandIndex1", 30.0),
    ("mixamorig7:RightHandIndex2", 20.0),
    ("mixamorig7:RightHandIndex3", 10.0),
]


# ============================================================
# LIMPIAR ESCENA
# ============================================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


# ============================================================
# IMPORTAR AVATAR
# ============================================================

if not os.path.exists(FBX_PATH):
    raise FileNotFoundError(
        f"No se encontró el avatar: {FBX_PATH}"
    )

print(f"Importando avatar: {FBX_PATH}")

bpy.ops.import_scene.fbx(
    filepath=FBX_PATH
)


# ============================================================
# BUSCAR ARMATURE
# ============================================================

armature = bpy.data.objects.get(ARMATURE_NAME)

if armature is None:
    raise RuntimeError(
        f"No se encontró el armature '{ARMATURE_NAME}'"
    )

print(f"Armature encontrado: {armature.name}")

bpy.context.view_layer.objects.active = armature
armature.select_set(True)

armature.rotation_mode = "XYZ"


# ============================================================
# VERIFICAR HUESOS
# ============================================================

print("\n=== VERIFICANDO DEDO ÍNDICE DERECHO ===")

for bone_name, angle in INDEX_BONES:

    bone = armature.pose.bones.get(bone_name)

    if bone is None:
        raise RuntimeError(
            f"No se encontró el hueso: {bone_name}"
        )

    print(
        f"OK: {bone_name} -> {angle} grados"
    )


# ============================================================
# CREAR ANIMACIÓN
# ============================================================

print("\n=== CREANDO ANIMACIÓN ===")

scene = bpy.context.scene

scene.render.fps = 25

# Frame 1 = posición neutra
scene.frame_set(1)

for bone_name, _ in INDEX_BONES:

    bone = armature.pose.bones[bone_name]

    bone.rotation_mode = "XYZ"
    bone.rotation_euler = (0.0, 0.0, 0.0)

    bone.keyframe_insert(
        data_path="rotation_euler",
        frame=1,
    )


# ------------------------------------------------------------
# Frame 25 = dedo doblado
# ------------------------------------------------------------

scene.frame_set(25)

for bone_name, angle in INDEX_BONES:

    bone = armature.pose.bones[bone_name]

    bone.rotation_mode = "XYZ"

    bone.rotation_euler.x = math.radians(angle)

    bone.keyframe_insert(
        data_path="rotation_euler",
        frame=25,
    )


# ------------------------------------------------------------
# Frame 50 = volver a posición neutra
# ------------------------------------------------------------

scene.frame_set(50)

for bone_name, _ in INDEX_BONES:

    bone = armature.pose.bones[bone_name]

    bone.rotation_mode = "XYZ"
    bone.rotation_euler.x = 0.0

    bone.keyframe_insert(
        data_path="rotation_euler",
        frame=50,
    )


# ============================================================
# CONFIGURACIÓN DE LA ANIMACIÓN
# ============================================================

scene.frame_start = 1
scene.frame_end = 50


# ============================================================
# CREAR CARPETA DE OUTPUT
# ============================================================

output_dir = os.path.dirname(OUTPUT_PATH)

os.makedirs(
    output_dir,
    exist_ok=True,
)


# ============================================================
# GUARDAR BLEND
# ============================================================

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)

print("\n=== SIGNMUSIC FINGER TEST COMPLETE ===")
print(f"Archivo creado: {OUTPUT_PATH}")
print("Animación:")
print("  Frame 1  -> posición neutra")
print("  Frame 25 -> dedo índice doblado")
print("  Frame 50 -> posición neutra")


# ============================================================
# FINAL
# ============================================================

bpy.ops.wm.quit_blender()