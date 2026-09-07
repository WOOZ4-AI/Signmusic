import bpy
import os


# ============================================================
# ARCHIVO
# ============================================================

PROJECT_ROOT = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
    )
)

BLEND_PATH = os.path.join(
    PROJECT_ROOT,
    "blender",
    "output",
    "signmusic_finger_pipeline_test.blend",
)


# ============================================================
# ABRIR BLEND
# ============================================================

print("=== SIGNMUSIC FINGER ACTION INSPECTOR ===")

if not os.path.exists(BLEND_PATH):
    raise FileNotFoundError(
        f"No existe:\n{BLEND_PATH}"
    )

bpy.ops.wm.open_mainfile(
    filepath=BLEND_PATH
)


# ============================================================
# ARMATURE
# ============================================================

armature = bpy.data.objects.get(
    "Armature"
)

if armature is None:
    raise RuntimeError(
        "No se encontró Armature."
    )

print(
    f"Armature: {armature.name}"
)


# ============================================================
# ACTION
# ============================================================

animation_data = armature.animation_data

if animation_data is None:
    raise RuntimeError(
        "El Armature no tiene animation_data."
    )

action = animation_data.action

if action is None:
    raise RuntimeError(
        "El Armature no tiene una Action activa."
    )

print(
    f"Action: {action.name}"
)


# ============================================================
# HUESOS
# ============================================================

FINGER_BONES = [
    "mixamorig7:RightHandIndex1",
    "mixamorig7:RightHandIndex2",
    "mixamorig7:RightHandIndex3",

    "mixamorig7:RightHandMiddle1",
    "mixamorig7:RightHandMiddle2",
    "mixamorig7:RightHandMiddle3",

    "mixamorig7:RightHandRing1",
    "mixamorig7:RightHandRing2",
    "mixamorig7:RightHandRing3",

    "mixamorig7:RightHandPinky1",
    "mixamorig7:RightHandPinky2",
    "mixamorig7:RightHandPinky3",
]


# ============================================================
# F-CURVES / CHANNELS
# ============================================================

print()
print("=== FINGER ANIMATION CHANNELS ===")

finger_channels = []

try:
    slots = list(action.slots)
except Exception:
    slots = []

print(
    f"Action slots: {len(slots)}"
)

for slot_index, slot in enumerate(slots):

    print()
    print(
        f"Slot {slot_index}: {slot!r}"
    )

    # Blender 5.x puede identificar el slot mediante
    # diferentes propiedades según el tipo de Action.
    for attribute in (
        "identifier",
        "name_display",
        "name",
        "id_root",
        "target_id_type",
    ):

        try:
            value = getattr(
                slot,
                attribute,
            )
        except Exception:
            continue

        print(
            f"  {attribute}: {value!r}"
        )

    # --------------------------------------------------------
    # Intentar obtener el channelbag
    # --------------------------------------------------------

    channelbag = None

    try:
        channelbag = action.channelbag(
            slot
        )
    except Exception as exc:

        print(
            f"  channelbag(): ERROR: {exc}"
        )

    if channelbag is None:

        print(
            "  Sin channelbag."
        )

        continue

    print(
        "  Channelbag encontrado."
    )

    # --------------------------------------------------------
    # FCurves
    # --------------------------------------------------------

    try:
        fcurves = list(
            channelbag.fcurves
        )
    except Exception as exc:

        print(
            f"  No se pudieron obtener FCurves: {exc}"
        )

        continue

    print(
        f"  FCurves totales: {len(fcurves)}"
    )

    for fcurve in fcurves:

        try:
            data_path = fcurve.data_path
        except Exception:
            data_path = ""

        is_finger_curve = any(
            name in data_path
            for name in (
                "RightHandIndex",
                "RightHandMiddle",
                "RightHandRing",
                "RightHandPinky",
            )
        )

        if not is_finger_curve:
            continue

        finger_channels.append(
            fcurve
        )

        print()
        print(
            f"  {data_path}"
        )

        try:
            print(
                f"    array_index: "
                f"{fcurve.array_index}"
            )
        except Exception:
            pass

        try:

            print(
                "    keyframes:"
            )

            for point in (
                fcurve.keyframe_points
            ):

                print(
                    f"      frame="
                    f"{point.co.x:.0f} "
                    f"value="
                    f"{point.co.y:.6f}"
                )

        except Exception as exc:

            print(
                f"    Error leyendo keyframes: {exc}"
            )


print()
print(
    f"Total finger channels: "
    f"{len(finger_channels)}"
)

# ============================================================
# EVALUACIÓN REAL DEL AVATAR
# ============================================================

print()
print("=== EVALUATED POSE ===")

for frame in (
    1,
    11,
    21,
):

    bpy.context.scene.frame_set(
        frame
    )

    bpy.context.view_layer.update()

    print()
    print(
        f"FRAME {frame}"
    )

    for bone_name in FINGER_BONES:

        bone = armature.pose.bones.get(
            bone_name
        )

        if bone is None:
            print(
                f"  MISSING: {bone_name}"
            )
            continue

        print(
            f"  {bone_name}: "
            f"X={bone.rotation_euler.x:.6f} "
            f"Y={bone.rotation_euler.y:.6f} "
            f"Z={bone.rotation_euler.z:.6f}"
        )


# ============================================================
# CONSTRAINTS
# ============================================================

print()
print("=== FINGER CONSTRAINTS ===")

for bone_name in FINGER_BONES:

    bone = armature.pose.bones.get(
        bone_name
    )

    if bone is None:
        continue

    if bone.constraints:

        print(
            f"\n{bone_name}"
        )

        for constraint in bone.constraints:

            print(
                f"  {constraint.type}: "
                f"{constraint.name}"
            )


# ============================================================
# RESULTADO
# ============================================================

print()
print(
    "=== INSPECTION COMPLETE ==="
)

bpy.ops.wm.quit_blender()