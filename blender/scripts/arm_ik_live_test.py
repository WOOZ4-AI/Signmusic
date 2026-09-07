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
    "arm_ik_live_test.blend",
)

ARMATURE_NAME = "Armature"

ARM_BONE = "mixamorig7:RightArm"
FOREARM_BONE = "mixamorig7:RightForeArm"
HAND_BONE = "mixamorig7:RightHand"

FPS = 25


# ============================================================
# LIMPIAR
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
    "=== SIGNMUSIC LIVE ARM IK TEST ==="
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
    f"Armature: {armature.name}"
)

print(
    "RightArm / RightForeArm / RightHand: OK"
)


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = FPS

scene.frame_start = 1

scene.frame_end = 100


# ============================================================
# UTILIDADES
# ============================================================

def reset_pose():
    """
    Devuelve brazo y antebrazo a neutral.
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


def get_hand_position():
    """
    Obtiene la posición mundial real de la mano.
    """

    bpy.context.view_layer.update()

    matrix = (
        armature.matrix_world
        @ hand.matrix
    )

    position = matrix.translation

    return Vector(
        (
            position.x,
            position.y,
            position.z,
        )
    )


def set_angles(
    arm_x,
    arm_z,
    forearm_x,
    forearm_z,
):
    """
    Aplica los cuatro grados de libertad
    de nuestra calibración.
    """

    arm.rotation_mode = "XYZ"

    forearm.rotation_mode = "XYZ"

    arm.rotation_euler = (
        math.radians(
            arm_x
        ),
        0.0,
        math.radians(
            arm_z
        ),
    )

    forearm.rotation_euler = (
        math.radians(
            forearm_x
        ),
        0.0,
        math.radians(
            forearm_z
        ),
    )

    bpy.context.view_layer.update()


def distance(
    a,
    b,
):
    return (
        a - b
    ).length


def evaluate(
    target,
):
    position = get_hand_position()

    return distance(
        position,
        target,
    )


# ============================================================
# POSICIÓN NEUTRAL
# ============================================================

reset_pose()

neutral = get_hand_position()

print()
print(
    "NEUTRAL"
)

print(
    f"X = {neutral.x:.6f}"
)

print(
    f"Y = {neutral.y:.6f}"
)

print(
    f"Z = {neutral.z:.6f}"
)


# ============================================================
# OBJETIVO
# ============================================================
#
# 10 cm hacia abajo en Z.
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
    "TARGET"
)

print(
    f"X = {target.x:.6f}"
)

print(
    f"Y = {target.y:.6f}"
)

print(
    f"Z = {target.z:.6f}"
)


# ============================================================
# BÚSQUEDA
# ============================================================

best = {
    "error": float("inf"),
    "arm_x": 0.0,
    "arm_z": 0.0,
    "forearm_x": 0.0,
    "forearm_z": 0.0,
}


# ============================================================
# BÚSQUEDA GRUESA
# ============================================================

print()
print(
    "=== BÚSQUEDA GRUESA ==="
)

for arm_x in range(
    -30,
    31,
    5,
):

    for arm_z in range(
        -30,
        31,
        5,
    ):

        for forearm_x in range(
            -30,
            31,
            5,
        ):

            for forearm_z in range(
                -30,
                31,
                5,
            ):

                reset_pose()

                set_angles(
                    arm_x,
                    arm_z,
                    forearm_x,
                    forearm_z,
                )

                error = evaluate(
                    target
                )

                if error < best[
                    "error"
                ]:

                    best = {
                        "error": error,
                        "arm_x": arm_x,
                        "arm_z": arm_z,
                        "forearm_x": forearm_x,
                        "forearm_z": forearm_z,
                    }


print(
    "Mejor resultado grueso:"
)

print(
    best
)


# ============================================================
# REFINAMIENTO
# ============================================================

print()
print(
    "=== REFINAMIENTO ==="
)

center = dict(
    best
)

step = 2.0

for _ in range(
    15
):

    improved = False

    for name in (
        "arm_x",
        "arm_z",
        "forearm_x",
        "forearm_z",
    ):

        original = float(
            center[name]
        )

        for delta in (
            -step,
            step,
        ):

            candidate = dict(
                center
            )

            candidate[
                name
            ] = (
                original
                + delta
            )

            reset_pose()

            set_angles(
                candidate["arm_x"],
                candidate["arm_z"],
                candidate["forearm_x"],
                candidate["forearm_z"],
            )

            error = evaluate(
                target
            )

            if error < center[
                "error"
            ]:

                center = {
                    **candidate,
                    "error": error,
                }

                improved = True

    if not improved:
        step *= 0.5

        if step < 0.1:
            break


# ============================================================
# RESULTADO
# ============================================================

reset_pose()

set_angles(
    center["arm_x"],
    center["arm_z"],
    center["forearm_x"],
    center["forearm_z"],
)

final_position = get_hand_position()

final_error = distance(
    final_position,
    target,
)


print()
print(
    "=== RESULTADO FINAL ==="
)

print(
    f"Arm X       = {center['arm_x']:.3f}°"
)

print(
    f"Arm Z       = {center['arm_z']:.3f}°"
)

print(
    f"ForeArm X   = {center['forearm_x']:.3f}°"
)

print(
    f"ForeArm Z   = {center['forearm_z']:.3f}°"
)

print()

print(
    "Target:"
)

print(
    f"  X={target.x:.6f}"
    f" Y={target.y:.6f}"
    f" Z={target.z:.6f}"
)

print()

print(
    "Final:"
)

print(
    f"  X={final_position.x:.6f}"
    f" Y={final_position.y:.6f}"
    f" Z={final_position.z:.6f}"
)

print()

print(
    f"Error = {final_error:.6f}"
)


# ============================================================
# GUARDAR ANIMACIÓN
# ============================================================

scene.frame_set(
    50
)

arm.keyframe_insert(
    data_path="rotation_euler",
    frame=50,
)

forearm.keyframe_insert(
    data_path="rotation_euler",
    frame=50,
)

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


print()
print(
    "=== LIVE ARM IK TEST COMPLETE ==="
)

print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()