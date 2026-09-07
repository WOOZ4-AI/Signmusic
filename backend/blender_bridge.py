from pathlib import Path
import subprocess
from typing import Optional


class BlenderBridge:
    """
    Puente entre Signmusic y Blender.

    Se encarga de ejecutar Blender desde Python.
    La generación y manipulación del avatar se añadirá
    posteriormente.
    """

    def __init__(
        self,
        blender_executable: str = "blender"
    ):
        self.blender_executable = blender_executable

    def get_version(self) -> str:
        """
        Obtiene la versión instalada de Blender.
        """

        result = subprocess.run(
            [
                self.blender_executable,
                "--version"
            ],
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout.strip()

    def run_script(
        self,
        script_path: str,
        blend_file: Optional[str] = None
    ) -> str:
        """
        Ejecuta un script Python dentro de Blender.

        Si se proporciona un archivo .blend,
        Blender lo abrirá antes de ejecutar el script.
        """

        path = Path(script_path)

        if not path.exists():
            raise FileNotFoundError(
                f"No existe el script de Blender: {path}"
            )

        command = [
            self.blender_executable,
            "--background",
        ]

        if blend_file:
            blend_path = Path(blend_file)

            if not blend_path.exists():
                raise FileNotFoundError(
                    f"No existe el archivo .blend: {blend_path}"
                )

            command.extend([
                str(blend_path)
            ])

        command.extend([
            "--python",
            str(path)
        ])

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True
        )

        return result.stdout