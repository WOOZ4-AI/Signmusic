import bpy
import json
import math
from pathlib import Path
from mathutils import Vector


PROJECT_ROOT = Path.cwd()

BLEND_PATH = (
    PROJECT_ROOT
    / "blender"
    / "output"
    / "signmusic_pipeline_generated.blend"
)

OUTPUT_PATH = (
    PROJECT_ROOT
    / "blender"
    / "output"
    / "rig_direction_calibration.json"
)

ARMATURE_NAME = "Armature"

RIGHT_ARM = "mixamorig7:RightArm"
RIGHT_FOREARM = "mixamorig7:RightForeArm"

HAND_CANDIDATES = [
    "mixamorig7:RightHand",
    "RightHand",
]

TEST_FRAME = 1
TEST_ANGLE_DEG = 30.0


def get_hand_bone(armature):
    for name in HAND_CANDIDATES:
        bone = armature.pose.bones.get(name)

        if bone is not None:
            return bone

    for bone in armature.pose.bones:
        lowered = bone.name.lower()

        if "righthand" in lowered:
            if "thumb" not in lowered:
                if "index" not in lowered:
                    if "middle" not in lowered:
                        if "ring" not in lowered:
                            if "pinky" not in lowered:
                                return bone

    return None


def world_position(bone):
    return bone.tail.copy()


def reset_pose(scene):
    scene.frame_set(TEST_FRAME)
    bpy.context.view_layer.update()


def set_euler_xyz(bone, rotation):
    bone.rotation_mode = "XYZ"
    bone.rotation_euler = rotation
    bpy.context.view_layer.update()


def measure_single_rotation(
    armature,
    bone_name,
    hand_bone_name,
    axis_index,
    angle_deg,
):
    scene = bpy.context.scene

    reset_pose(scene)

    bone = armature.pose.bones.get(
        bone_name
    )

    hand = armature.pose.bones.get(
        hand_bone_name
    )

    if bone is None:
        raise RuntimeError(
            f"No se encontro el hueso {bone_name}"
        )

    if hand is None:
        raise RuntimeError(
            f"No se encontro el hueso {hand_bone_name}"
        )

    baseline_hand = world_position(hand)

    baseline_rotation = bone.rotation_euler.copy()

    plus_rotation = baseline_rotation.copy()
    plus_rotation[axis_index] += math.radians(
        angle_deg
    )

    set_euler_xyz(
        bone,
        plus_rotation,
    )

    plus_hand = world_position(hand)
    plus_delta = plus_hand - baseline_hand

    reset_pose(scene)

    bone = armature.pose.bones.get(
        bone_name
    )

    hand = armature.pose.bones.get(
        hand_bone_name
    )

    baseline_rotation = bone.rotation_euler.copy()

    minus_rotation = baseline_rotation.copy()
    minus_rotation[axis_index] -= math.radians(
        angle_deg
    )

    set_euler_xyz(
        bone,
        minus_rotation,
    )

    minus_hand = world_position(hand)
    minus_delta = minus_hand - baseline_hand

    reset_pose(scene)

    return {
        "bone": bone_name,
        "axis": ["X", "Y", "Z"][axis_index],
        "angle_deg": float(angle_deg),
        "plus": {
            "delta_world": {
                "x": round(float(plus_delta.x), 6),
                "y": round(float(plus_delta.y), 6),
                "z": round(float(plus_delta.z), 6),
            },
            "distance": round(
                float(plus_delta.length),
                6,
            ),
            "dominant_axis": dominant_axis(
                plus_delta
            ),
            "dominant_direction": dominant_direction(
                plus_delta
            ),
        },
        "minus": {
            "delta_world": {
                "x": round(float(minus_delta.x), 6),
                "y": round(float(minus_delta.y), 6),
                "z": round(float(minus_delta.z), 6),
            },
            "distance": round(
                float(minus_delta.length),
                6,
            ),
            "dominant_axis": dominant_axis(
                minus_delta
            ),
            "dominant_direction": dominant_direction(
                minus_delta
            ),
        },
    }


def dominant_axis(vector):
    values = {
        "X": abs(float(vector.x)),
        "Y": abs(float(vector.y)),
        "Z": abs(float(vector.z)),
    }

    return max(
        values,
        key=values.get,
    )


def dominant_direction(vector):
    axis = dominant_axis(vector)

    if axis == "X":
        if vector.x > 0:
            return "WORLD +X"
        return "WORLD -X"

    if axis == "Y":
        if vector.y > 0:
            return "WORLD +Y"
        return "WORLD -Y"

    if vector.z > 0:
        return "WORLD +Z"

    return "WORLD -Z"


def describe_direction(vector):
    x = float(vector.x)
    y = float(vector.y)
    z = float(vector.z)

    axis = dominant_axis(vector)

    if axis == "X":
        direction = "RIGHT" if x > 0 else "LEFT"

    elif axis == "Y":
        direction = "FORWARD" if y < 0 else "BACKWARD"

    else:
        direction = "UP" if z > 0 else "DOWN"

    return {
        "direction": direction,
        "dominant_axis": axis,
        "vector": {
            "x": round(x, 6),
            "y": round(y, 6),
            "z": round(z, 6),
        },
    }


def print_test(result):
    plus = result["plus"]
    minus = result["minus"]

    print()
    print(
        f'{result["bone"]} | Axis {result["axis"]}'
    )

    print(
        f'  +{result["angle_deg"]:.1f}° '
        f'-> '
        f'X={plus["delta_world"]["x"]:+.4f} '
        f'Y={plus["delta_world"]["y"]:+.4f} '
        f'Z={plus["delta_world"]["z"]:+.4f} '
        f'-> {plus["dominant_direction"]}'
    )

    print(
        f'  -{result["angle_deg"]:.1f}° '
        f'-> '
        f'X={minus["delta_world"]["x"]:+.4f} '
        f'Y={minus["delta_world"]["y"]:+.4f} '
        f'Z={minus["delta_world"]["z"]:+.4f} '
        f'-> {minus["dominant_direction"]}'
    )


def main():
    print("=" * 78)
    print("SIGNMUSIC - CALIBRACION DIRECCIONAL DEL RIG")
    print("=" * 78)

    print()
    print(f"Blend: {BLEND_PATH}")

    if not BLEND_PATH.exists():
        print()
        print(
            "ERROR: No existe el archivo .blend."
        )
        return 1

    armature = bpy.data.objects.get(
        ARMATURE_NAME
    )

    if armature is None:
        print()
        print(
            f"ERROR: No se encontro '{ARMATURE_NAME}'."
        )
        return 1

    arm_bone = armature.pose.bones.get(
        RIGHT_ARM
    )

    forearm_bone = armature.pose.bones.get(
        RIGHT_FOREARM
    )

    hand_bone = get_hand_bone(
        armature
    )

    if arm_bone is None:
        print(
            f"ERROR: No se encontro {RIGHT_ARM}"
        )
        return 1

    if forearm_bone is None:
        print(
            f"ERROR: No se encontro {RIGHT_FOREARM}"
        )
        return 1

    if hand_bone is None:
        print(
            "ERROR: No se encontro la mano derecha."
        )
        return 1

    print()
    print(
        f"RightArm: {arm_bone.name}"
    )

    print(
        f"RightForeArm: {forearm_bone.name}"
    )

    print(
        f"Hand target: {hand_bone.name}"
    )

    scene = bpy.context.scene
    reset_pose(scene)

    baseline = world_position(
        hand_bone
    )

    print()
    print("POSICION BASE DE LA MANO")
    print(
        f"X={baseline.x:.6f} "
        f"Y={baseline.y:.6f} "
        f"Z={baseline.z:.6f}"
    )

    result = {
        "project": "Signmusic",
        "blend": str(BLEND_PATH),
        "armature": armature.name,
        "test_frame": TEST_FRAME,
        "test_angle_deg": TEST_ANGLE_DEG,
        "hand_bone": hand_bone.name,
        "baseline_hand_world": {
            "x": round(float(baseline.x), 6),
            "y": round(float(baseline.y), 6),
            "z": round(float(baseline.z), 6),
        },
        "tests": {
            "right_arm": {},
            "right_forearm": {},
        },
        "candidate_directions": [],
    }

    # ==========================================================
    # RIGHT ARM
    # ==========================================================

    print()
    print("=" * 78)
    print("RIGHT ARM")
    print("=" * 78)

    for axis_index in range(3):
        measurement = measure_single_rotation(
            armature,
            RIGHT_ARM,
            hand_bone.name,
            axis_index,
            TEST_ANGLE_DEG,
        )

        axis_name = measurement["axis"]

        result["tests"]["right_arm"][
            axis_name
        ] = measurement

        print_test(
            measurement
        )

    # ==========================================================
    # RIGHT FOREARM
    # ==========================================================

    print()
    print("=" * 78)
    print("RIGHT FOREARM")
    print("=" * 78)

    for axis_index in range(3):
        measurement = measure_single_rotation(
            armature,
            RIGHT_FOREARM,
            hand_bone.name,
            axis_index,
            TEST_ANGLE_DEG,
        )

        axis_name = measurement["axis"]

        result["tests"]["right_forearm"][
            axis_name
        ] = measurement

        print_test(
            measurement
        )

    # ==========================================================
    # DIRECCIONES HUMANAS
    # ==========================================================

    print()
    print("=" * 78)
    print("INTERPRETACION DE DIRECCIONES")
    print("=" * 78)

    direction_candidates = []

    for bone_group in (
        "right_arm",
        "right_forearm",
    ):

        for axis_name, measurement in result[
            "tests"
        ][bone_group].items():

            for sign in (
                "plus",
                "minus",
            ):

                delta = Vector(
                    (
                        measurement[sign][
                            "delta_world"
                        ]["x"],
                        measurement[sign][
                            "delta_world"
                        ]["y"],
                        measurement[sign][
                            "delta_world"
                        ]["z"],
                    )
                )

                description = describe_direction(
                    delta
                )

                candidate = {
                    "bone_group": bone_group,
                    "axis": axis_name,
                    "rotation": (
                        f"+{measurement['angle_deg']}"
                        if sign == "plus"
                        else f"-{measurement['angle_deg']}"
                    ),
                    "sign": sign,
                    **description,
                    "distance": round(
                        float(delta.length),
                        6,
                    ),
                }

                direction_candidates.append(
                    candidate
                )

                print(
                    f'{bone_group:<15} '
                    f'axis={axis_name} '
                    f'{candidate["rotation"]:>7} '
                    f'-> '
                    f'{candidate["direction"]:<9} '
                    f'| '
                    f'axis={candidate["dominant_axis"]} '
                    f'| '
                    f'distance={candidate["distance"]:.4f}'
                )

    result["candidate_directions"] = (
        direction_candidates
    )

    # ==========================================================
    # CANDIDATOS PARA FORWARD
    # ==========================================================

    forward_candidates = [
        candidate
        for candidate in direction_candidates
        if candidate["direction"] == "FORWARD"
    ]

    forward_candidates.sort(
        key=lambda item: item["distance"],
        reverse=True,
    )

    result["forward_candidates"] = (
        forward_candidates
    )

    print()
    print("=" * 78)
    print("CANDIDATOS PARA FORWARD")
    print("=" * 78)

    if not forward_candidates:
        print(
            "NO se encontro un movimiento dominante "
            "clasificado como FORWARD."
        )

    else:
        for candidate in forward_candidates:
            print(
                f'{candidate["bone_group"]} | '
                f'Axis {candidate["axis"]} | '
                f'{candidate["rotation"]} | '
                f'distance={candidate["distance"]:.4f}'
            )

    # ==========================================================
    # GUARDAR
    # ==========================================================

    result["note"] = (
        "La direccion FORWARD se define aqui como "
        "WORLD -Y porque la camara de validacion esta "
        "situada en Y negativo. La calibracion sirve "
        "para determinar que rotacion local acerca la "
        "mano hacia la camara, no para validar por si "
        "sola la forma linguistica de un signo DGS."
    )

    reset_pose(scene)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    OUTPUT_PATH.write_text(
        json.dumps(
            result,
            indent=4,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print()
    print("=" * 78)
    print("CALIBRACION COMPLETADA")
    print("=" * 78)

    print()
    print(
        f"Resultado: {OUTPUT_PATH}"
    )

    print()
    print(
        "El .blend NO ha sido modificado ni guardado."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())