import subprocess
from pathlib import Path

# Rutas
fbx_file = Path("models/avatar/character.fbx").resolve()
glb_file = Path("models/avatar/character.glb").resolve()

# Blender executable
blender_exe = r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe"

print(f"📦 Convirtiendo {fbx_file.name} a GLB...")
print(f"   Entrada: {fbx_file}")
print(f"   Salida: {glb_file}")

if not fbx_file.exists():
    print(f"❌ Error: {fbx_file} no existe")
    exit(1)

# Script de Blender
blender_script = f"""
import bpy
bpy.ops.import_scene.fbx(filepath=r'{fbx_file}')
bpy.ops.export_scene.gltf(filepath=r'{glb_file}', export_format='GLB')
"""

# Crear archivo temporal
temp_script = Path("temp_blend_script.py")
temp_script.write_text(blender_script)

print("⏳ Ejecutando Blender (esto tarda un poco)...")

# Ejecutar Blender
result = subprocess.run(
    [blender_exe, "--background", "--python", str(temp_script)],
    capture_output=True,
    text=True
)

print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)

# Limpiar
temp_script.unlink()

# Verificar resultado
if glb_file.exists():
    print(f"✅ GLB creado exitosamente: {glb_file}")
else:
    print(f"❌ Error: El archivo GLB no se creó")
    print(f"Return code: {result.returncode}")