import bpy


print("=== SIGNMUSIC AVATAR INSPECTION ===")

# Limpiar escena
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Importar FBX
fbx_path = "blender/assets/Ch08_nonPBR.fbx"

bpy.ops.import_scene.fbx(filepath=fbx_path)

print(f"Imported FBX: {fbx_path}")
print()

# Mostrar objetos
print("=== OBJECTS ===")

for obj in bpy.context.scene.objects:
    print(
        f"- {obj.name} | "
        f"type={obj.type}"
    )

# Buscar armatures
print()
print("=== ARMATURES ===")

armatures = [
    obj
    for obj in bpy.context.scene.objects
    if obj.type == "ARMATURE"
]

for armature in armatures:
    print(f"Armature: {armature.name}")
    print(f"Bones: {len(armature.data.bones)}")
    print()

    print("=== BONES ===")

    for bone in armature.data.bones:
        print(
            f"- {bone.name}"
            f" | parent={bone.parent.name if bone.parent else None}"
        )

print()
print("=== SIGNMUSIC AVATAR INSPECTION COMPLETE ===")