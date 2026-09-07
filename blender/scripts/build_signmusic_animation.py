import bpy
import os
import math


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
    "signmusic_save.blend",
)


# ============================================================
# INICIO
# ============================================================

print("=== SIGNMUSIC ANIMATION BUILDER ===")


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
        f"No se encontró el avatar:\n{FBX_PATH}"
    )

print(f"Importando avatar: {FBX_PATH}")

bpy.ops.import_scene.fbx(
    filepath=FBX_PATH
)


# ============================================================
# BUSCAR ARMATURE
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
        "No se encontró ningún Armature."
    )

print(f"Armature encontrado: {armature.name}")


# ============================================================
# DATOS TEMPORALES DE SIGNMUSIC
# ============================================================

ANIMATION = {
    "concept": "SAVE",

    "start_time": 0.0,
    "end_time": 0.8,

    "keyframes": [

        {
            "time": 0.0,

            "bones": {

                "mixamorig7:LeftArm": {
                    "rotation": [0.0, 0.0, 0.0],
                    "position": [0.0, 0.0, 0.0],
                },

                "mixamorig7:RightArm": {
                    "rotation": [0.0, 0.0, 0.0],
                    "position": [0.0, 0.0, 0.0],
                },

                "mixamorig7:LeftHand": {
                    "rotation": [0.0, 0.0, 0.0],
                },

                "mixamorig7:RightHand": {
                    "rotation": [0.0, 0.0, 0.0],
                },
            },
        },

        {
            "time": 0.4,

            "bones": {

                "mixamorig7:LeftArm": {
                    "rotation": [45.0, 0.0, 0.0],
                    "position": [0.0, 0.15, 0.0],
                },

                "mixamorig7:RightArm": {
                    "rotation": [45.0, 0.0, 0.0],
                    "position": [0.0, 0.15, 0.0],
                },

                "mixamorig7:LeftHand": {
                    "rotation": [22.5, 0.0, 0.0],
                },

                "mixamorig7:RightHand": {
                    "rotation": [22.5, 0.0, 0.0],
                },
            },
        },

        {
            "time": 0.8,

            "bones": {

                "mixamorig7:LeftArm": {
                    "rotation": [0.0, 0.0, 0.0],
                    "position": [0.0, 0.0, 0.0],
                },

                "mixamorig7:RightArm": {
                    "rotation": [0.0, 0.0, 0.0],
                    "position": [0.0, 0.0, 0.0],
                },

                "mixamorig7:LeftHand": {
                    "rotation": [0.0, 0.0, 0.0],
                },

                "mixamorig7:RightHand": {
                    "rotation": [0.0, 0.0, 0.0],
                },
            },
        },
    ],
}


# ============================================================
# CONFIGURAR ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = 25

scene.frame_start = 1
scene.frame_end = 21


# ============================================================
# CREAR ANIMACIÓN
# ============================================================

action = bpy.data.actions.new(
    name="SignMusic_SAVE"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# APLICAR KEYFRAMES
# ============================================================

print("\n=== APLICANDO KEYFRAMES ===")


for keyframe in ANIMATION["keyframes"]:

    time = keyframe["time"]

    frame = round(
        time * scene.render.fps
    ) + 1

    scene.frame_set(frame)

    print(
        f"Frame {frame} | "
        f"Time {time:.2f}s"
    )


    for bone_name, transform in keyframe["bones"].items():

        pose_bone = armature.pose.bones.get(
            bone_name
        )

        if pose_bone is None:

            print(
                f"WARNING: hueso no encontrado: "
                f"{bone_name}"
            )

            continue


        # ----------------------------------------------------
        # ROTACIÓN
        # ----------------------------------------------------

        if "rotation" in transform:

            rotation = transform["rotation"]

            pose_bone.rotation_mode = "XYZ"

            pose_bone.rotation_euler = (
                math.radians(
                    float(rotation[0])
                ),

                math.radians(
                    float(rotation[1])
                ),

                math.radians(
                    float(rotation[2])
                ),
            )

            pose_bone.keyframe_insert(
                data_path="rotation_euler",
                frame=frame,
                group=bone_name,
            )


        # ----------------------------------------------------
        # POSICIÓN
        # ----------------------------------------------------

        if "position" in transform:

            position = transform["position"]

            pose_bone.location = (
                float(position[0]),
                float(position[1]),
                float(position[2]),
            )

            pose_bone.keyframe_insert(
                data_path="location",
                frame=frame,
                group=bone_name,
            )


# ============================================================
# INTERPOLACIÓN
# ============================================================

print("\n=== CONFIGURANDO INTERPOLACIÓN ===")

# Blender 5.2 utiliza la nueva estructura de Actions.
# Los keyframes ya fueron creados correctamente.
# La interpolación por defecto es suficiente para esta prueba.

print("Interpolación preparada.")


# ============================================================
# CREAR OUTPUT
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True,
)


# ============================================================
# GUARDAR BLEND
# ============================================================

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


# ============================================================
# FINAL
# ============================================================

print("\n=== SIGNMUSIC ANIMATION COMPLETE ===")

print(
    f"Concepto: {ANIMATION['concept']}"
)

print(
    f"Duración: {ANIMATION['end_time']} segundos"
)

print(
    f"Archivo: {OUTPUT_PATH}"
)

bpy.ops.wm.quit_blender()