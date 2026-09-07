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
    "=== SIGNMUSIC 3D ARM REACHABILITY TEST ==="
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


LIMITS = {
    "arm_x": (-45.0, 45.0),
    "arm_z": (-45.0, 45.0),
    "forearm_x": (-60.0, 60.0),
    "forearm_z": (-60.0, 60.0),
}


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


def get_hand_position():

    update()

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


def axis_error(
    actual,
    target,
):

    return {
        "x": abs(
            actual.x
            - target.x
        ),

        "y": abs(
            actual.y
            - target.y
        ),

        "z": abs(
            actual.z
            - target.z
        ),
    }


# ============================================================
# BÚSQUEDA DE UN EJE
# ============================================================

def search_target(
    neutral,
    target,
    primary_axis,
):

    best = {
        "error": float("inf"),

        "arm_x": 0.0,
        "arm_z": 0.0,
        "forearm_x": 0.0,
        "forearm_z": 0.0,
    }

    # --------------------------------------------------------
    # Primera búsqueda
    # --------------------------------------------------------

    for arm_x in range(
        -30,
        31,
        2,
    ):

        for arm_z in range(
            -30,
            31,
            2,
        ):

            for forearm_x in range(
                -30,
                31,
                2,
            ):

                for forearm_z in range(
                    -30,
                    31,
                    2,
                ):

                    angles = {
                        "arm_x": float(
                            arm_x
                        ),

                        "arm_z": float(
                            arm_z
                        ),

                        "forearm_x": float(
                            forearm_x
                        ),

                        "forearm_z": float(
                            forearm_z
                        ),
                    }

                    set_angles(
                        angles
                    )

                    actual = (
                        get_hand_position()
                    )

                    errors = axis_error(
                        actual,
                        target,
                    )

                    # ------------------------------------------------
                    # Pesos según el eje que estamos intentando mover
                    # ------------------------------------------------

                    if primary_axis == "x":

                        error = (
                            errors["x"]
                            + errors["y"] * 0.15
                            + errors["z"] * 0.15
                        )

                    elif primary_axis == "y":

                        error = (
                            errors["y"]
                            + errors["x"] * 0.15
                            + errors["z"] * 0.15
                        )

                    else:

                        error = (
                            errors["z"]
                            + errors["x"] * 0.15
                            + errors["y"] * 0.15
                        )

                    if error < best[
                        "error"
                    ]:

                        best = {
                            "error": error,
                            **angles,
                        }

    # --------------------------------------------------------
    # Refinamiento
    # --------------------------------------------------------

    step = 1.0

    for _ in range(
        15
    ):

        improved = True

        while improved:

            improved = False

            for name in ANGLE_NAMES:

                original = best[
                    name
                ]

                candidates = (
                    original - step,
                    original + step,
                )

                for candidate in candidates:

                    lower, upper = LIMITS[
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
                        trial
                    )

                    actual = (
                        get_hand_position()
                    )

                    errors = axis_error(
                        actual,
                        target,
                    )

                    if primary_axis == "x":

                        error = (
                            errors["x"]
                            + errors["y"] * 0.15
                            + errors["z"] * 0.15
                        )

                    elif primary_axis == "y":

                        error = (
                            errors["y"]
                            + errors["x"] * 0.15
                            + errors["z"] * 0.15
                        )

                    else:

                        error = (
                            errors["z"]
                            + errors["x"] * 0.15
                            + errors["y"] * 0.15
                        )

                    if error < best[
                        "error"
                    ]:

                        best = {
                            "error": error,
                            **trial,
                        }

                        improved = True

        step *= 0.5

        if step < 0.1:
            break

    set_angles(
        best
    )

    final = get_hand_position()

    return (
        best,
        final,
    )


# ============================================================
# NEUTRAL
# ============================================================

reset_pose()

neutral = get_hand_position()

print()
print(
    "NEUTRAL:"
)

print(
    f"X={neutral.x:.6f} "
    f"Y={neutral.y:.6f} "
    f"Z={neutral.z:.6f}"
)


# ============================================================
# OBJETIVOS
# ============================================================

targets = [

    (
        "DOWN 0.10",
        Vector(
            (
                neutral.x,
                neutral.y,
                neutral.z - 0.10,
            )
        ),
        "z",
    ),

    (
        "UP 0.10",
        Vector(
            (
                neutral.x,
                neutral.y,
                neutral.z + 0.10,
            )
        ),
        "z",
    ),

    (
        "RIGHT 0.10",
        Vector(
            (
                neutral.x + 0.10,
                neutral.y,
                neutral.z,
            )
        ),
        "x",
    ),

    (
        "LEFT 0.10",
        Vector(
            (
                neutral.x - 0.10,
                neutral.y,
                neutral.z,
            )
        ),
        "x",
    ),

    (
        "FRONT 0.10",
        Vector(
            (
                neutral.x,
                neutral.y + 0.10,
                neutral.z,
            )
        ),
        "y",
    ),

    (
        "BACK 0.10",
        Vector(
            (
                neutral.x,
                neutral.y - 0.10,
                neutral.z,
            )
        ),
        "y",
    ),
]


# ============================================================
# EJECUTAR PRUEBAS
# ============================================================

for label, target, axis in targets:

    reset_pose()

    print()
    print(
        "============================================================"
    )

    print(
        label
    )

    print(
        f"TARGET:"
        f" X={target.x:.6f}"
        f" Y={target.y:.6f}"
        f" Z={target.z:.6f}"
    )

    best, final = search_target(
        neutral,
        target,
        axis,
    )

    print()
    print(
        "ANGLES:"
    )

    print(
        f"  Arm X       = "
        f"{best['arm_x']:.3f}°"
    )

    print(
        f"  Arm Z       = "
        f"{best['arm_z']:.3f}°"
    )

    print(
        f"  ForeArm X   = "
        f"{best['forearm_x']:.3f}°"
    )

    print(
        f"  ForeArm Z   = "
        f"{best['forearm_z']:.3f}°"
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
        "ABSOLUTE ERROR:"
    )

    print(
        f"  X={abs(final.x - target.x):.6f}"
    )

    print(
        f"  Y={abs(final.y - target.y):.6f}"
    )

    print(
        f"  Z={abs(final.z - target.z):.6f}"
    )


# ============================================================
# FINAL
# ============================================================

print()
print(
    "=== 3D REACHABILITY TEST COMPLETE ==="
)

bpy.ops.wm.quit_blender()