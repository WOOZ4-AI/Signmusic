from typing import Any, Dict, List


class ArmMotionSolver:
    """
    Convierte movimientos semánticos de Signmusic
    en rotaciones del brazo derecho del rig Mixamo.

    Calibración visual real del avatar:

        RightArm X +20°  → brazo baja
        RightArm X -20°  → brazo sube

        RightArm Z +20°  → brazo va hacia atrás
        RightArm Z -20°  → brazo vuelve hacia el centro

        RightForeArm X +30° → antebrazo baja/se dobla

    Por tanto:

        movimiento vertical
            → RightArm X

        movimiento de profundidad
            → RightArm Z

    Esta clase no depende de Blender.
    """

    # =========================================================
    # LIMITES
    # =========================================================

    ARM_X_LIMIT = 65.0
    ARM_Z_LIMIT = 65.0

    FOREARM_X_LIMIT = 75.0
    FOREARM_Z_LIMIT = 75.0

    # =========================================================
    # PERFILES DE MOVIMIENTO
    # =========================================================

    MOVEMENT_PROFILES = {

        # -----------------------------------------------------
        # NEUTRAL
        # -----------------------------------------------------

        "none": {
            "arm_x": 0.0,
            "arm_z": 0.0,
            "forearm_x": 0.0,
            "forearm_z": 0.0,
        },

        # -----------------------------------------------------
        # SUBIR
        # -----------------------------------------------------
        #
        # RightArm X negativo = subir
        # -----------------------------------------------------

        "up": {
            "arm_x": -25.0,
            "arm_z": 0.0,
            "forearm_x": -10.0,
            "forearm_z": 0.0,
        },

        # -----------------------------------------------------
        # BAJAR
        # -----------------------------------------------------

        "down": {
            "arm_x": 25.0,
            "arm_z": 0.0,
            "forearm_x": 10.0,
            "forearm_z": 0.0,
        },

        # -----------------------------------------------------
        # PULL UP
        # -----------------------------------------------------
        #
        # SAVE:
        # levantar progresivamente la mano.
        # -----------------------------------------------------

        "pull_up": {
            "arm_x": -28.0,
            "arm_z": 0.0,
            "forearm_x": -12.0,
            "forearm_z": 0.0,
        },

        # -----------------------------------------------------
        # FORWARD
        # -----------------------------------------------------
        #
        # Z negativo mueve el brazo hacia el centro/adelante
        # respecto a la calibración observada.
        #
        # La magnitud es moderada para evitar una extensión
        # exagerada.
        # -----------------------------------------------------

        "forward": {
            "arm_x": 0.0,
            "arm_z": -25.0,
            "forearm_x": 0.0,
            "forearm_z": -10.0,
        },

        # -----------------------------------------------------
        # BACKWARD
        # -----------------------------------------------------

        "backward": {
            "arm_x": 0.0,
            "arm_z": 25.0,
            "forearm_x": 0.0,
            "forearm_z": 10.0,
        },

        # -----------------------------------------------------
        # POINT FORWARD
        # -----------------------------------------------------

        "point_forward": {
            "arm_x": 0.0,
            "arm_z": -30.0,
            "forearm_x": 0.0,
            "forearm_z": -15.0,
        },

        # -----------------------------------------------------
        # POINT TO SELF
        # -----------------------------------------------------
        #
        # Movimiento inverso hacia el cuerpo.
        # -----------------------------------------------------

        "point_to_self": {
            "arm_x": 0.0,
            "arm_z": 22.0,
            "forearm_x": 0.0,
            "forearm_z": 12.0,
        },

        # -----------------------------------------------------
        # FRONT TO CENTER
        # -----------------------------------------------------

        "front_to_center": {
            "arm_x": 0.0,
            "arm_z": 22.0,
            "forearm_x": 0.0,
            "forearm_z": 12.0,
        },

        # -----------------------------------------------------
        # CENTER TO UPPER
        # -----------------------------------------------------

        "center_to_upper": {
            "arm_x": -25.0,
            "arm_z": 0.0,
            "forearm_x": -10.0,
            "forearm_z": 0.0,
        },

        # -----------------------------------------------------
        # LEFT
        # -----------------------------------------------------

        "left": {
            "arm_x": 0.0,
            "arm_z": -12.0,
            "forearm_x": 0.0,
            "forearm_z": -5.0,
        },

        # -----------------------------------------------------
        # RIGHT
        # -----------------------------------------------------

        "right": {
            "arm_x": 0.0,
            "arm_z": 12.0,
            "forearm_x": 0.0,
            "forearm_z": 5.0,
        },
    }

    # =========================================================
    # ALIAS
    # =========================================================

    ALIASES = {
        "neutral": "none",
        "static": "none",

        "up": "up",
        "upward": "up",

        "down": "down",
        "downward": "down",

        "pull_up": "pull_up",
        "pullup": "pull_up",

        "forward": "forward",
        "front": "forward",

        "backward": "backward",
        "back": "backward",

        "point_forward": "point_forward",
        "point_to_other": "point_forward",
        "point_other": "point_forward",

        "point_to_self": "point_to_self",
        "point_self": "point_to_self",

        "front_to_center": "front_to_center",
        "center_to_upper": "center_to_upper",

        "left": "left",
        "right": "right",
    }

    # =========================================================
    # NORMALIZAR PATH
    # =========================================================

    @classmethod
    def _normalize_path(
        cls,
        path: str,
    ) -> str:

        normalized = str(
            path
        ).strip().lower()

        return cls.ALIASES.get(
            normalized,
            normalized,
        )

    # =========================================================
    # OBTENER PERFIL
    # =========================================================

    @classmethod
    def get_profile(
        cls,
        path: str,
    ) -> Dict[str, float]:

        normalized = (
            cls._normalize_path(
                path
            )
        )

        profile = cls.MOVEMENT_PROFILES.get(
            normalized
        )

        if profile is None:

            profile = cls.MOVEMENT_PROFILES[
                "none"
            ]

        return dict(
            profile
        )

    # =========================================================
    # LIMITAR
    # =========================================================

    @staticmethod
    def _clamp(
        value: float,
        minimum: float,
        maximum: float,
    ) -> float:

        return max(
            minimum,
            min(
                maximum,
                float(value),
            ),
        )

    # =========================================================
    # RESOLVER MOVIMIENTO
    # =========================================================

    def solve_movement(
        self,
        path: str,
        factor: float,
    ) -> Dict[str, Dict[str, Any]]:
        """
        Convierte un movimiento semántico en rotaciones.

        factor:

            0.0 → neutral
            1.0 → posición final
        """

        factor = max(
            0.0,
            min(
                1.0,
                float(factor),
            ),
        )

        profile = self.get_profile(
            path
        )

        arm_x = (
            profile["arm_x"]
            * factor
        )

        arm_z = (
            profile["arm_z"]
            * factor
        )

        forearm_x = (
            profile["forearm_x"]
            * factor
        )

        forearm_z = (
            profile["forearm_z"]
            * factor
        )

        arm_x = self._clamp(
            arm_x,
            -self.ARM_X_LIMIT,
            self.ARM_X_LIMIT,
        )

        arm_z = self._clamp(
            arm_z,
            -self.ARM_Z_LIMIT,
            self.ARM_Z_LIMIT,
        )

        forearm_x = self._clamp(
            forearm_x,
            -self.FOREARM_X_LIMIT,
            self.FOREARM_X_LIMIT,
        )

        forearm_z = self._clamp(
            forearm_z,
            -self.FOREARM_Z_LIMIT,
            self.FOREARM_Z_LIMIT,
        )

        return {
            "right_arm": {
                "rotation": [
                    float(arm_x),
                    0.0,
                    float(arm_z),
                ]
            },

            "right_forearm": {
                "rotation": [
                    float(forearm_x),
                    0.0,
                    float(forearm_z),
                ]
            },
        }

    # =========================================================
    # COMPATIBILIDAD POSITION
    # =========================================================

    def solve_position(
        self,
        position: List[float],
    ) -> Dict[str, Dict[str, Any]]:
        """
        Compatibilidad con la API anterior.

        La interpretación principal del sistema actual
        es semántica mediante solve_movement().
        """

        if not isinstance(
            position,
            (list, tuple),
        ):
            raise TypeError(
                "position debe ser una lista o tupla."
            )

        if len(position) != 3:
            raise ValueError(
                "position debe contener exactamente "
                "3 valores."
            )

        x = float(
            position[0]
        )

        y = float(
            position[1]
        )

        z = float(
            position[2]
        )

        # -----------------------------------------------------
        # Vertical:
        #
        # Y positivo = subir
        # RightArm X negativo = subir
        # -----------------------------------------------------

        arm_x = (
            -25.0
            * max(
                -1.0,
                min(
                    1.0,
                    y,
                ),
            )
        )

        forearm_x = (
            -10.0
            * max(
                -1.0,
                min(
                    1.0,
                    y,
                ),
            )
        )

        # -----------------------------------------------------
        # Profundidad:
        #
        # Z negativo = forward
        # Z positivo = backward
        # -----------------------------------------------------

        arm_z = (
            25.0
            * max(
                -1.0,
                min(
                    1.0,
                    z,
                ),
            )
        )

        forearm_z = (
            10.0
            * max(
                -1.0,
                min(
                    1.0,
                    z,
                ),
            )
        )

        # -----------------------------------------------------
        # X espacial:
        #
        # Movimiento lateral suave.
        # -----------------------------------------------------

        arm_z += (
            -12.0
            * max(
                -1.0,
                min(
                    1.0,
                    x,
                ),
            )
        )

        forearm_z += (
            -5.0
            * max(
                -1.0,
                min(
                    1.0,
                    x,
                ),
            )
        )

        return {
            "right_arm": {
                "rotation": [
                    float(
                        self._clamp(
                            arm_x,
                            -self.ARM_X_LIMIT,
                            self.ARM_X_LIMIT,
                        )
                    ),
                    0.0,
                    float(
                        self._clamp(
                            arm_z,
                            -self.ARM_Z_LIMIT,
                            self.ARM_Z_LIMIT,
                        )
                    ),
                ]
            },

            "right_forearm": {
                "rotation": [
                    float(
                        self._clamp(
                            forearm_x,
                            -self.FOREARM_X_LIMIT,
                            self.FOREARM_X_LIMIT,
                        )
                    ),
                    0.0,
                    float(
                        self._clamp(
                            forearm_z,
                            -self.FOREARM_Z_LIMIT,
                            self.FOREARM_Z_LIMIT,
                        )
                    ),
                ]
            },
        }

    # =========================================================
    # RESOLVER TRAYECTORIA
    # =========================================================

    def solve_trajectory(
        self,
        trajectory: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Convierte una trayectoria temporal en keyframes.
        """

        if not isinstance(
            trajectory,
            dict,
        ):
            raise TypeError(
                "trajectory debe ser un diccionario."
            )

        points = trajectory.get(
            "points",
            [],
        )

        if not isinstance(
            points,
            list,
        ):
            raise TypeError(
                "trajectory['points'] debe ser una lista."
            )

        path = self._normalize_path(
            trajectory.get(
                "path",
                "none",
            )
        )

        result = []

        for index, point in enumerate(
            points
        ):

            if not isinstance(
                point,
                dict,
            ):
                raise TypeError(
                    "Cada punto debe ser un diccionario."
                )

            normalized_time = float(
                point.get(
                    "normalized_time",
                    (
                        index
                        / max(
                            1,
                            len(points) - 1,
                        )
                    ),
                )
            )

            normalized_time = max(
                0.0,
                min(
                    1.0,
                    normalized_time,
                ),
            )

            bones = (
                self.solve_movement(
                    path,
                    normalized_time,
                )
            )

            result.append(
                {
                    "time": float(
                        point.get(
                            "time",
                            0.0,
                        )
                    ),
                    "normalized_time": (
                        normalized_time
                    ),
                    "position": list(
                        point.get(
                            "position",
                            [
                                0.0,
                                0.0,
                                0.0,
                            ],
                        )
                    ),
                    "bones": bones,
                }
            )

        return result

    # =========================================================
    # VALIDACIÓN
    # =========================================================

    @classmethod
    def validate_result(
        cls,
        result: List[Dict[str, Any]],
    ) -> List[str]:

        errors = []

        if not isinstance(
            result,
            list,
        ):

            return [
                "result debe ser una lista."
            ]

        previous_time = -1.0

        for index, item in enumerate(
            result
        ):

            if not isinstance(
                item,
                dict,
            ):

                errors.append(
                    f"Keyframe {index} inválido."
                )

                continue

            if "time" not in item:

                errors.append(
                    f"Keyframe {index}: "
                    "falta time."
                )

            if "bones" not in item:

                errors.append(
                    f"Keyframe {index}: "
                    "falta bones."
                )

                continue

            try:

                current_time = float(
                    item["time"]
                )

            except (
                TypeError,
                ValueError,
            ):

                errors.append(
                    f"Keyframe {index}: "
                    "time inválido."
                )

                continue

            if current_time < previous_time:

                errors.append(
                    f"Keyframe {index}: "
                    "tiempo fuera de orden."
                )

            previous_time = current_time

            bones = item["bones"]

            if not isinstance(
                bones,
                dict,
            ):

                errors.append(
                    f"Keyframe {index}: "
                    "bones inválido."
                )

                continue

            for required_bone in (
                "right_arm",
                "right_forearm",
            ):

                if required_bone not in bones:

                    errors.append(
                        f"Keyframe {index}: "
                        f"falta {required_bone}."
                    )

        return errors


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    solver = ArmMotionSolver()

    print(
        "=== SIGNMUSIC CALIBRATED ARM MOTION SOLVER ==="
    )

    movements = (
        "up",
        "down",
        "pull_up",
        "forward",
        "backward",
        "point_forward",
        "point_to_self",
    )

    for movement in movements:

        print()
        print(
            movement + ":"
        )

        for factor in (
            0.0,
            0.5,
            1.0,
        ):

            result = (
                solver.solve_movement(
                    movement,
                    factor,
                )
            )

            print(
                f"  factor={factor:.1f} "
                f"→ "
                f"RightArm="
                f"{result['right_arm']['rotation']} "
                f"RightForeArm="
                f"{result['right_forearm']['rotation']}"
            )

    # ---------------------------------------------------------
    # PULL UP
    # ---------------------------------------------------------

    trajectory = {
        "path": "pull_up",
        "duration": 0.8,
        "points": [
            {
                "time": 0.0,
                "normalized_time": 0.0,
                "position": [
                    0.0,
                    0.0,
                    0.0,
                ],
            },
            {
                "time": 0.2667,
                "normalized_time": 0.3333,
                "position": [
                    0.0,
                    0.35,
                    0.0,
                ],
            },
            {
                "time": 0.5333,
                "normalized_time": 0.6667,
                "position": [
                    0.0,
                    0.75,
                    0.0,
                ],
            },
            {
                "time": 0.8,
                "normalized_time": 1.0,
                "position": [
                    0.0,
                    1.0,
                    0.0,
                ],
            },
        ],
    }

    print()
    print(
        "=== PULL UP TRAJECTORY ==="
    )

    solved = (
        solver.solve_trajectory(
            trajectory
        )
    )

    for item in solved:

        print(
            item
        )

    print()
    print(
        "Validation:"
    )

    print(
        solver.validate_result(
            solved
        )
        or "OK"
    )

    print()
    print(
        "Status: OK"
    )