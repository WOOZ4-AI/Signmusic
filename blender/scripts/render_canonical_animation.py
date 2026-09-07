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

DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "animations",
    "save_me_save_you_animation.json",
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
    "signmusic_canonical_animation.blend",
)


# ============================================================
# BACKEND
# ============================================================

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from animation_loader import AnimationLoader
from blender_renderer import BlenderRenderer


# ============================================================
# INICIO
# ============================================================

print("=== SIGNMUSIC CANONICAL BLENDER RENDERER ===")


# ============================================================
# CARGAR ANIMACIÓN
# ============================================================

if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(
        f"No existe la animación:\n{DATA_PATH}"
    )

loader = AnimationLoader()

sequence = loader.load_file(
    DATA_PATH
)

print(
    f"Formato: {sequence['format']}"
)

print(
    f"FPS: {sequence['fps']}"
)

print(
    f"Duración total: "
    f"{sequence['total_duration']}s"
)

print(
    f"Animaciones: "
    f"{len(sequence['animations'])}"
)


# ============================================================
# PREPARAR CON BLENDER RENDERER
# ============================================================

renderer = BlenderRenderer()

prepared = renderer.prepare_sequence(
    sequence
)

print(
    "\nBlenderRenderer: OK"
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
    f"\nImportando avatar:"
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

fps = prepared.get(
    "fps",
    25,
)

total_duration = prepared.get(
    "total_duration",
    0.0,
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
    name="SignMusic_Canonical"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# APLICAR ANIMACIONES
# ============================================================

print(
    "\n=== APLICANDO ANIMACIÓN CANÓNICA ==="
)


for animation in prepared[
    "animations"
]:

    concept = animation.get(
        "concept",
        "UNKNOWN",
    )

    status = animation.get(
        "status",
        "unknown",
    )

    start_time = float(
        animation.get(
            "start_time",
            0.0,
        )
    )

    duration = float(
        animation.get(
            "duration",
            0.0,
        )
    )

    print(
        f"\nConcepto: {concept}"
    )

    print(
        f"  Status: {status}"
    )

    print(
        f"  Inicio: {start_time:.2f}s"
    )

    print(
        f"  Duración: {duration:.2f}s"
    )


    # --------------------------------------------------------
    # SEGMENTO SIN ANIMACIÓN
    # --------------------------------------------------------

    if status == "undefined":

        print(
            "  → Sin animación disponible"
        )

        continue


    # --------------------------------------------------------
    # KEYFRAMES
    # --------------------------------------------------------

    for keyframe in animation.get(
        "keyframes",
        [],
    ):

        frame = keyframe.get(
            "frame"
        )

        absolute_time = keyframe.get(
            "absolute_time"
        )

        if frame is None:

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
                    absolute_time
                    * fps
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


        # ----------------------------------------------------
        # APLICAR HUESOS
        # ----------------------------------------------------

        for bone_name, transform in (
            keyframe.get(
                "bones",
                {}
            ).items()
        ):

            pose_bone = (
                armature.pose.bones.get(
                    bone_name
                )
            )

            if pose_bone is None:

                print(
                    f"    WARNING: hueso no encontrado: "
                    f"{bone_name}"
                )

                continue


            # ------------------------------------------------
            # ROTACIÓN
            # ------------------------------------------------

            if "rotation" in transform:

                rotation = (
                    transform[
                        "rotation"
                    ]
                )

                if len(rotation) != 3:
                    raise ValueError(
                        f"Rotación inválida "
                        f"para {bone_name}"
                    )

                pose_bone.rotation_mode = (
                    "XYZ"
                )

                pose_bone.rotation_euler = (
                    math.radians(
                        float(
                            rotation[0]
                        )
                    ),
                    math.radians(
                        float(
                            rotation[1]
                        )
                    ),
                    math.radians(
                        float(
                            rotation[2]
                        )
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

                position = (
                    transform[
                        "position"
                    ]
                )

                if len(position) != 3:
                    raise ValueError(
                        f"Posición inválida "
                        f"para {bone_name}"
                    )

                pose_bone.location = (
                    float(
                        position[0]
                    ),
                    float(
                        position[1]
                    ),
                    float(
                        position[2]
                    ),
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

                scale = (
                    transform[
                        "scale"
                    ]
                )

                if len(scale) != 3:
                    raise ValueError(
                        f"Escala inválida "
                        f"para {bone_name}"
                    )

                pose_bone.scale = (
                    float(
                        scale[0]
                    ),
                    float(
                        scale[1]
                    ),
                    float(
                        scale[2]
                    ),
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
    exist_ok=True,
)

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


# ============================================================
# RESULTADO
# ============================================================

print(
    "\n=== SIGNMUSIC CANONICAL RENDER COMPLETE ==="
)

print(
    f"Conceptos: "
    f"{len(prepared['animations'])}"
)

print(
    f"Duración: "
    f"{total_duration}s"
)

print(
    f"Archivo: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()