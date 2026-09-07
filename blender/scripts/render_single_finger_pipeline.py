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
    "signmusic_single_finger_pipeline.blend",
)

ARMATURE_NAME = "Armature"


# ============================================================
# BACKEND
# ============================================================

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from motion_generator import MotionGenerator
from blender_renderer import BlenderRenderer


# ============================================================
# INICIO
# ============================================================

print(
    "=== SIGNMUSIC SINGLE FINGER PIPELINE TEST ==="
)


# ============================================================
# GENERADORES
# ============================================================

motion_generator = MotionGenerator()

renderer = BlenderRenderer()

print(
    "MotionGenerator: OK"
)

print(
    "BlenderRenderer: OK"
)


# ============================================================
# SIGNO ARTIFICIAL
# ============================================================

test_sign = {
    "concept": "SAVE",
    "duration": 0.8,

    # --------------------------------------------------------
    # SOLO ÍNDICE
    # --------------------------------------------------------

    "hand_shape": {
        "shape": "FINGER_TEST",

        "fingers": {
            "index": {
                "flexion": 60,
            },
        },
    },

    "orientation": {},
    "location": {},
    "movement": {},
    "non_manual": {},
}


# ============================================================
# GENERAR MOTION PLAN
# ============================================================

plan = motion_generator.generate_motion(
    test_sign
)


errors = plan.validate()

if errors:
    raise RuntimeError(
        "MotionPlan inválido: "
        + "; ".join(errors)
    )


print()
print(
    "MotionPlan: OK"
)

print(
    "Concept:",
    plan.concept
)

print(
    "Duration:",
    plan.duration
)

print(
    "FPS:",
    plan.fps
)


# ============================================================
# MOSTRAR KEYFRAMES
# ============================================================

print()
print(
    "=== MOTION PLAN KEYFRAMES ==="
)

for keyframe in plan.keyframes:

    print()
    print(
        f"Time {keyframe.time:.2f}s | "
        f"Phase {keyframe.phase}"
    )

    for bone_name, transform in (
        keyframe.bones.items()
    ):

        # Solo mostramos dedos
        if (
            "index" not in bone_name
        ):
            continue

        print(
            f"  {bone_name}: "
            f"{transform}"
        )


# ============================================================
# CONSTRUIR SECUENCIA
# ============================================================

sequence = {
    "bpm": 120,
    "fps": plan.fps,
    "beat_duration": 0.5,
    "total_duration": plan.duration,

    "animations": [
        {
            "concept": plan.concept,
            "start_time": 0.0,
            "duration": plan.duration,
            "end_time": plan.duration,
            "status": "defined",
            "confidence": 0.0,

            "keyframes": [
                {
                    **keyframe.to_dict(),
                    "frame": (
                        round(
                            keyframe.time
                            * plan.fps
                        )
                        + 1
                    ),
                    "absolute_time": (
                        keyframe.time
                    ),
                }
                for keyframe
                in plan.keyframes
            ],
        }
    ],
}


# ============================================================
# BLENDER RENDERER
# ============================================================

prepared = renderer.prepare_sequence(
    sequence
)


print()
print(
    "BlenderRenderer: OK"
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

if not os.path.exists(
    FBX_PATH
):

    raise FileNotFoundError(
        f"No existe el avatar:\n{FBX_PATH}"
    )


print()
print(
    f"Importando avatar:"
)

print(
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

    armatures = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "ARMATURE"
    ]

    if len(armatures) == 1:

        armature = armatures[0]


if armature is None:

    raise RuntimeError(
        "No se encontró Armature."
    )


print(
    f"Armature encontrado: "
    f"{armature.name}"
)


# ============================================================
# CONFIGURAR ESCENA
# ============================================================

scene = bpy.context.scene

fps = int(
    prepared.get(
        "fps",
        25,
    )
)

total_duration = float(
    prepared.get(
        "total_duration",
        plan.duration,
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
# ACTION
# ============================================================

action = bpy.data.actions.new(
    name="SignMusic_SingleFinger_TEST"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# APLICAR SOLO ÍNDICE
# ============================================================

print()
print(
    "=== APLICANDO SOLO ÍNDICE DERECHO ==="
)


for animation in prepared[
    "animations"
]:

    for keyframe in animation[
        "keyframes"
    ]:

        frame = int(
            keyframe["frame"]
        )

        scene.frame_set(
            frame
        )

        print()
        print(
            f"Frame {frame} | "
            f"Time "
            f"{keyframe['absolute_time']:.2f}s | "
            f"Phase {keyframe['phase']}"
        )


        for bone_name, transform in (
            keyframe["bones"].items()
        ):

            # ------------------------------------------------
            # IGNORAR TODO EXCEPTO EL ÍNDICE
            # ------------------------------------------------

            if "RightHandIndex" not in bone_name:

                continue


            pose_bone = (
                armature.pose.bones.get(
                    bone_name
                )
            )

            if pose_bone is None:

                print(
                    f"WARNING: no existe "
                    f"{bone_name}"
                )

                continue


            print(
                f"  → {bone_name}"
            )


            # ------------------------------------------------
            # ROTACIÓN
            # ------------------------------------------------

            if "rotation" in transform:

                rotation = transform[
                    "rotation"
                ]

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
    exist_ok=True
)

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


# ============================================================
# RESULTADO
# ============================================================

print()
print(
    "=== SINGLE FINGER PIPELINE COMPLETE ==="
)

print(
    "Solo se animó:"
)

print(
    "  RightHandIndex1"
)

print(
    "  RightHandIndex2"
)

print(
    "  RightHandIndex3"
)

print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()