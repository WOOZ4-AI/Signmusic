import json
from pathlib import Path

class SongLoader:
    """Carga metadatos y estructura de canciones desde JSON"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.metadata_dir = self.data_dir / "metadata"
    
    def load_song(self, song_id: str) -> dict:
        """
        Carga metadata y estructura de una canción
        
        Args:
            song_id: ID único de la canción (ej: "save_me_save_you")
        
        Returns:
            dict con metadata y estructura
        """
        metadata_path = self.metadata_dir / f"song_{song_id}.json"
        structure_path = self.metadata_dir / f"song_{song_id}_structure.json"
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"No existe: {metadata_path}")
        
        with open(metadata_path, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        with open(structure_path, 'r', encoding='utf-8') as f:
            structure = json.load(f)
        
        return {
            "metadata": metadata,
            "structure": structure
        }
    
    def save_song_structure(self, song_id: str, structure: dict) -> None:
        """Guarda la estructura actualizada de una canción"""
        structure_path = self.metadata_dir / f"song_{song_id}_structure.json"
        
        with open(structure_path, 'w', encoding='utf-8') as f:
            json.dump(structure, f, indent=2, ensure_ascii=False)