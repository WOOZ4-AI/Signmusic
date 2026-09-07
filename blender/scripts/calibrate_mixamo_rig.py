import bpy
import json
import math
from pathlib import Path
from mathutils import Vector, Euler


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
    / "mixamo_rig_calibration.json"
)

ARMATURE_NAME = "Armature"

TEST_FRAME = 1
TEST_ANGLE_DEG = 30.0

RIGHT_ARM = "mixamorig7:RightArm"
RIGHT_FOREARM = "mixamorig7:RightForeArm"


def find_bone(armature, exact_name):
    bone = armature.pose.bones.get(exact_name)

    if bone is not None:
        return bone

    return None


def find_right_hand_bone(armature):
    candidates = [
        "mixamorig7:RightHand",
        "mixamorig7:RightHandIndex1",
    ]

    for name in candidates:
        bone = armature.pose.bones.get(name)

        if bone is not None:
            return bone

    for bone in armature.pose.bones:
        name = bone.name.lower()

        if "righthand" in name and "index" not in name:
            return bone

    return None


def world_point_from_bone(bone):
    return bone.tail


def reset_scene_pose(scene):
    scene.frame_set(TEST_FRAME)
    bpy.context.view_layer.update()


def get_euler_rotation(bone):
    if bone.rotation_mode == "QUATERNION":
        return bone.rotation_quaternion.to_euler("XYZ")

    if bone.rotation_mode == "AXIS_ANGLE":
        return bone.rotation_axis_angle[:3]

    return bone.rotation_euler.copy()


def set_rotation_euler(bone, rotation):
    bone.rotation_mode = "XYZ"
    bone.rotation_euler = rotation
    bpy.context.view_layer.update()


def measure_rotation_test(
    armature,
    source_bone,
    target_bone,
    axis_index,
    angle_deg,
):
    reset_scene_pose(bpy.context.scene)

    source_bone = armature.pose.bones.get(
        source_bone.name
    )

    target_bone = armature.pose.bones.get(
        target_bone.name
    )

    baseline_target = world_point_from_bone(
        target_bone
    ).copy()

    baseline_rotation = get_euler_rotation(
        source_bone
    )

    plus_rotation = baseline_rotation.copy()
    plus_rotation[axis_index] += math.radians(
        angle_deg
    )

    set_rotation_euler(
        source_bone,
        plus_rotation,
    )

    plus_target = world_point_from_bone(
        target_bone
    ).copy()

    plus_delta = (
        plus_target - baseline_target
    )

    reset_scene_pose(
        bpy.context.scene
    )

    source_bone = armature.pose.bones.get(
        source_bone.name
    )

    baseline_rotation = get_euler_rotation(
        source_bone
    )

    minus_rotation = baseline_rotation.copy()
    minus_rotation[axis_index] -= math.radians(
        angle_deg
    )

    set_rotation_euler(
        source_bone,
        minus_rotation,
    )

    minus_target = world_point_from_bone(
        target_bone
    ).copy()

    minus_delta = (
        minus_target - baseline_target
    )

    reset_scene_pose(
        bpy.context.scene
    )

    return {
        "axis": ["X", "Y", "Z"][axis_index],
        "angle_deg": angle_deg,
        "plus_position": {
            "x": round(float(plus_target.x), 6),
            "y": round(float(plus_target.y), 6),
            "z": round(float(plus_target.z), 6),
        },
        "plus_delta": {
            "x": round(float(plus_delta.x), 6),
            "y": round(float(plus_delta.y), 6),
            "z": round(float(plus_delta.z), 6),
        },
        "plus_distance": round(
            float(plus_delta.length),
            6,
        ),
        "minus_position": {
            "x": round(float(minus_target.x), 6),
            "y": round(float(minus_target.y), 6),
            "z": round(float(minus_target.z), 6),
        },
        "minus_delta": {
            "x": round(float(minus_delta.x), 6),
            "y": round(float(minus_delta.y), 6),
            "z": round(float(minus_delta.z), 6),
        },
        "minus_distance": round(
            float(minus_delta.length),
            6,
        ),
    }


def direction_name(vector):
    absolute = {
        "X": abs(vector.x),
        "Y": abs(vector.y),
        "Z": abs(vector.z),
    }

    primary_axis = max(
        absolute,
        key=absolute.get,
    )

    value = getattr(
        vector,
        primary_axis.lower(),
    )

    if primary_axis == "X":
        return "RIGHT" if value > 0 else "LEFT"

    if primary_axis == "Y":
        return "FORWARD" if value > 0 else "BACKWARD"

    return "UP" if value > 0 else "DOWN"


def strongest_direction(test):
    vector = Vector(
        (
            test["plus_delta"]["x"],
            test["plus_delta"]["y"],
            test["plus_delta"]["z"],
        )
    )

    return {
        "direction": direction_name(vector),
        "vector": {
            "x": round(float(vector.x), 6),
            "y": round(float(vector.y), 6),
            "z": round(float(vector.z), 6),
        },
        "distance": round(
            float(vector.length),
            6,
        ),
    }


def print_test(label, test):
    print()
    print(label)
    print(
        f"  +{test['angle_deg']}° "
        f"{test['axis']} -> "
        f"delta "
        f"X={test['plus_delta']['x']:+.4f} "
        f"Y={test['plus_delta']['y']:+.4f} "
        f"Z={test['plus_delta']['z']:+.4f} "
        f"| distance={test['plus_distance']:.4f}"
    )

    print(
        f"  -{test['angle_deg']}° "
        f"{test['axis']} -> "
        f"delta "
        f"X={test['minus_delta']['x']:+.4f} "
        f"Y={test['minus_delta']['y']:+.4f} "
        f"Z={test['minus_delta']['z']:+.4f} "
        f"| distance={test['minus_distance']:.4f}"
    )


def main():
    print("=" * 70)
    print("SIGNMUSIC - CALIBRACION DEL RIG MIXAMO")
    print("=" * 70)

    print()
    print(f"Blend: {BLEND_PATH}")

    if not BLEND_PATH.exists():
        print()
        print("ERROR: No existe el archivo .blend.")
        return 1

    armature = bpy.data.objects.get(
        ARMATURE_NAME
    )

    if armature is None:
        print()
        print(
            f"ERROR: No se encontro '{ARMATURE_NAME}'."
        )

        print()
        print("Armatures disponibles:")

        for obj in bpy.data.objects:
            if obj.type == "ARMATURE":
                print(f"  - {obj.name}")

        return 1

    print(
        f"Armature: {armature.name}"
    )

    arm_bone = find_bone(
        armature,
        RIGHT_ARM,
    )

    forearm_bone = find_bone(
        armature,
        RIGHT_FOREARM,
    )

    hand_bone = find_right_hand_bone(
        armature
    )

    if arm_bone is None:
        print()
        print(
            f"ERROR: No se encontro {RIGHT_ARM}"
        )
        return 1

    if forearm_bone is None:
        print()
        print(
            f"ERROR: No se encontro {RIGHT_FOREARM}"
        )
        return 1

    if hand_bone is None:
        print()
        print(
            "ERROR: No se encontro un hueso de mano derecha."
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

    scene.frame_set(TEST_FRAME)
    bpy.context.view_layer.update()

    baseline_hand = (
        world_point_from_bone(
            hand_bone
        ).copy()
    )

    print()
    print(
        "Punto de referencia de la mano:"
    )

    print(
        f"  X={baseline_hand.x:.6f}"
        f" Y={baseline_hand.y:.6f}"
        f" Z={baseline_hand.z:.6f}"
    )

    result = {
        "project": "Signmusic",
        "avatar": "Ch08_nonPBR",
        "armature": armature.name,
        "frame": TEST_FRAME,
        "test_angle_deg": TEST_ANGLE_DEG,
        "target_bone": hand_bone.name,
        "baseline_hand": {
            "x": round(
                float(baseline_hand.x),
                6,
            ),
            "y": round(
                float(baseline_hand.y),
                6,
            ),
            "z": round(
                float(baseline_hand.z),
                6,
            ),
        },
        "tests": {
            "right_arm": {},
            "right_forearm": {},
        },
    }

    # ========================================================
    # CALIBRACION DEL BRAZO
    # ========================================================

    print()
    print("=" * 70)
    print("RIGHT ARM")
    print("=" * 70)

    for axis_index in range(3):
        test = measure_rotation_test(
            armature,
            arm_bone,
            hand_bone,
            axis_index,
            TEST_ANGLE_DEG,
        )

        result["tests"]["right_arm"][
            test["axis"]
        ] = test

        print_test(
            f"Axis {test['axis']}",
            test,
        )

    # ========================================================
    # CALIBRACION DEL ANTEBRAZO
    # ========================================================

    print()
    print("=" * 70)
    print("RIGHT FOREARM")
    print("=" * 70)

    for axis_index in range(3):
        test = measure_rotation_test(
            armature,
            forearm_bone,
            hand_bone,
            axis_index,
            TEST_ANGLE_DEG,
        )

        result["tests"]["right_forearm"][
            test["axis"]
        ] = test

        print_test(
            f"Axis {test['axis']}",
            test,
        )

    # ========================================================
    # RESUMEN DIRECCIONAL
    # ========================================================

    print()
    print("=" * 70)
    print("RESUMEN DIRECCIONAL")
    print("=" * 70)

    result["direction_summary"] = {
        "right_arm": {},
        "right_forearm": {},
    }

    for bone_group in [
        "right_arm",
        "right_forearm",
    ]:
        print()
        print(
            bone_group.upper()
        )

        for axis_name, test in result["tests"][
            bone_group
        ].items():

            summary = strongest_direction(
                test
            )

            result["direction_summary"][
                bone_group
            ][axis_name] = summary

            print(
                f"  {axis_name}: "
                f"{summary['direction']} "
                f"vector="
                f"({summary['vector']['x']:+.4f}, "
                f"{summary['vector']['y']:+.4f}, "
                f"{summary['vector']['z']:+.4f}) "
                f"distance={summary['distance']:.4f}"
            )

    # ========================================================
    # EJE MAS EFECTIVO
    # ========================================================

    result["strongest_axes"] = {}

    for bone_group in [
        "right_arm",
        "right_forearm",
    ]:
        candidates = []

        for axis_name, summary in result[
            "direction_summary"
        ][bone_group].items():

            candidates.append(
                (
                    summary["distance"],
                    axis_name,
                    summary,
                )
            )

        candidates.sort(
            reverse=True
        )

        if candidates:
            strongest = candidates[0]

            result["strongest_axes"][
                bone_group
            ] = {
                "axis": strongest[1],
                "distance": strongest[0],
                "summary": strongest[2],
            }

    print()
    print("=" * 70)
    print("EJES MAS EFECTIVOS")
    print("=" * 70)

    for bone_group, strongest in result[
        "strongest_axes"
    ].items():

        print(
            f"{bone_group}: "
            f"axis {strongest['axis']} "
            f"distance={strongest['distance']:.4f}"
        )

    # ========================================================
    # IMPORTANTE
    # ========================================================

    result["note"] = (
        "Esta calibracion mide como las rotaciones locales "
        "de los huesos RightArm y RightForeArm desplazan "
        "el hueso de la mano en coordenadas mundiales. "
        "Sirve para calibrar el rig, pero no determina por "
        "si sola la gramatica ni la forma linguistica de DGS."
    )

    # ========================================================
    # RESTAURAR FRAME ORIGINAL
    # ========================================================

    scene.frame_set(TEST_FRAME)
    bpy.context.view_layer.update()

    # ========================================================
    # GUARDAR
    # ========================================================

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
    print("=" * 70)
    print("CALIBRACION COMPLETADA")
    print("=" * 70)

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