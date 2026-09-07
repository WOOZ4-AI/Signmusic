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

ARMATURE_NAME = "Armature"
MESH_NAME = "Ch08_Body"

BONE_NAME = "mixamorig7:RightHandIndex1"

ANGLE = 45.0


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
    "=== SIGNMUSIC FINGER DEFORMATION MEASUREMENT ==="
)

print(
    f"Importando: {FBX_PATH}"
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
    raise RuntimeError(
        "No se encontró Armature."
    )


bone = armature.pose.bones.get(
    BONE_NAME
)

if bone is None:
    raise RuntimeError(
        f"No se encontró {BONE_NAME}"
    )


# ============================================================
# MESH
# ============================================================

mesh = bpy.data.objects.get(
    MESH_NAME
)

if mesh is None:
    raise RuntimeError(
        f"No se encontró {MESH_NAME}"
    )


print(
    f"Armature: {armature.name}"
)

print(
    f"Mesh: {mesh.name}"
)


# ============================================================
# ARMATURE MODIFIER
# ============================================================

armature_modifiers = [
    modifier
    for modifier in mesh.modifiers
    if modifier.type == "ARMATURE"
]

print()
print(
    "=== ARMATURE MODIFIER ==="
)

print(
    f"Cantidad: {len(armature_modifiers)}"
)

for modifier in armature_modifiers:

    print(
        f"Modifier: {modifier.name}"
    )

    print(
        f"  Object: "
        f"{modifier.object.name if modifier.object else None}"
    )

    print(
        f"  show_viewport: "
        f"{modifier.show_viewport}"
    )

    print(
        f"  show_render: "
        f"{modifier.show_render}"
    )


# ============================================================
# VERTICES CON PESO
# ============================================================

vertex_group = mesh.vertex_groups.get(
    BONE_NAME
)

if vertex_group is None:
    raise RuntimeError(
        f"No existe vertex group para {BONE_NAME}"
    )


weighted_indices = []

for vertex in mesh.data.vertices:

    try:
        weight = vertex_group.weight(
            vertex.index
        )

    except RuntimeError:
        continue

    if weight > 0:
        weighted_indices.append(
            vertex.index
        )


print()
print(
    "=== WEIGHTED VERTICES ==="
)

print(
    f"Vértices afectados: "
    f"{len(weighted_indices)}"
)


# ============================================================
# FUNCIÓN PARA OBTENER GEOMETRÍA EVALUADA
# ============================================================

def get_evaluated_coordinates():

    depsgraph = (
        bpy.context.evaluated_depsgraph_get()
    )

    evaluated_object = (
        mesh.evaluated_get(
            depsgraph
        )
    )

    evaluated_mesh = (
        evaluated_object.to_mesh()
    )

    coordinates = {}

    for index in weighted_indices:

        if index >= len(
            evaluated_mesh.vertices
        ):
            continue

        vertex = (
            evaluated_mesh.vertices[
                index
            ]
        )

        coordinates[index] = (
            tuple(vertex.co)
        )

    evaluated_object.to_mesh_clear()

    return coordinates


# ============================================================
# POSICIÓN NEUTRA
# ============================================================

scene = bpy.context.scene

scene.frame_set(1)

bone.rotation_mode = "XYZ"

bone.rotation_euler = (
    0.0,
    0.0,
    0.0,
)

bpy.context.view_layer.update()

neutral = (
    get_evaluated_coordinates()
)


print()
print(
    "Neutral pose capturada."
)


# ============================================================
# ROTAR BONE
# ============================================================

scene.frame_set(2)

bone.rotation_mode = "XYZ"

bone.rotation_euler = (
    math.radians(ANGLE),
    0.0,
    0.0,
)

bpy.context.view_layer.update()

rotated = (
    get_evaluated_coordinates()
)


print(
    f"Pose rotada: X = {ANGLE}°"
)


# ============================================================
# COMPARAR
# ============================================================

print()
print(
    "=== DEFORMATION DELTA ==="
)

changed_vertices = 0

max_delta = 0.0

max_vertex = None

for index in neutral:

    if index not in rotated:
        continue

    a = neutral[index]
    b = rotated[index]

    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]

    delta = math.sqrt(
        dx * dx
        + dy * dy
        + dz * dz
    )

    if delta > 0.000001:

        changed_vertices += 1

    if delta > max_delta:

        max_delta = delta
        max_vertex = index


print(
    f"Vértices que cambiaron: "
    f"{changed_vertices}"
)

print(
    f"Máximo desplazamiento: "
    f"{max_delta:.8f}"
)

print(
    f"Vertex máximo: "
    f"{max_vertex}"
)


# ============================================================
# RESULTADO
# ============================================================

print()
print(
    "=== RESULTADO ==="
)

if changed_vertices > 0:

    print(
        "DEFORMACIÓN REAL: SÍ"
    )

    print(
        "El mesh responde a la rotación del hueso."
    )

else:

    print(
        "DEFORMACIÓN REAL: NO"
    )

    print(
        "El mesh NO está cambiando aunque el hueso rote."
    )


print()
print(
    "=== MEASUREMENT COMPLETE ==="
)

bpy.ops.wm.quit_blender()