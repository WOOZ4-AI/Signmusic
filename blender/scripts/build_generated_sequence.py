import bpy
import os
import sys
import math


# ============================================================
# CONFIGURACIÓN DEL PROYECTO
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

BACKEND_DIR = os.path.join(
    PROJECT_ROOT,
    "backend",
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
    "signmusic_generated.blend",
)


# ============================================================
# IMPORTAR BACKEND
# ============================================================

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from keyframe_generator import KeyframeGenerator
from avatar_animation import AvatarAnimation


# ============================================================
# INICIO
# ============================================================

print("=== SIGNMUSIC GENERATED SEQUENCE ===")


# ============================================================
# GENERAR SECUENCIA DESDE EL BACKEND
# ============================================================

generator = KeyframeGenerator()
avatar_animation = AvatarAnimation()

sequence = generator.generate_animation_sequence(
    ["SAVE", "ME"],
    bpm=120,
)

prepared_sequence = avatar_animation.prepare_sequence(
    sequence
)

print(
    f"Conceptos generados: "
    f"{len(prepared_sequence['animations'])}"
)

print(
    f"Duración total: "
    f"{prepared_sequence['total_duration']} segundos"
)


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

print(
    f"Importando avatar: {FBX_PATH}"
)

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

print(
    f"Armature encontrado: {armature.name}"
)


# ============================================================
# CONFIGURAR ESCENA
# ============================================================

scene = bpy.context.scene

fps = prepared_sequence.get(
    "fps",
    25,
)

scene.render.fps = fps

total_duration = prepared_sequence.get(
    "total_duration",
    0,
)

scene.frame_start = 1

scene.frame_end = max(
    1,
    round(total_duration * fps) + 1,
)

print(
    f"FPS: {fps}"
)

print(
    f"Frames: "
    f"{scene.frame_start} → {scene.frame_end}"
)


# ============================================================
# CREAR ACTION
# ============================================================

action = bpy.data.actions.new(
    name="SignMusic_Generated"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# APLICAR SECUENCIA
# ============================================================

print("\n=== APLICANDO SECUENCIA GENERADA ===")


for animation in prepared_sequence["animations"]:

    concept = animation.get(
        "concept",
        "UNKNOWN",
    )

    start_time = animation.get(
        "start_time",
        0.0,
    )

    print(
        f"\nConcepto: {concept}"
    )

    for keyframe in animation.get(
        "keyframes",
        [],
    ):

        local_time = keyframe.get(
            "time",
            0.0,
        )

        absolute_time = (
            start_time +
            local_time
        )

        frame = (
            round(
                absolute_time * fps
            )
            + 1
        )

        scene.frame_set(frame)

        print(
            f"  Frame {frame} | "
            f"Time {absolute_time:.2f}s"
        )

        for bone_name, transform in keyframe[
            "bones"
        ].items():

            pose_bone = armature.pose.bones.get(
                bone_name
            )

            if pose_bone is None:

                print(
                    f"  WARNING: hueso no encontrado: "
                    f"{bone_name}"
                )

                continue


            # ------------------------------------------------
            # ROTACIÓN
            # ------------------------------------------------

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


            # ------------------------------------------------
            # POSICIÓN
            # ------------------------------------------------

            if "position" in transform:

                position = transform[
                    "position"
                ]

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


            # ------------------------------------------------
            # ESCALA
            # ------------------------------------------------

            if "scale" in transform:

                scale = transform[
                    "scale"
                ]

                pose_bone.scale = (
                    float(scale[0]),
                    float(scale[1]),
                    float(scale[2]),
                )

                pose_bone.keyframe_insert(
                    data_path="scale",
                    frame=frame,
                    group=bone_name,
                )


# ============================================================
# INTERPOLACIÓN
# ============================================================

print(
    "\n=== CONFIGURANDO INTERPOLACIÓN ==="
)

# Blender 5.2 utiliza la nueva estructura de
# Actions. Los keyframes ya fueron creados.
#
# No recorremos action.fcurves ni las estructuras
# antiguas de Blender, porque Blender 5.2 utiliza
# ChannelBags.

print(
    "Interpolación preparada."
)


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

print(
    "\n=== SIGNMUSIC GENERATED SEQUENCE COMPLETE ==="
)

print(
    f"Conceptos: "
    f"{len(prepared_sequence['animations'])}"
)

print(
    f"Duración: "
    f"{total_duration} segundos"
)

print(
    f"Archivo: {OUTPUT_PATH}"
)

bpy.ops.wm.quit_blender()