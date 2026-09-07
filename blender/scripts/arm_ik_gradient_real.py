import bpy
import math
import os


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
    "arm_ik_gradient_real.blend",
)

ARMATURE_NAME = "Armature"

ARM_BONE = "mixamorig7:RightArm"
FOREARM_BONE = "mixamorig7:RightForeArm"
HAND_BONE = "mixamorig7:RightHand"

FPS = 25


# ============================================================
# IMPORTAR
# ============================================================

print(
    "=== SIGNMUSIC REAL GRADIENT IK ==="
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
# UTILIDADES
# ============================================================

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
    values,
):

    arm.rotation_mode = "XYZ"

    forearm.rotation_mode = "XYZ"

    arm.rotation_euler = (
        math.radians(
            values["arm_x"]
        ),
        0.0,
        math.radians(
            values["arm_z"]
        ),
    )

    forearm.rotation_euler = (
        math.radians(
            values["forearm_x"]
        ),
        0.0,
        math.radians(
            values["forearm_z"]
        ),
    )

    update()


def get_hand_position():

    update()

    matrix = (
        armature.matrix_world
        @ hand.matrix
    )

    return (
        matrix.translation.copy()
    )


def distance(
    a,
    b,
):

    dx = (
        a.x
        - b.x
    )

    dy = (
        a.y
        - b.y
    )

    dz = (
        a.z
        - b.z
    )

    return math.sqrt(
        dx * dx
        + dy * dy
        + dz * dz
    )


def evaluate(
    angles,
    target,
):

    set_angles(
        angles
    )

    position = (
        get_hand_position()
    )

    error = distance(
        position,
        target,
    )

    return (
        position,
        error,
    )


# ============================================================
# NEUTRAL
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

target = neutral.copy()

target.z -= 0.10

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
# PARÁMETROS
# ============================================================

angle_names = (
    "arm_x",
    "arm_z",
    "forearm_x",
    "forearm_z",
)

angles = {
    "arm_x": 0.0,
    "arm_z": 0.0,
    "forearm_x": 0.0,
    "forearm_z": 0.0,
}

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


# ============================================================
# GRADIENTE NUMÉRICO
# ============================================================

EPSILON = 0.5

LEARNING_RATE = 0.8

MAX_ITERATIONS = 120

TOLERANCE = 0.002


# ============================================================
# ERROR INICIAL
# ============================================================

reset_pose()

current_position = (
    get_hand_position()
)

current_error = distance(
    current_position,
    target,
)

print()
print(
    "Initial error:",
    f"{current_error:.6f}"
)


# ============================================================
# OPTIMIZACIÓN
# ============================================================

for iteration in range(
    MAX_ITERATIONS
):

    gradients = {}

    # ---------------------------------------------------------
    # Calcular gradiente de cada DOF
    # ---------------------------------------------------------

    for name in angle_names:

        original = angles[
            name
        ]

        # + epsilon

        plus = dict(
            angles
        )

        plus[
            name
        ] = original + EPSILON

        _, error_plus = evaluate(
            plus,
            target,
        )

        # - epsilon

        minus = dict(
            angles
        )

        minus[
            name
        ] = original - EPSILON

        _, error_minus = evaluate(
            minus,
            target,
        )

        gradient = (
            error_plus
            - error_minus
        ) / (
            2.0
            * EPSILON
        )

        gradients[
            name
        ] = gradient

    # ---------------------------------------------------------
    # Actualizar todos los DOF
    # ---------------------------------------------------------

    candidate = dict(
        angles
    )

    for name in angle_names:

        value = (
            angles[name]
            - (
                LEARNING_RATE
                * gradients[name]
            )
        )

        lower, upper = limits[
            name
        ]

        value = max(
            lower,
            min(
                upper,
                value,
            )
        )

        candidate[
            name
        ] = value

    candidate_position, candidate_error = evaluate(
        candidate,
        target,
    )

    # ---------------------------------------------------------
    # Aceptar si mejora
    # ---------------------------------------------------------

    if candidate_error < current_error:

        angles = candidate

        current_error = (
            candidate_error
        )

        current_position = (
            candidate_position
        )

    else:

        # Reducir learning rate

        LEARNING_RATE *= 0.5

    if iteration % 10 == 0:

        print(
            f"Iteration {iteration:3d} "
            f"Error = {current_error:.6f}"
        )

    if current_error <= (
        TOLERANCE
    ):
        break


# ============================================================
# RESULTADO
# ============================================================

set_angles(
    angles
)

final_position = (
    get_hand_position()
)

final_error = distance(
    final_position,
    target,
)


print()
print(
    "=== RESULTADO ==="
)

print(
    f"Iterations = {iteration + 1}"
)

print()

print(
    f"Arm X       = "
    f"{angles['arm_x']:.3f}°"
)

print(
    f"Arm Z       = "
    f"{angles['arm_z']:.3f}°"
)

print(
    f"ForeArm X   = "
    f"{angles['forearm_x']:.3f}°"
)

print(
    f"ForeArm Z   = "
    f"{angles['forearm_z']:.3f}°"
)

print()

print(
    "TARGET:"
)

print(
    f"X={target.x:.6f} "
    f"Y={target.y:.6f} "
    f"Z={target.z:.6f}"
)

print()

print(
    "FINAL:"
)

print(
    f"X={final_position.x:.6f} "
    f"Y={final_position.y:.6f} "
    f"Z={final_position.z:.6f}"
)

print()

print(
    f"FINAL ERROR = "
    f"{final_error:.6f}"
)


# ============================================================
# CREAR ANIMACIÓN
# ============================================================

scene = bpy.context.scene

scene.render.fps = FPS

scene.frame_start = 1

scene.frame_end = 50


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
    25
)

set_angles(
    angles
)

arm.keyframe_insert(
    data_path="rotation_euler",
    frame=25,
)

forearm.keyframe_insert(
    data_path="rotation_euler",
    frame=25,
)


scene.frame_set(
    50
)

reset_pose()

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


print()
print(
    "=== REAL GRADIENT IK COMPLETE ==="
)

print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()