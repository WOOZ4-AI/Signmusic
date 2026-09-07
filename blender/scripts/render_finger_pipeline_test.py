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
    "signmusic_finger_pipeline_test.blend",
)


# ============================================================
# IMPORTAR BACKEND
# ============================================================

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from motion_generator import MotionGenerator
from blender_renderer import BlenderRenderer


# ============================================================
# INICIO
# ============================================================

print(
    "=== SIGNMUSIC FINGER PIPELINE TEST ==="
)


# ============================================================
# CREAR GENERADORES
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

# IMPORTANTE:
# Esta configuración NO representa un signo real.
# Solamente prueba que los dedos pueden viajar
# desde el backend hasta Blender.

test_sign = {
    "concept": "SAVE",
    "duration": 0.8,

    "hand_shape": {
        "shape": "TEST",

        "fingers": {
            "index": {
                "rotation": [
                    30,
                    20,
                    10,
                ],
            },

            "middle": {
                "rotation": [
                    25,
                    15,
                    5,
                ],
            },

            "ring": {
                "rotation": [
                    20,
                    10,
                    5,
                ],
            },

            "pinky": {
                "rotation": [
                    15,
                    10,
                    5,
                ],
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


validation = plan.validate()

if validation:
    raise RuntimeError(
        "MotionPlan inválido: "
        + "; ".join(validation)
    )


print(
    "\nMotionPlan: OK"
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
# CREAR SECUENCIA
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
                keyframe.to_dict()
                for keyframe in plan.keyframes
            ],
        }
    ],
}


# ============================================================
# PREPARAR PARA BLENDER
# ============================================================

prepared = renderer.prepare_sequence(
    sequence
)

print(
    "\nBlenderRenderer preparation: OK"
)


# ============================================================
# INFORMACIÓN DE KEYFRAMES
# ============================================================

print(
    "\n=== KEYFRAMES PREPARADOS ==="
)

for animation in prepared[
    "animations"
]:

    for keyframe in animation[
        "keyframes"
    ]:

        print(
            f"Frame {keyframe['frame']} | "
            f"Time {keyframe['absolute_time']:.2f}s | "
            f"Phase {keyframe['phase']}"
        )

        for bone_name in keyframe[
            "bones"
        ]:

            print(
                f"  → {bone_name}"
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
    prepared.get(
        "fps",
        25,
    )
)

total_duration = float(
    prepared.get(
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
    name="SignMusic_FingerPipeline_TEST"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# APLICAR KEYFRAMES
# ============================================================

print(
    "\n=== APLICANDO KEYFRAMES AL AVATAR ==="
)


for animation in prepared[
    "animations"
]:

    if animation.get(
        "status"
    ) == "undefined":

        continue


    for keyframe in animation[
        "keyframes"
    ]:

        frame = int(
            keyframe["frame"]
        )

        scene.frame_set(
            frame
        )

        print(
            f"\nFrame {frame} | "
            f"Time {keyframe['absolute_time']:.2f}s | "
            f"Phase {keyframe['phase']}"
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
                    f"WARNING: hueso no encontrado: "
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

                position = transform[
                    "position"
                ]

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

                scale = transform[
                    "scale"
                ]

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
    "\n=== SIGNMUSIC FINGER PIPELINE COMPLETE ==="
)

print(
    f"Concept: {plan.concept}"
)

print(
    f"Keyframes: {len(plan.keyframes)}"
)

print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()