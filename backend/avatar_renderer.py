from typing import Dict, Any


class AvatarRenderer:
    """
    Prepara el estado del avatar para un motor de renderizado 3D.

    Esta clase no renderiza gráficos todavía.
    Su responsabilidad actual es convertir el estado calculado
    por AvatarPlayer en una estructura limpia y consistente
    que posteriormente podrá consumir un motor 3D.
    """

    def __init__(self):
        self.last_state = None

    # ---------------------------------------------------------
    # Estado del avatar
    # ---------------------------------------------------------

    def render_state(
        self,
        state: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Prepara un estado del avatar para renderizado.

        Args:
            state:
                Estado generado por AvatarPlayer.get_avatar_state().

        Returns:
            Estado preparado para el motor 3D.
        """

        if not isinstance(state, dict):
            raise TypeError("El estado del avatar debe ser un diccionario")

        bones = state.get("bones", {})

        rendered_bones = {}

        for bone_name, transform in bones.items():

            rotation = transform.get(
                "rotation",
                [0.0, 0.0, 0.0]
            )

            position = transform.get(
                "position",
                [0.0, 0.0, 0.0]
            )

            rendered_bones[bone_name] = {
                "rotation": [
                    float(value)
                    for value in rotation
                ],
                "position": [
                    float(value)
                    for value in position
                ],
            }

        rendered_state = {
            "concept": state.get("concept"),
            "global_time": float(
                state.get("global_time", 0.0)
            ),
            "start_time": state.get("start_time"),
            "end_time": state.get("end_time"),
            "bones": rendered_bones,
        }

        self.last_state = rendered_state

        return rendered_state

    # ---------------------------------------------------------
    # Información del modelo
    # ---------------------------------------------------------

    @staticmethod
    def get_model_requirements() -> Dict[str, Any]:
        """
        Describe los requisitos que deberá cumplir el futuro
        modelo 3D del avatar.
        """

        return {
            "skeleton": "Mixamo-compatible",
            "required_bones": [
                "mixamorig7:Head",
                "mixamorig7:LeftArm",
                "mixamorig7:LeftForeArm",
                "mixamorig7:LeftHand",
                "mixamorig7:RightArm",
                "mixamorig7:RightForeArm",
                "mixamorig7:RightHand",
                "mixamorig7:Spine",
            ],
            "rotation_unit": "degrees",
            "position_unit": "relative",
        }

    # ---------------------------------------------------------
    # Último estado
    # ---------------------------------------------------------

    def get_last_state(self):
        """
        Devuelve el último estado preparado para renderizado.
        """

        return self.last_state