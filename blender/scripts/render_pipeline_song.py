import bpy
import math
import os
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
    "signmusic_pipeline_song.blend",
)


# ============================================================
# BACKEND
# ============================================================

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from pipeline import SignMusicPipeline


# ============================================================
# INICIO
# ============================================================

print(
    "=== SIGNMUSIC PIPELINE BLENDER RENDER ==="
)


# ============================================================
# CREAR PIPELINE
# ============================================================

pipeline = SignMusicPipeline()


# ============================================================
# CANCIÓN DE PRUEBA
# ============================================================

song = {
    "title": "Save Me",
    "lyrics": "Save me",
}


# ============================================================
# PROCESAR CANCIÓN
# ============================================================

result = pipeline.process_song(
    song,
    bpm=120,
)


print(
    "\nPipeline status:",
    result["pipeline_status"],
)

print(
    "Song:",
    result["song"],
)

print(
    "Concepts:",
    [
        item["concept"]
        for item in result["concepts"]
    ],
)

print(
    "Animations:",
    len(result["animations"]),
)


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

if not os.path.exists(FBX_PATH):
    raise FileNotFoundError(
        f"No existe el avatar:\n{FBX_PATH}"
    )


print(
    "\nImportando avatar:"
)

print(
    FBX_PATH
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

fps = int(
    result.get(
        "fps",
        25,
    )
)

total_duration = float(
    result.get(
        "total_duration",
        0.0,
    )
)

scene.render.fps = fps

scene.frame_start = 1

scene.frame_end = (
    round(
        total_duration * fps
    )
    + 1
)


print(
    f"FPS: {fps}"
)

print(
    f"Frames: "
    f"{scene.frame_start} → "
    f"{scene.frame_end}"
)


# ============================================================
# CREAR ACTION
# ============================================================

action = bpy.data.actions.new(
    name="SignMusic_Pipeline"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# APLICAR ANIMACIONES
# ============================================================

print(
    "\n=== APLICANDO PIPELINE ==="
)


for animation in result[
    "animations"
]:

    concept = animation.get(
        "concept",
        "UNKNOWN",
    )

    status = animation.get(
        "status",
        "undefined",
    )

    print(
        f"\nConcepto: {concept}"
    )

    print(
        f"  Status: {status}"
    )


    if status == "undefined":

        print(
            "  → Sin animación disponible"
        )

        continue


    start_time = float(
        animation.get(
            "start_time",
            0.0,
        )
    )


    for keyframe in animation.get(
        "keyframes",
        [],
    ):

        local_time = float(
            keyframe.get(
                "time",
                0.0,
            )
        )

        absolute_time = (
            start_time
            + local_time
        )

        frame = (
            round(
                absolute_time * fps
            )
            + 1
        )

        scene.frame_set(
            frame
        )

        print(
            f"  Frame {frame} | "
            f"Time {absolute_time:.2f}s"
        )


        for bone_name, transform in (
            keyframe.get(
                "bones",
                {},
            ).items()
        ):

            pose_bone = (
                armature.pose.bones.get(
                    bone_name
                )
            )

            if pose_bone is None:

                print(
                    f"    WARNING: "
                    f"hueso no encontrado: "
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

                pose_bone.rotation_mode = (
                    "XYZ"
                )

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
# GUARDAR
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


# ============================================================
# RESULTADO
# ============================================================

print(
    "\n=== SIGNMUSIC PIPELINE BLENDER COMPLETE ==="
)

print(
    f"Conceptos: "
    f"{len(result['animations'])}"
)

print(
    f"Duración: "
    f"{total_duration}s"
)

print(
    f"Archivo: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()