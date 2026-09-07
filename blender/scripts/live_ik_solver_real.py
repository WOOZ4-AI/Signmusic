import bpy
import math
import os

from mathutils import Vector


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

OUTPUT_PATH = os.path.join(
    PROJECT_ROOT,
    "blender",
    "output",
    "live_ik_solver_real.blend",
)

ARMATURE_NAME = "Armature"

ARM_BONE = "mixamorig7:RightArm"
FOREARM_BONE = "mixamorig7:RightForeArm"
HAND_BONE = "mixamorig7:RightHand"

FPS = 25


# ============================================================
# IMPORTAR AVATAR
# ============================================================

print(
    "=== SIGNMUSIC REAL-TIME AVATAR IK TEST ==="
)

print(
    f"Importando: {FBX_PATH}"
)

if not os.path.exists(
    FBX_PATH
):
    raise FileNotFoundError(
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
    raise RuntimeError(
        "No se encontró Armature."
    )

arm = armature.pose.bones.get(
    ARM_BONE
)

forearm = armature.pose.bones.get(
    FOREARM_BONE
)

hand = armature.pose.bones.get(
    HAND_BONE
)

if arm is None:
    raise RuntimeError(
        f"No se encontró {ARM_BONE}"
    )

if forearm is None:
    raise RuntimeError(
        f"No se encontró {FOREARM_BONE}"
    )

if hand is None:
    raise RuntimeError(
        f"No se encontró {HAND_BONE}"
    )


print(
    "Armature: OK"
)


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = FPS

scene.frame_start = 1

scene.frame_end = 100


# ============================================================
# ACTION
# ============================================================

action = bpy.data.actions.new(
    name="LiveIKSolverReal"
)

armature.animation_data_create()

armature.animation_data.action = action


# ============================================================
# UTILIDADES
# ============================================================

def reset_pose():
    """
    Devuelve los huesos a posición neutra.
    """

    arm.rotation_mode = "XYZ"

    forearm.rotation_mode = "XYZ"

    hand.rotation_mode = "XYZ"

    arm.rotation_euler = (
        0.0,
        0.0,
        0.0,
    )

    forearm.rotation_euler = (
        0.0,
        0.0,
        0.0,
    )

    hand.rotation_euler = (
        0.0,
        0.0,
        0.0,
    )

    bpy.context.view_layer.update()


def set_angles(
    arm_x,
    arm_z,
    forearm_x,
    forearm_z,
):
    """
    Aplica los cuatro DOF calibrados.
    """

    arm.rotation_mode = "XYZ"

    forearm.rotation_mode = "XYZ"

    arm.rotation_euler = (
        math.radians(
            float(arm_x)
        ),
        0.0,
        math.radians(
            float(arm_z)
        ),
    )

    forearm.rotation_euler = (
        math.radians(
            float(forearm_x)
        ),
        0.0,
        math.radians(
            float(forearm_z)
        ),
    )

    bpy.context.view_layer.update()


def hand_position():
    """
    Posición mundial real de RightHand.
    """

    bpy.context.view_layer.update()

    matrix = (
        armature.matrix_world
        @ hand.matrix
    )

    return matrix.translation.copy()


def error_to_target(
    target,
):
    """
    Distancia entre la mano real y el objetivo.
    """

    current = hand_position()

    return (
        current
        - target
    ).length


# ============================================================
# POSICIÓN NEUTRAL
# ============================================================

reset_pose()

neutral = hand_position()

print()
print(
    "NEUTRAL:"
)

print(
    f"  X={neutral.x:.6f}"
)

print(
    f"  Y={neutral.y:.6f}"
)

print(
    f"  Z={neutral.z:.6f}"
)


# ============================================================
# OBJETIVO
# ============================================================
#
# Diez centímetros hacia abajo.
# ============================================================

target = Vector(
    (
        neutral.x,
        neutral.y,
        neutral.z - 0.10,
    )
)

print()
print(
    "TARGET:"
)

print(
    f"  X={target.x:.6f}"
)

print(
    f"  Y={target.y:.6f}"
)

print(
    f"  Z={target.z:.6f}"
)


# ============================================================
# SOLUCIÓN INICIAL
# ============================================================

best = {
    "arm_x": 0.0,
    "arm_z": 0.0,
    "forearm_x": 0.0,
    "forearm_z": 0.0,
}

reset_pose()

best_error = error_to_target(
    target
)


print()
print(
    "Initial error:",
    f"{best_error:.6f}"
)


# ============================================================
# BÚSQUEDA ADAPTATIVA
# ============================================================

steps = (
    10.0,
    5.0,
    2.0,
    1.0,
    0.5,
    0.25,
)

angle_names = (
    "arm_x",
    "arm_z",
    "forearm_x",
    "forearm_z",
)


# Límites razonables para evitar
# posiciones completamente absurdas.

limits = {
    "arm_x": (
        -90.0,
        90.0,
    ),

    "arm_z": (
        -90.0,
        90.0,
    ),

    "forearm_x": (
        -120.0,
        120.0,
    ),

    "forearm_z": (
        -120.0,
        120.0,
    ),
}


iterations = 0


for step in steps:

    improved = True

    while improved:

        improved = False

        for name in angle_names:

            current_value = (
                best[name]
            )

            candidates = (
                current_value - step,
                current_value + step,
            )

            for candidate in candidates:

                lower, upper = limits[
                    name
                ]

                candidate = max(
                    lower,
                    min(
                        upper,
                        candidate,
                    ),
                )

                trial = dict(
                    best
                )

                trial[
                    name
                ] = candidate

                set_angles(
                    trial["arm_x"],
                    trial["arm_z"],
                    trial["forearm_x"],
                    trial["forearm_z"],
                )

                error = (
                    error_to_target(
                        target
                    )
                )

                iterations += 1

                if error < best_error:

                    best = trial

                    best_error = error

                    improved = True

        if best_error <= 0.001:
            break

    if best_error <= 0.001:
        break


# ============================================================
# RESULTADO
# ============================================================

set_angles(
    best["arm_x"],
    best["arm_z"],
    best["forearm_x"],
    best["forearm_z"],
)

final_position = hand_position()

final_error = error_to_target(
    target
)


print()
print(
    "=== SOLUCIÓN IK REAL ==="
)

print(
    f"Arm X     = {best['arm_x']:.3f}°"
)

print(
    f"Arm Z     = {best['arm_z']:.3f}°"
)

print(
    f"ForeArm X = {best['forearm_x']:.3f}°"
)

print(
    f"ForeArm Z = {best['forearm_z']:.3f}°"
)

print()

print(
    "TARGET:"
)

print(
    f"  X={target.x:.6f}"
    f" Y={target.y:.6f}"
    f" Z={target.z:.6f}"
)

print()

print(
    "FINAL:"
)

print(
    f"  X={final_position.x:.6f}"
    f" Y={final_position.y:.6f}"
    f" Z={final_position.z:.6f}"
)

print()

print(
    f"FINAL ERROR = {final_error:.6f}"
)

print(
    f"ITERATIONS = {iterations}"
)


# ============================================================
# GUARDAR ANIMACIÓN
# ============================================================

scene.frame_set(
    1
)

reset_pose()

arm.keyframe_insert(
    data_path="rotation_euler",
    frame=1,
)

forearm.keyframe_insert(
    data_path="rotation_euler",
    frame=1,
)

scene.frame_set(
    50
)

set_angles(
    best["arm_x"],
    best["arm_z"],
    best["forearm_x"],
    best["forearm_z"],
)

arm.keyframe_insert(
    data_path="rotation_euler",
    frame=50,
)

forearm.keyframe_insert(
    data_path="rotation_euler",
    frame=50,
)


# ============================================================
# GUARDAR
# ============================================================

os.makedirs(
    os.path.dirname(
        OUTPUT_PATH
    ),
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
    "=== REAL IK TEST COMPLETE ==="
)

print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()