import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.keyframe_generator import KeyframeGenerator

def main():
    print("🎬 SIGNMUSIC - Keyframe Generator Test\n")
    
    generator = KeyframeGenerator()
    
    # Conceptos de la canción "Save Me, Save You"
    concepts = ["SAVE", "ME", "SAVE", "YOU"]
    
    print(f"📝 Conceptos: {concepts}\n")
    
    # Generar secuencia
    sequence = generator.generate_animation_sequence(concepts, bpm=120)
    
    print(f"⏱️  Duración total: {sequence['total_duration']:.2f} segundos")
    print(f"🎬 Animaciones: {len(sequence['animations'])}\n")
    
    for anim in sequence['animations']:
        print(f"  {anim['concept']}: {anim['start_time']:.2f}s → {anim['end_time']:.2f}s ({anim['duration']:.2f}s)")
    
    # Guardar JSON
    output = "data/animations/save_me_save_you_animation.json"
    Path(output).parent.mkdir(parents=True, exist_ok=True)
    generator.save_animation_to_json(sequence, output)
    
    print(f"\n✅ Test completado!")

if __name__ == "__main__":
    main()