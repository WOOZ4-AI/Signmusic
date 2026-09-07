import bpy
import os
import math
import sys


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
    "signmusic_sequence_test.blend",
)


# ============================================================
# SECUENCIA DE PRUEBA
# ============================================================

SEQUENCE = {
    "fps": 25,
    "animations": [
        {
            "concept": "SAVE",
            "start_time": 0.0,
            "duration": 0.8,
            "keyframes": [
                {
                    "time": 0.0,
                    "bones": {
                        "mixamorig7:LeftArm": {
                            "rotation": [0, 0, 0]
                        },
                        "mixamorig7:RightArm": {
                            "rotation": [0, 0, 0]
                        },
                    },
                },
                {
                    "time": 0.4,
                    "bones": {
                        "mixamorig7:LeftArm": {
                            "rotation": [45, 0, 0]
                        },
                        "mixamorig7:RightArm": {
                            "rotation": [45, 0, 0]
                        },
                    },
                },
                {
                    "time": 0.8,
                    "bones": {
                        "mixamorig7:LeftArm": {
                            "rotation": [0, 0, 0]
                        },
                        "mixamorig7:RightArm": {
                            "rotation": [0, 0, 0]
                        },
                    },
                },
            ],
        },
        {
            "concept": "ME",
            "start_time": 0.8,
            "duration": 0.45,
            "keyframes": [
                {
                    "time": 0.0,
                    "bones": {
                        "mixamorig7:RightArm": {
                            "rotation": [0, 0, 0]
                        },
                    },
                },
                {
                    "time": 0.24,
                    "bones": {
                        "mixamorig7:RightArm": {
                            "rotation": [25, 0, 0]
                        },
                    },
                },
                {
                    "time": 0.45,
                    "bones": {
                        "mixamorig7:RightArm": {
                            "rotation": [0, 0, 0]
                        },
                    },
                },
            ],
        },
    ],
}


# ============================================================
# INICIO
# ============================================================

print("=== SIGNMUSIC SEQUENCE TEST ===")


# ============================================================
# LIMPIAR
# ============================================================

bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)


# ============================================================
# IMPORTAR AVATAR
# ============================================================

print(f"Importando avatar: {FBX_PATH}")

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

print(f"Armature encontrado: {armature.name}")


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = SEQUENCE["fps"]
scene.frame_start = 1


total_duration = 0.0

for animation in SEQUENCE["animations"]:
    end_time = (
        animation["start_time"]
        + animation["duration"]
    )

    total_duration = max(
        total_duration,
        end_time,
    )

scene.frame_end = round(
    total_duration * scene.render.fps
) + 1


print(
    f"Duración total: {total_duration:.2f} segundos"
)

print(
    f"Frames: {scene.frame_start} → {scene.frame_end}"
)


# ============================================================
# ACTION
# ============================================================

action = bpy.data.actions.new(
    name="SignMusic_SAVE_ME"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# KEYFRAMES
# ============================================================

print("\n=== APLICANDO SECUENCIA ===")


for animation in SEQUENCE["animations"]:

    concept = animation["concept"]
    start_time = animation["start_time"]

    print(
        f"\nConcepto: {concept}"
    )

    for keyframe in animation["keyframes"]:

        absolute_time = (
            start_time
            + keyframe["time"]
        )

        frame = round(
            absolute_time
            * scene.render.fps
        ) + 1

        scene.frame_set(frame)

        print(
            f"  Frame {frame} | "
            f"Time {absolute_time:.2f}s"
        )

        for bone_name, transform in (
            keyframe["bones"].items()
        ):

            pose_bone = (
                armature.pose.bones.get(
                    bone_name
                )
            )

            if pose_bone is None:
                print(
                    f"  WARNING: "
                    f"hueso no encontrado: "
                    f"{bone_name}"
                )
                continue

            if "rotation" in transform:

                rotation = transform[
                    "rotation"
                ]

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


# ============================================================
# GUARDAR
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True,
)

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


# ============================================================
# FINAL
# ============================================================

print("\n=== SEQUENCE TEST COMPLETE ===")

print(
    f"Archivo: {OUTPUT_PATH}"
)

print(
    f"Duración: {total_duration:.2f}s"
)

bpy.ops.wm.quit_blender()