import bpy

print("=== SIGNMUSIC BLENDER TEST ===")
print(f"Blender version: {bpy.app.version_string}")

# Limpiar la escena
bpy.ops.object.select_all(action="SELECT")
bpy.ops.object.delete(use_global=False)

# Crear un cubo de prueba
bpy.ops.mesh.primitive_cube_add(
    location=(0, 0, 0)
)

cube = bpy.context.active_object
cube.name = "Signmusic_Test_Avatar"

print(f"Created object: {cube.name}")
print("=== SIGNMUSIC TEST COMPLETE ===")