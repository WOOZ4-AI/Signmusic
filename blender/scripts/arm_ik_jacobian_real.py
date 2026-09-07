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
    "arm_ik_jacobian_real_v2.blend",
)

ARMATURE_NAME = "Armature"

ARM_BONE = "mixamorig7:RightArm"
FOREARM_BONE = "mixamorig7:RightForeArm"
HAND_BONE = "mixamorig7:RightHand"

ANGLE_NAMES = (
    "arm_x",
    "arm_z",
    "forearm_x",
    "forearm_z",
)

ANGLE_LIMITS = {
    "arm_x": (-90.0, 90.0),
    "arm_z": (-90.0, 90.0),
    "forearm_x": (-120.0, 120.0),
    "forearm_z": (-120.0, 120.0),
}

FPS = 25


# ============================================================
# IMPORTAR
# ============================================================

print(
    "=== SIGNMUSIC REAL JACOBIAN IK V2 ==="
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


def set_angles(angles):
    arm.rotation_mode = "XYZ"
    forearm.rotation_mode = "XYZ"

    arm.rotation_euler = (
        math.radians(
            float(angles["arm_x"])
        ),
        0.0,
        math.radians(
            float(angles["arm_z"])
        ),
    )

    forearm.rotation_euler = (
        math.radians(
            float(angles["forearm_x"])
        ),
        0.0,
        math.radians(
            float(angles["forearm_z"])
        ),
    )

    update()


def get_hand_position():
    update()

    matrix = (
        armature.matrix_world
        @ hand.matrix
    )

    return matrix.translation.copy()


def distance(a, b):
    return (
        a - b
    ).length


def clamp_angles(angles):
    result = {}

    for name in ANGLE_NAMES:

        value = float(
            angles.get(
                name,
                0.0,
            )
        )

        lower, upper = ANGLE_LIMITS[
            name
        ]

        result[name] = max(
            lower,
            min(
                upper,
                value,
            ),
        )

    return result


# ============================================================
# JACOBIAN REAL
# ============================================================

def numerical_jacobian(
    angles,
    epsilon_degrees=0.25,
):
    """
    Calcula:

        d(X,Y,Z) / d(ángulo)

    utilizando el avatar real.

    La derivada se expresa en:
        unidades de Blender / grado
    """

    jacobian = {}

    for name in ANGLE_NAMES:

        plus = dict(
            angles
        )

        minus = dict(
            angles
        )

        plus[name] += epsilon_degrees

        minus[name] -= epsilon_degrees

        plus = clamp_angles(
            plus
        )

        minus = clamp_angles(
            minus
        )

        set_angles(
            plus
        )

        position_plus = (
            get_hand_position()
        )

        set_angles(
            minus
        )

        position_minus = (
            get_hand_position()
        )

        delta = (
            position_plus
            - position_minus
        )

        denominator = (
            plus[name]
            - minus[name]
        )

        if abs(
            denominator
        ) < 1e-9:

            raise RuntimeError(
                f"No se pudo calcular "
                f"Jacobiano para {name}"
            )

        jacobian[name] = (
            delta.x / denominator,
            delta.y / denominator,
            delta.z / denominator,
        )

    return jacobian


# ============================================================
# MATRIZ 4x4
# ============================================================

def build_normal_matrix(
    jacobian,
    damping,
):
    """
    Construye:

        J^T J + λ²I

    donde:

        J = 3 x 4

    Resultado:

        4 x 4
    """

    matrix = [
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0],
    ]

    for row in range(4):

        a = jacobian[
            ANGLE_NAMES[row]
        ]

        for column in range(4):

            b = jacobian[
                ANGLE_NAMES[column]
            ]

            matrix[row][
                column
            ] = (
                a[0] * b[0]
                + a[1] * b[1]
                + a[2] * b[2]
            )

    damping_squared = (
        damping
        * damping
    )

    for index in range(4):

        matrix[index][
            index
        ] += damping_squared

    return matrix


# ============================================================
# INVERSA 4x4
# ============================================================

def inverse_4x4(
    matrix
):
    """
    Inversa mediante eliminación Gauss-Jordan.
    """

    size = 4

    augmented = []

    for row in range(size):

        augmented_row = [
            float(
                matrix[row][column]
            )
            for column in range(size)
        ]

        augmented_row += [
            1.0 if row == column else 0.0
            for column in range(size)
        ]

        augmented.append(
            augmented_row
        )

    for column in range(size):

        pivot_row = max(
            range(
                column,
                size,
            ),
            key=lambda row:
                abs(
                    augmented[row][column]
                ),
        )

        pivot = augmented[
            pivot_row
        ][column]

        if abs(
            pivot
        ) < 1e-12:

            return None

        if pivot_row != column:

            augmented[
                pivot_row
            ], augmented[
                column
            ] = (
                augmented[column],
                augmented[pivot_row],
            )

        pivot = augmented[
            column
        ][column]

        for j in range(
            column,
            size * 2,
        ):

            augmented[
                column
            ][j] /= pivot

        for row in range(size):

            if row == column:
                continue

            factor = augmented[
                row
            ][column]

            if abs(
                factor
            ) < 1e-15:

                continue

            for j in range(
                column,
                size * 2,
            ):

                augmented[
                    row
                ][j] -= (
                    factor
                    * augmented[
                        column
                    ][j]
                )

    return [
        row[size:]
        for row in augmented
    ]


# ============================================================
# MATRIX × VECTOR
# ============================================================

def matrix_vector(
    matrix,
    vector,
):

    return [
        sum(
            matrix[row][column]
            * vector[column]
            for column in range(
                len(vector)
            )
        )
        for row in range(
            len(matrix)
        )
    ]


# ============================================================
# Jᵀ × VECTOR
# ============================================================

def jacobian_transpose_vector(
    jacobian,
    vector,
):

    result = []

    for name in ANGLE_NAMES:

        column = jacobian[
            name
        ]

        result.append(
            column[0] * vector[0]
            + column[1] * vector[1]
            + column[2] * vector[2]
        )

    return result


# ============================================================
# SOLVER
# ============================================================

def solve_ik(
    target,
    max_iterations=100,
    tolerance=0.002,
):
    """
    IK mediante Levenberg-Marquardt simplificado:

        Δθ =
            (JᵀJ + λ²I)^-1
            Jᵀe

    """

    angles = {
        "arm_x": 0.0,
        "arm_z": 0.0,
        "forearm_x": 0.0,
        "forearm_z": 0.0,
    }

    damping = 0.03

    step_scale = 1.0

    current_position = None

    current_error = float(
        "inf"
    )

    print()
    print(
        "=== ITERACIONES IK ==="
    )

    for iteration in range(
        max_iterations
    ):

        set_angles(
            angles
        )

        current_position = (
            get_hand_position()
        )

        error_vector = (
            target
            - current_position
        )

        current_error = (
            error_vector.length
        )

        if iteration % 5 == 0:

            print(
                f"Iteration {iteration:3d} "
                f"Error={current_error:.6f}"
            )

        if current_error <= tolerance:

            break

        jacobian = (
            numerical_jacobian(
                angles
            )
        )

        normal = (
            build_normal_matrix(
                jacobian,
                damping,
            )
        )

        inverse = inverse_4x4(
            normal
        )

        if inverse is None:

            damping *= 2.0

            continue

        error_xyz = [
            error_vector.x,
            error_vector.y,
            error_vector.z,
        ]

        jt_error = (
            jacobian_transpose_vector(
                jacobian,
                error_xyz,
            )
        )

        delta = matrix_vector(
            inverse,
            jt_error,
        )

        candidate = dict(
            angles
        )

        for index, name in enumerate(
            ANGLE_NAMES
        ):

            # Los cálculos del Jacobiano son por grado,
            # así que delta ya está en grados.

            change = (
                delta[index]
                * step_scale
            )

            # Evitar saltos enormes.

            change = max(
                -8.0,
                min(
                    8.0,
                    change,
                ),
            )

            candidate[
                name
            ] += change

        candidate = clamp_angles(
            candidate
        )

        # -----------------------------------------------------
        # Comprobar candidato
        # -----------------------------------------------------

        set_angles(
            candidate
        )

        candidate_position = (
            get_hand_position()
        )

        candidate_error = (
            distance(
                candidate_position,
                target,
            )
        )

        if candidate_error < (
            current_error
        ):

            angles = candidate

            # Cuando mejora, podemos reducir algo
            # la amortiguación.

            damping = max(
                0.005,
                damping * 0.85,
            )

            step_scale = min(
                1.0,
                step_scale * 1.1,
            )

        else:

            # Cuando no mejora, hacemos el paso
            # más conservador.

            damping = min(
                1.0,
                damping * 2.0,
            )

            step_scale = max(
                0.1,
                step_scale * 0.5,
            )

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

    return {
        **angles,

        "position": [
            final_position.x,
            final_position.y,
            final_position.z,
        ],

        "error": final_error,

        "iterations": (
            iteration + 1
        ),

        "success": (
            final_error
            <= tolerance
        ),
    }


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = FPS

scene.frame_start = 1

scene.frame_end = 50


# ============================================================
# NEUTRAL
# ============================================================

reset_pose()

neutral = get_hand_position()

print()
print(
    "=== NEUTRAL ==="
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
# MOSTRAR JACOBIANO
# ============================================================

base_angles = {
    "arm_x": 0.0,
    "arm_z": 0.0,
    "forearm_x": 0.0,
    "forearm_z": 0.0,
}

jacobian = numerical_jacobian(
    base_angles
)

print()
print(
    "=== JACOBIAN REAL ==="
)

for name in ANGLE_NAMES:

    dx, dy, dz = jacobian[
        name
    ]

    print(
        f"{name}: "
        f"dX={dx:.8f} "
        f"dY={dy:.8f} "
        f"dZ={dz:.8f}"
    )


# ============================================================
# OBJETIVO
# ============================================================

target = neutral.copy()

target.z -= 0.10

print()
print(
    "=== TARGET ==="
)

print(
    f"X={target.x:.6f}"
)

print(
    f"Y={target.y:.6f}"
)

print(
    f"Z={target.z:.6f}"
)


# ============================================================
# RESOLVER
# ============================================================

reset_pose()

result = solve_ik(
    target=target,
    max_iterations=100,
    tolerance=0.002,
)


# ============================================================
# RESULTADO
# ============================================================

print()
print(
    "=== RESULTADO IK V2 ==="
)

print(
    f"Arm X       = "
    f"{result['arm_x']:.4f}°"
)

print(
    f"Arm Z       = "
    f"{result['arm_z']:.4f}°"
)

print(
    f"ForeArm X   = "
    f"{result['forearm_x']:.4f}°"
)

print(
    f"ForeArm Z   = "
    f"{result['forearm_z']:.4f}°"
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
    f"X={result['position'][0]:.6f} "
    f"Y={result['position'][1]:.6f} "
    f"Z={result['position'][2]:.6f}"
)

print()

print(
    f"ERROR={result['error']:.6f}"
)

print(
    f"ITERATIONS={result['iterations']}"
)

print(
    f"SUCCESS={result['success']}"
)


# ============================================================
# ANIMACIÓN
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
    25
)

set_angles(
    result
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
    "=== REAL JACOBIAN IK V2 COMPLETE ==="
)

print(
    f"Output: {OUTPUT_PATH}"
)


bpy.ops.wm.quit_blender()