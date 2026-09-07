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
    "signmusic_motionplan_test.blend",
)


# ============================================================
# BACKEND
# ============================================================

if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from motion_plan import MotionPlan
from bone_mapper import BoneMapper


# ============================================================
# CREAR MOTION PLAN
# ============================================================

print("=== SIGNMUSIC MOTIONPLAN BLENDER TEST ===")


plan = MotionPlan(
    concept="SAVE",
    duration=0.8,
    fps=25,
)


plan.add_keyframe(
    time=0.0,
    phase="start",
    bones={
        "right_arm": {
            "rotation": [0, 0, 0],
        },
        "right_hand": {
            "rotation": [0, 0, 0],
        },
        "right_index_1": {
            "rotation": [0, 0, 0],
        },
    },
)


plan.add_keyframe(
    time=0.4,
    phase="motion",
    bones={
        "right_arm": {
            "rotation": [25, 0, 0],
        },
        "right_hand": {
            "rotation": [15, 0, 0],
        },
        "right_index_1": {
            "rotation": [20, 0, 0],
        },
    },
)


plan.add_keyframe(
    time=0.8,
    phase="end",
    bones={
        "right_arm": {
            "rotation": [0, 0, 0],
        },
        "right_hand": {
            "rotation": [0, 0, 0],
        },
        "right_index_1": {
            "rotation": [0, 0, 0],
        },
    },
)


# ============================================================
# VALIDAR
# ============================================================

errors = plan.validate()

if errors:
    raise RuntimeError(
        "MotionPlan inválido: "
        + "; ".join(errors)
    )

print("MotionPlan: OK")


# ============================================================
# BONE MAPPER
# ============================================================

mapper = BoneMapper()

print("BoneMapper: OK")


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

print(
    f"Importando avatar: {FBX_PATH}"
)

if not os.path.exists(FBX_PATH):
    raise FileNotFoundError(
        f"No existe el avatar: {FBX_PATH}"
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

scene.render.fps = plan.fps

scene.frame_start = 1

scene.frame_end = (
    round(plan.duration * plan.fps)
    + 1
)


print(
    f"FPS: {plan.fps}"
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
    name="SignMusic_MotionPlan_TEST"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# APLICAR KEYFRAMES
# ============================================================

print(
    "\n=== APLICANDO MOTION PLAN ==="
)


for keyframe in plan.keyframes:

    frame = (
        round(
            keyframe.time
            * plan.fps
        )
        + 1
    )

    scene.frame_set(frame)

    print(
        f"\nFrame {frame} | "
        f"Time {keyframe.time:.2f}s | "
        f"Phase: {keyframe.phase}"
    )


    # --------------------------------------------------------
    # MAPEAR HUESOS LÓGICOS
    # --------------------------------------------------------

    mapped_bones = mapper.map_transforms(
        keyframe.bones
    )


    for bone_name, transform in (
        mapped_bones.items()
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


        # ----------------------------------------------------
        # ROTACIÓN
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # POSICIÓN
        # ----------------------------------------------------

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


        # ----------------------------------------------------
        # ESCALA
        # ----------------------------------------------------

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
    exist_ok=True,
)


bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


# ============================================================
# RESULTADO
# ============================================================

print(
    "\n=== MOTIONPLAN BLENDER TEST COMPLETE ==="
)

print(
    f"Concept: {plan.concept}"
)

print(
    f"Duration: {plan.duration}s"
)

print(
    f"Keyframes: {len(plan.keyframes)}"
)

print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()