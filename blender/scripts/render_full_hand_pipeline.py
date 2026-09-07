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
    "signmusic_full_hand_pipeline.blend",
)


# ============================================================
# BACKEND
# ============================================================

if BACKEND_DIR not in sys.path:
    sys.path.insert(
        0,
        BACKEND_DIR,
    )

from motion_generator import MotionGenerator
from blender_renderer import BlenderRenderer


# ============================================================
# INICIO
# ============================================================

print(
    "=== SIGNMUSIC FULL HAND PIPELINE TEST ==="
)

motion_generator = MotionGenerator()

renderer = BlenderRenderer()

print(
    "MotionGenerator: OK"
)

print(
    "BlenderRenderer: OK"
)


# ============================================================
# CONFIGURACIÓN ARTIFICIAL
# ============================================================

# IMPORTANTE:
# Esto NO representa un signo real.
# Es exclusivamente una prueba técnica
# de control de los 15 huesos de la mano.

test_sign = {
    "concept": "SAVE",
    "duration": 0.8,

    "hand_shape": {
        "shape": "FULL_HAND_TEST",

        "fingers": {

            "thumb": {
                "opposition": 45,
            },

            "index": {
                "flexion": 60,
            },

            "middle": {
                "flexion": 50,
            },

            "ring": {
                "flexion": 45,
            },

            "pinky": {
                "flexion": 35,
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
    f"Concept: {plan.concept}"
)

print(
    f"Duration: {plan.duration}s"
)

print(
    f"FPS: {plan.fps}"
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
        FBX_PATH
    )

print()
print(
    "Importando avatar:"
)

print(
    FBX_PATH
)

bpy.ops.import_scene.fbx(
    filepath=FBX_PATH
)


# ============================================================
# ENCONTRAR ARMATURE
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
# CREAR ACTION
# ============================================================

action = bpy.data.actions.new(
    name="SignMusic_FullHand_TEST"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# APLICAR LOS 15 HUESOS DE LA MANO
# ============================================================

print()
print(
    "=== APLICANDO MANO COMPLETA ==="
)

finger_names = (
    "RightHandThumb",
    "RightHandIndex",
    "RightHandMiddle",
    "RightHandRing",
    "RightHandPinky",
)


applied_bones = set()


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
            # Solo huesos de los dedos
            # ------------------------------------------------

            if not bone_name.startswith(
                "mixamorig7:"
            ):
                continue

            if not any(
                finger_name in bone_name
                for finger_name
                in finger_names
            ):
                continue

            pose_bone = (
                armature.pose.bones.get(
                    bone_name
                )
            )

            if pose_bone is None:

                print(
                    f"WARNING: "
                    f"{bone_name} no encontrado"
                )

                continue


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

                applied_bones.add(
                    bone_name
                )

                print(
                    f"  → {bone_name}"
                )


# ============================================================
# RESUMEN DE HUESOS
# ============================================================

print()
print(
    "=== RESUMEN DE HUESOS APLICADOS ==="
)

for bone_name in sorted(
    applied_bones
):

    print(
        f"  ✅ {bone_name}"
    )

print()
print(
    f"Total de huesos aplicados: "
    f"{len(applied_bones)}"
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
    "=== SIGNMUSIC FULL HAND PIPELINE COMPLETE ==="
)

print(
    f"Concept: {plan.concept}"
)

print(
    f"Keyframes: "
    f"{len(plan.keyframes)}"
)

print(
    f"Huesos de mano aplicados: "
    f"{len(applied_bones)}"
)

print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()