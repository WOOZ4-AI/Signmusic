import sys
from pathlib import Path

# Añade el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.song_loader import SongLoader
from backend.semantic_analyzer import SemanticAnalyzer
from backend.sign_generator import SignGenerator

def main():
    print("🎵 SIGNMUSIC - Song Processor\n")
    
    # Carga la canción
    loader = SongLoader()
    song = loader.load_song("save_me_save_you")
    
    print(f"📝 Canción: {song['metadata']['title']}")
    print(f"🎤 Artista: {song['metadata']['artist']}")
    print(f"📊 Estado: {song['metadata']['status']}\n")
    
    # Inicializa analizadores
    analyzer = SemanticAnalyzer()
    generator = SignGenerator()
    
    # Línea de prueba (después añadiremos la letra completa)
    test_line = "Save me, save you"
    
    print(f"🔍 Analizando: '{test_line}'\n")
    
    # Análisis semántico
    line_analysis = analyzer.analyze_line(test_line)
    print(f"📌 Tokens: {line_analysis['tokens']}")
    print(f"💡 Conceptos: {line_analysis['concepts']}\n")
    
    # Generación de signos
    concepts = list(line_analysis['concepts'].keys())
    signs = generator.generate_sequence(concepts)
    
    print(f"🤟 Signos DGS generados:")
    for sign in signs:
        print(f"  - {sign['concept']}: {sign['sign'] if sign['sign'] else 'NO MAPEADO'}")
    
    print(f"\n✅ Procesamiento completado")

if __name__ == "__main__":
    main()
    