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
# IMPORTAR
# ============================================================

print(
    "=== SIGNMUSIC ARM IK REACHABILITY TEST ==="
)

print(
    f"Importando: {FBX_PATH}"
)

if not os.path.exists(FBX_PATH):
    raise FileNotFoundError(FBX_PATH)

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
# UTILIDADES
# ============================================================

ANGLE_NAMES = (
    "arm_x",
    "arm_z",
    "forearm_x",
    "forearm_z",
)


def update():
    bpy.context.view_layer.update()


def reset_pose():

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

    update()


def set_angles(
    angles,
):

    arm.rotation_mode = "XYZ"

    forearm.rotation_mode = "XYZ"

    arm.rotation_euler = (
        math.radians(
            angles["arm_x"]
        ),
        0.0,
        math.radians(
            angles["arm_z"]
        ),
    )

    forearm.rotation_euler = (
        math.radians(
            angles["forearm_x"]
        ),
        0.0,
        math.radians(
            angles["forearm_z"]
        ),
    )

    update()


def hand_position():

    update()

    matrix = (
        armature.matrix_world
        @ hand.matrix
    )

    return matrix.translation.copy()


# ============================================================
# NEUTRAL
# ============================================================

reset_pose()

neutral = hand_position()

print()
print(
    "NEUTRAL"
)

print(
    f"X={neutral.x:.6f}"
)

print(
    f"Y={neutral.y:.6f}"
)

print(
    f"Z={neutral.z:.6f}"
)


# ============================================================
# OBJETIVOS SOLO EN Z
# ============================================================

z_offsets = (
    -0.02,
    -0.04,
    -0.06,
    -0.08,
    -0.10,
    0.05,
    0.10,
)


# ============================================================
# BÚSQUEDA
# ============================================================

for offset in z_offsets:

    target_z = (
        neutral.z
        + offset
    )

    target = Vector(
        (
            neutral.x,
            neutral.y,
            target_z,
        )
    )

    best = {
        "error": float("inf"),

        "arm_x": 0.0,
        "arm_z": 0.0,

        "forearm_x": 0.0,
        "forearm_z": 0.0,
    }

    print()
    print(
        "============================================================"
    )

    print(
        f"TARGET Z OFFSET = {offset:+.3f}"
    )

    print(
        f"TARGET Z = {target_z:.6f}"
    )

    # ---------------------------------------------------------
    # Búsqueda en los dos DOF principales para Z
    # ---------------------------------------------------------

    for arm_x in range(
        -25,
        26,
        2,
    ):

        for forearm_x in range(
            -25,
            26,
            2,
        ):

            angles = {
                "arm_x": float(
                    arm_x
                ),

                "arm_z": 0.0,

                "forearm_x": float(
                    forearm_x
                ),

                "forearm_z": 0.0,
            }

            set_angles(
                angles
            )

            position = (
                hand_position()
            )

            # -----------------------------------------------
            # Error únicamente en Z
            # -----------------------------------------------

            error = abs(
                position.z
                - target.z
            )

            if error < best[
                "error"
            ]:

                best = {
                    "error": error,

                    **angles,
                }

    # ---------------------------------------------------------
    # Aplicar mejor solución
    # ---------------------------------------------------------

    set_angles(
        best
    )

    final = hand_position()

    print()
    print(
        "BEST SOLUTION"
    )

    print(
        f"Arm X       = {best['arm_x']:.3f}°"
    )

    print(
        f"ForeArm X   = {best['forearm_x']:.3f}°"
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
        f"  X={final.x:.6f}"
        f" Y={final.y:.6f}"
        f" Z={final.z:.6f}"
    )

    print()

    print(
        "Z ERROR = "
        f"{abs(final.z - target.z):.6f}"
    )


# ============================================================
# FINAL
# ============================================================

print()
print(
    "=== REACHABILITY TEST COMPLETE ==="
)

bpy.ops.wm.quit_blender()