import json
from pathlib import Path

# Instalamos la librería para leer GLB
# pip install trimesh

try:
    import trimesh
except ImportError:
    print("⚠️ Instalando trimesh...")
    import subprocess
    subprocess.check_call(["pip", "install", "trimesh"])
    import trimesh

def inspect_glb(glb_path):
    """
    Inspecciona la estructura de un archivo GLB
    """
    glb_path = Path(glb_path)
    
    if not glb_path.exists():
        print(f"❌ Error: {glb_path} no existe")
        return
    
    print(f"📦 Inspeccionando: {glb_path}\n")
    
    # Cargar el modelo
    mesh = trimesh.load(glb_path)
    
    # Extraer información
    print("=" * 60)
    print("INFORMACIÓN DEL MODELO")
    print("=" * 60)
    
    if hasattr(mesh, 'geometry'):
        print(f"\n🔷 Geometría:")
        for name, geom in mesh.geometry.items():
            print(f"   - {name}: {geom}")
    
    if hasattr(mesh, 'graph'):
        print(f"\n🦴 Nodos de la jerarquía:")
        for node_name in mesh.graph.nodes:
            print(f"   - {node_name}")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    inspect_glb("models/avatar/character.glb")