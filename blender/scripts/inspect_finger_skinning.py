import bpy
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


ARMATURE_NAME = "Armature"

BONES_TO_CHECK = [
    "mixamorig7:RightHand",
    "mixamorig7:RightHandIndex1",
    "mixamorig7:RightHandIndex2",
    "mixamorig7:RightHandIndex3",
]


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
    "=== SIGNMUSIC FINGER SKINNING INSPECTOR ==="
)

print(
    f"Importando avatar: {FBX_PATH}"
)

if not os.path.exists(FBX_PATH):
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

    armatures = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "ARMATURE"
    ]

    if len(armatures) == 1:
        armature = armatures[0]


if armature is None:
    raise RuntimeError(
        "No se encontró el Armature."
    )


print(
    f"\nArmature: {armature.name}"
)

print(
    f"Huesos totales: "
    f"{len(armature.data.bones)}"
)


# ============================================================
# COMPROBAR HUESOS
# ============================================================

print()
print(
    "=== BONE DEFORM ==="
)

for bone_name in BONES_TO_CHECK:

    edit_or_data_bone = (
        armature.data.bones.get(
            bone_name
        )
    )

    pose_bone = (
        armature.pose.bones.get(
            bone_name
        )
    )

    print()
    print(
        bone_name
    )

    if edit_or_data_bone is None:

        print(
            "  EXISTE: NO"
        )

        continue

    print(
        "  EXISTE: SÍ"
    )

    print(
        "  use_deform:",
        edit_or_data_bone.use_deform
    )

    if edit_or_data_bone.parent:

        print(
            "  parent:",
            edit_or_data_bone.parent.name
        )

    else:

        print(
            "  parent: None"
        )

    if pose_bone:

        print(
            "  pose bone: OK"
        )


# ============================================================
# MESHES
# ============================================================

print()
print(
    "=== MESHES Y ARMATURE MODIFIERS ==="
)

meshes = [
    obj
    for obj in bpy.context.scene.objects
    if obj.type == "MESH"
]


print(
    f"Meshes encontrados: "
    f"{len(meshes)}"
)


for mesh in meshes:

    print()
    print(
        f"MESH: {mesh.name}"
    )

    armature_modifiers = [
        modifier
        for modifier in mesh.modifiers
        if modifier.type == "ARMATURE"
    ]

    print(
        f"  Armature modifiers: "
        f"{len(armature_modifiers)}"
    )

    for modifier in armature_modifiers:

        print(
            "  → modifier.object:",
            modifier.object.name
            if modifier.object
            else None
        )


    # --------------------------------------------------------
    # VERTEX GROUPS
    # --------------------------------------------------------

    group_names = {
        group.name
        for group in mesh.vertex_groups
    }

    print(
        f"  Vertex groups: "
        f"{len(group_names)}"
    )

    for bone_name in BONES_TO_CHECK:

        print(
            f"  Vertex group "
            f"{bone_name}: "
            f"{'SÍ' if bone_name in group_names else 'NO'}"
        )


# ============================================================
# COMPROBAR PESOS
# ============================================================

print()
print(
    "=== PESOS DE VERTEX GROUPS ==="
)

for mesh in meshes:

    group_by_name = {
        group.name: group
        for group in mesh.vertex_groups
    }

    for bone_name in BONES_TO_CHECK:

        group = group_by_name.get(
            bone_name
        )

        if group is None:

            print()
            print(
                f"{mesh.name} → {bone_name}"
            )

            print(
                "  Grupo: NO EXISTE"
            )

            continue

        total_weight = 0.0

        vertex_count = 0

        for vertex in mesh.data.vertices:

            try:

                weight = group.weight(
                    vertex.index
                )

            except RuntimeError:

                continue

            if weight > 0:

                total_weight += weight

                vertex_count += 1

        print()
        print(
            f"{mesh.name} → {bone_name}"
        )

        print(
            f"  Vértices con peso: "
            f"{vertex_count}"
        )

        print(
            f"  Peso acumulado: "
            f"{total_weight:.4f}"
        )


# ============================================================
# FINAL
# ============================================================

print()
print(
    "=== INSPECCIÓN COMPLETA ==="
)

bpy.ops.wm.quit_blender()