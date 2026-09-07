import bpy
import json
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

SEQUENCE_PATH = os.path.join(
    PROJECT_ROOT,
    "blender",
    "output",
    "pipeline_sequence.json",
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
    "signmusic_pipeline_generated.blend",
)


# ============================================================
# INICIO
# ============================================================

print(
    "=== SIGNMUSIC PIPELINE SEQUENCE EXECUTOR ==="
)

print(
    f"Sequence: {SEQUENCE_PATH}"
)

print(
    f"Avatar: {FBX_PATH}"
)


# ============================================================
# VALIDAR ARCHIVOS
# ============================================================

if not os.path.exists(
    SEQUENCE_PATH
):
    raise FileNotFoundError(
        "No existe la secuencia JSON:\n"
        f"{SEQUENCE_PATH}"
    )

if not os.path.exists(
    FBX_PATH
):
    raise FileNotFoundError(
        "No existe el avatar FBX:\n"
        f"{FBX_PATH}"
    )


# ============================================================
# CARGAR SECUENCIA
# ============================================================

print()
print(
    "=== CARGANDO SECUENCIA ==="
)

with open(
    SEQUENCE_PATH,
    "r",
    encoding="utf-8",
) as file:

    sequence = json.load(
        file
    )


if not isinstance(
    sequence,
    dict,
):
    raise TypeError(
        "La secuencia JSON debe ser un objeto."
    )


animations = sequence.get(
    "animations",
    [],
)

if not isinstance(
    animations,
    list,
):
    raise TypeError(
        "'animations' debe ser una lista."
    )


fps = int(
    sequence.get(
        "fps",
        25,
    )
)

total_duration = float(
    sequence.get(
        "total_duration",
        0.0,
    )
)


print(
    f"FPS: {fps}"
)

print(
    f"Animaciones: {len(animations)}"
)

print(
    f"Duración total: {total_duration:.3f}s"
)


# ============================================================
# LIMPIAR ESCENA
# ============================================================

print()
print(
    "=== LIMPIANDO ESCENA ==="
)

bpy.ops.object.select_all(
    action="SELECT"
)

bpy.ops.object.delete(
    use_global=False
)


# ============================================================
# IMPORTAR AVATAR
# ============================================================

print()
print(
    "=== IMPORTANDO AVATAR ==="
)

bpy.ops.import_scene.fbx(
    filepath=FBX_PATH
)


# ============================================================
# BUSCAR ARMATURE
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

    if len(
        armatures
    ) == 1:

        armature = (
            armatures[0]
        )


if armature is None:
    raise RuntimeError(
        "No se encontró ningún Armature."
    )


print(
    f"Armature: {armature.name}"
)


# ============================================================
# ESCENA
# ============================================================

scene = bpy.context.scene

scene.render.fps = fps

scene.frame_start = 1

scene.frame_end = (
    max(
        1,
        round(
            total_duration
            * fps
        )
        + 1,
    )
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
    name="SignMusic_Pipeline_Generated"
)

armature.animation_data_create()

armature.animation_data.action = (
    action
)


# ============================================================
# ESTADÍSTICAS
# ============================================================

total_keyframes = 0

applied_bones = set()

warnings = []


# ============================================================
# APLICAR ANIMACIONES
# ============================================================

print()
print(
    "=== APLICANDO SECUENCIA ==="
)


for animation_index, animation in enumerate(
    animations
):

    concept = str(
        animation.get(
            "concept",
            "UNKNOWN",
        )
    )

    status = str(
        animation.get(
            "status",
            "undefined",
        )
    )

    start_time = float(
        animation.get(
            "start_time",
            0.0,
        )
    )

    duration = float(
        animation.get(
            "duration",
            0.0,
        )
    )

    print()
    print(
        "------------------------------------------------------------"
    )

    print(
        f"Animation {animation_index + 1}"
    )

    print(
        f"Concept: {concept}"
    )

    print(
        f"Status: {status}"
    )

    print(
        f"Start: {start_time:.3f}s"
    )

    print(
        f"Duration: {duration:.3f}s"
    )

    # --------------------------------------------------------
    # Animación sin datos
    # --------------------------------------------------------

    if status == "undefined":

        print(
            "→ Sin keyframes; se omite."
        )

        continue

    keyframes = animation.get(
        "keyframes",
        [],
    )

    if not isinstance(
        keyframes,
        list,
    ):

        warnings.append(
            f"{concept}: keyframes inválidos"
        )

        continue

    # --------------------------------------------------------
    # KEYFRAMES
    # --------------------------------------------------------

    for keyframe_index, keyframe in enumerate(
        keyframes
    ):

        if not isinstance(
            keyframe,
            dict,
        ):

            warnings.append(
                f"{concept}: "
                f"keyframe {keyframe_index} inválido"
            )

            continue

        # ----------------------------------------------------
        # Tiempo
        # ----------------------------------------------------

        absolute_time = (
            keyframe.get(
                "absolute_time"
            )
        )

        if absolute_time is None:

            local_time = float(
                keyframe.get(
                    "time",
                    0.0,
                )
            )

            absolute_time = (
                start_time
                + local_time
            )

        absolute_time = float(
            absolute_time
        )

        # ----------------------------------------------------
        # Frame
        # ----------------------------------------------------

        frame = keyframe.get(
            "frame"
        )

        if frame is None:

            frame = (
                round(
                    absolute_time
                    * fps
                )
                + 1
            )

        frame = int(
            frame
        )

        if frame < 1:

            warnings.append(
                f"{concept}: "
                f"frame inválido {frame}"
            )

            continue

        scene.frame_set(
            frame
        )

        print(
            f"  Frame {frame} | "
            f"Time {absolute_time:.3f}s | "
            f"Phase {keyframe.get('phase', '?')}"
        )

        bones = keyframe.get(
            "bones",
            {},
        )

        if not isinstance(
            bones,
            dict,
        ):

            warnings.append(
                f"{concept}: "
                f"keyframe {keyframe_index} "
                "no contiene bones válidos"
            )

            continue

        # ----------------------------------------------------
        # HUESOS
        # ----------------------------------------------------

        for bone_name, transform in bones.items():

            if not isinstance(
                bone_name,
                str,
            ):

                warnings.append(
                    f"{concept}: nombre de hueso inválido"
                )

                continue

            pose_bone = (
                armature.pose.bones.get(
                    bone_name
                )
            )

            if pose_bone is None:

                warning = (
                    f"{concept}: "
                    f"hueso no encontrado: "
                    f"{bone_name}"
                )

                warnings.append(
                    warning
                )

                print(
                    f"    WARNING: {bone_name}"
                )

                continue

            if not isinstance(
                transform,
                dict,
            ):

                warnings.append(
                    f"{concept}: "
                    f"transform inválido para "
                    f"{bone_name}"
                )

                continue

            applied_bones.add(
                bone_name
            )

            # ------------------------------------------------
            # ROTACIÓN
            # ------------------------------------------------

            if "rotation" in transform:

                rotation = transform[
                    "rotation"
                ]

                if (
                    isinstance(
                        rotation,
                        (list, tuple),
                    )
                    and len(rotation) >= 3
                ):

                    pose_bone.rotation_mode = (
                        "XYZ"
                    )

                    pose_bone.rotation_euler = (
                        math.radians(
                            float(
                                rotation[0]
                            )
                        ),

                        math.radians(
                            float(
                                rotation[1]
                            )
                        ),

                        math.radians(
                            float(
                                rotation[2]
                            )
                        ),
                    )

                    pose_bone.keyframe_insert(
                        data_path="rotation_euler",
                        frame=frame,
                        group=bone_name,
                    )

                else:

                    warnings.append(
                        f"{concept}: "
                        f"rotación inválida para "
                        f"{bone_name}"
                    )

            # ------------------------------------------------
            # POSICIÓN
            # ------------------------------------------------

            if "position" in transform:

                position = transform[
                    "position"
                ]

                if (
                    isinstance(
                        position,
                        (list, tuple),
                    )
                    and len(position) >= 3
                ):

                    pose_bone.location = (
                        float(
                            position[0]
                        ),

                        float(
                            position[1]
                        ),

                        float(
                            position[2]
                        ),
                    )

                    pose_bone.keyframe_insert(
                        data_path="location",
                        frame=frame,
                        group=bone_name,
                    )

                else:

                    warnings.append(
                        f"{concept}: "
                        f"posición inválida para "
                        f"{bone_name}"
                    )

            # ------------------------------------------------
            # ESCALA
            # ------------------------------------------------

            if "scale" in transform:

                scale = transform[
                    "scale"
                ]

                if (
                    isinstance(
                        scale,
                        (list, tuple),
                    )
                    and len(scale) >= 3
                ):

                    pose_bone.scale = (
                        float(
                            scale[0]
                        ),

                        float(
                            scale[1]
                        ),

                        float(
                            scale[2]
                        ),
                    )

                    pose_bone.keyframe_insert(
                        data_path="scale",
                        frame=frame,
                        group=bone_name,
                    )

                else:

                    warnings.append(
                        f"{concept}: "
                        f"escala inválida para "
                        f"{bone_name}"
                    )

            total_keyframes += 1


# ============================================================
# INTERPOLACIÓN
# ============================================================

print()
print(
    "=== CONFIGURANDO INTERPOLACIÓN ==="
)

# Para esta primera integración utilizamos
# interpolación BEZIER, que produce transiciones
# suaves entre los keyframes.

for curve_index in range(
    len(
        action.fcurves
    )
    if hasattr(
        action,
        "fcurves",
    )
    else 0
):

    fcurve = action.fcurves[
        curve_index
    ]

    for keyframe_point in (
        fcurve.keyframe_points
    ):

        keyframe_point.interpolation = (
            "BEZIER"
        )


print(
    "Interpolación configurada."
)


# ============================================================
# GUARDAR
# ============================================================

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)

print()
print(
    "=== GUARDANDO BLEND ==="
)

bpy.ops.wm.save_as_mainfile(
    filepath=OUTPUT_PATH
)


# ============================================================
# RESULTADO
# ============================================================

print()
print(
    "============================================================"
)

print(
    "=== SIGNMUSIC PIPELINE EXECUTION COMPLETE ==="
)

print(
    f"Animations: {len(animations)}"
)

print(
    f"Keyframe transforms: {total_keyframes}"
)

print(
    f"Unique bones applied: {len(applied_bones)}"
)

print(
    f"Warnings: {len(warnings)}"
)

print(
    f"Output: {OUTPUT_PATH}"
)

if warnings:

    print()
    print(
        "=== WARNINGS ==="
    )

    for warning in warnings[:50]:

        print(
            f"- {warning}"
        )

    if len(warnings) > 50:

        print(
            f"... y {len(warnings) - 50} warnings más."
        )


bpy.ops.wm.quit_blender()