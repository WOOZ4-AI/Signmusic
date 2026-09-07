from typing import Any, Dict, List


class ArmTrajectoryCompiler:
    """
    Compilador de trayectorias espaciales de Signmusic.

    Convierte:

        movimiento conceptual
                ↓
        puntos espaciales
                ↓
        puntos temporales

    Esta clase NO depende de Blender.

    Flujo:

        MovementCompiler
                ↓
        ArmTrajectoryCompiler
                ↓
        trayectoria temporal
                ↓
        ArmMotionSolver
                ↓
        brazo / antebrazo
    """

    MIN_POINT_COUNT = 1

    # =========================================================
    # COMPILAR TRAYECTORIA
    # =========================================================

    def compile_trajectory(
        self,
        movement: Dict[str, Any],
        total_duration: float,
    ) -> Dict[str, Any]:
        """
        Convierte un movimiento conceptual en una trayectoria
        temporal.

        Entrada:

            {
                "path": "pull_up",
                "duration": 0.8,
                "points": [
                    {
                        "position": [...]
                    },
                    ...
                ]
            }

        Salida:

            {
                "path": "pull_up",
                "duration": 0.8,
                "points": [
                    {
                        "time": 0.0,
                        "normalized_time": 0.0,
                        "position": [...]
                    },
                    ...
                ]
            }
        """

        if not isinstance(
            movement,
            dict,
        ):
            raise TypeError(
                "movement debe ser un diccionario."
            )

        total_duration = float(
            total_duration
        )

        if total_duration <= 0:
            raise ValueError(
                "total_duration debe ser mayor que 0."
            )

        # -----------------------------------------------------
        # PATH
        # -----------------------------------------------------

        path = movement.get(
            "path",
            "none",
        )

        path = str(
            path
        ).strip().lower()

        # -----------------------------------------------------
        # PUNTOS
        # -----------------------------------------------------

        points = movement.get(
            "points",
            [],
        )

        if not isinstance(
            points,
            list,
        ):
            raise TypeError(
                "movement['points'] debe ser una lista."
            )

        if len(points) < self.MIN_POINT_COUNT:
            raise ValueError(
                "La trayectoria debe contener al menos "
                "un punto."
            )

        # -----------------------------------------------------
        # DURACIÓN DEL MOVIMIENTO
        # -----------------------------------------------------

        movement_duration = float(
            movement.get(
                "duration",
                total_duration,
            )
        )

        if movement_duration <= 0:
            raise ValueError(
                "La duración del movimiento "
                "debe ser mayor que 0."
            )

        # -----------------------------------------------------
        # NO PERMITIR QUE EXCEDA EL SIGNO
        # -----------------------------------------------------

        effective_duration = min(
            movement_duration,
            total_duration,
        )

        # =====================================================
        # CREAR PUNTOS TEMPORALES
        # =====================================================

        compiled_points = []

        if len(points) == 1:

            position = (
                self._validate_position(
                    points[0]
                )
            )

            compiled_points.append(
                {
                    "time": 0.0,
                    "normalized_time": 0.0,
                    "position": position,
                }
            )

        else:

            last_index = (
                len(points) - 1
            )

            for index, point in enumerate(
                points
            ):

                position = (
                    self._validate_position(
                        point
                    )
                )

                normalized_time = (
                    index
                    / last_index
                )

                time = (
                    normalized_time
                    * effective_duration
                )

                compiled_points.append(
                    {
                        "time": float(
                            time
                        ),
                        "normalized_time": float(
                            normalized_time
                        ),
                        "position": position,
                    }
                )

        trajectory = {
            "path": path,
            "duration": float(
                effective_duration
            ),
            "points": compiled_points,
        }

        errors = (
            self.validate_trajectory(
                trajectory
            )
        )

        if errors:
            raise ValueError(
                "Trayectoria inválida: "
                + "; ".join(errors)
            )

        return trajectory

    # =========================================================
    # VALIDAR POSICIÓN
    # =========================================================

    @staticmethod
    def _validate_position(
        point: Dict[str, Any],
    ) -> List[float]:
        """
        Valida y normaliza una posición.
        """

        if not isinstance(
            point,
            dict,
        ):
            raise TypeError(
                "Cada punto de trayectoria "
                "debe ser un diccionario."
            )

        position = point.get(
            "position"
        )

        if not isinstance(
            position,
            (list, tuple),
        ):
            raise TypeError(
                "Cada punto debe contener "
                "'position' como lista."
            )

        if len(position) != 3:
            raise ValueError(
                "'position' debe tener exactamente "
                "3 valores."
            )

        return [
            float(position[0]),
            float(position[1]),
            float(position[2]),
        ]

    # =========================================================
    # INTERPOLAR POSICIÓN
    # =========================================================

    @staticmethod
    def interpolate_position(
        start: List[float],
        end: List[float],
        factor: float,
    ) -> List[float]:
        """
        Interpolación lineal entre dos posiciones.

        factor:

            0.0 → inicio
            1.0 → final
        """

        if len(start) != 3:
            raise ValueError(
                "start debe tener 3 valores."
            )

        if len(end) != 3:
            raise ValueError(
                "end debe tener 3 valores."
            )

        factor = max(
            0.0,
            min(
                1.0,
                float(factor),
            ),
        )

        return [
            float(
                start[0]
                + (
                    end[0]
                    - start[0]
                )
                * factor
            ),
            float(
                start[1]
                + (
                    end[1]
                    - start[1]
                )
                * factor
            ),
            float(
                start[2]
                + (
                    end[2]
                    - start[2]
                )
                * factor
            ),
        ]

    # =========================================================
    # OBTENER POSICIÓN EN UN MOMENTO
    # =========================================================

    def evaluate_at_time(
        self,
        trajectory: Dict[str, Any],
        time: float,
    ) -> List[float]:
        """
        Evalúa la trayectoria en un instante.

        Si está entre dos puntos se interpola.
        """

        points = trajectory.get(
            "points",
            [],
        )

        if not points:
            raise ValueError(
                "La trayectoria no contiene puntos."
            )

        time = float(
            time
        )

        # -----------------------------------------------------
        # ANTES DEL INICIO
        # -----------------------------------------------------

        if time <= float(
            points[0]["time"]
        ):

            return list(
                points[0]["position"]
            )

        # -----------------------------------------------------
        # DESPUÉS DEL FINAL
        # -----------------------------------------------------

        if time >= float(
            points[-1]["time"]
        ):

            return list(
                points[-1]["position"]
            )

        # -----------------------------------------------------
        # INTERVALO
        # -----------------------------------------------------

        for index in range(
            len(points) - 1
        ):

            current = points[
                index
            ]

            next_point = points[
                index + 1
            ]

            current_time = float(
                current["time"]
            )

            next_time = float(
                next_point["time"]
            )

            if (
                current_time
                <= time
                <= next_time
            ):

                interval = (
                    next_time
                    - current_time
                )

                if interval <= 0:

                    return list(
                        current["position"]
                    )

                factor = (
                    time
                    - current_time
                ) / interval

                return self.interpolate_position(
                    current["position"],
                    next_point["position"],
                    factor,
                )

        return list(
            points[-1]["position"]
        )

    # =========================================================
    # FACTOR TEMPORAL
    # =========================================================

    @staticmethod
    def get_motion_factor(
        trajectory: Dict[str, Any],
        time: float,
    ) -> float:
        """
        Devuelve el progreso del movimiento:

            0.0 → comienzo
            1.0 → final

        Después de terminar el movimiento, permanece en 1.0.
        """

        duration = float(
            trajectory.get(
                "duration",
                0.0,
            )
        )

        if duration <= 0:
            return 1.0

        time = float(
            time
        )

        return max(
            0.0,
            min(
                1.0,
                time / duration,
            ),
        )

    # =========================================================
    # PUNTOS TEMPORALES
    # =========================================================

    def get_timed_points(
        self,
        trajectory: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Devuelve los puntos temporales compilados.
        """

        points = trajectory.get(
            "points",
            [],
        )

        return [
            dict(point)
            for point
            in points
        ]

    # =========================================================
    # OBTENER DURACIÓN
    # =========================================================

    @staticmethod
    def get_duration(
        trajectory: Dict[str, Any],
    ) -> float:

        return float(
            trajectory.get(
                "duration",
                0.0,
            )
        )

    # =========================================================
    # VALIDAR TRAYECTORIA
    # =========================================================

    def validate_trajectory(
        self,
        trajectory: Dict[str, Any],
    ) -> List[str]:
        """
        Valida una trayectoria compilada.
        """

        errors = []

        if not isinstance(
            trajectory,
            dict,
        ):

            return [
                "trajectory debe ser un diccionario."
            ]

        if "path" not in trajectory:

            errors.append(
                "Falta 'path'."
            )

        if "duration" not in trajectory:

            errors.append(
                "Falta 'duration'."
            )

        if "points" not in trajectory:

            errors.append(
                "Falta 'points'."
            )

            return errors

        try:

            duration = float(
                trajectory[
                    "duration"
                ]
            )

            if duration < 0:

                errors.append(
                    "'duration' no puede ser negativa."
                )

        except (
            TypeError,
            ValueError,
        ):

            errors.append(
                "'duration' inválida."
            )

        points = trajectory[
            "points"
        ]

        if not isinstance(
            points,
            list,
        ):

            errors.append(
                "'points' debe ser una lista."
            )

            return errors

        if not points:

            errors.append(
                "La trayectoria no puede estar vacía."
            )

            return errors

        previous_time = -1.0

        for index, point in enumerate(
            points
        ):

            if not isinstance(
                point,
                dict,
            ):

                errors.append(
                    f"Punto {index} inválido."
                )

                continue

            if "time" not in point:

                errors.append(
                    f"Punto {index}: "
                    "falta 'time'."
                )

            if "position" not in point:

                errors.append(
                    f"Punto {index}: "
                    "falta 'position'."
                )

                continue

            try:

                current_time = float(
                    point["time"]
                )

            except (
                TypeError,
                ValueError,
            ):

                errors.append(
                    f"Punto {index}: "
                    "time inválido."
                )

                continue

            if current_time < 0:

                errors.append(
                    f"Punto {index}: "
                    "time negativo."
                )

            if current_time < previous_time:

                errors.append(
                    f"Punto {index}: "
                    "los tiempos no están ordenados."
                )

            previous_time = current_time

            if duration >= 0 and current_time > duration:

                errors.append(
                    f"Punto {index}: "
                    "time excede la duración."
                )

            try:

                position = point[
                    "position"
                ]

                if not isinstance(
                    position,
                    (list, tuple),
                ):

                    errors.append(
                        f"Punto {index}: "
                        "position inválida."
                    )

                elif len(position) != 3:

                    errors.append(
                        f"Punto {index}: "
                        "position debe tener 3 valores."
                    )

            except (
                TypeError,
                ValueError,
            ):

                errors.append(
                    f"Punto {index}: "
                    "position inválida."
                )

        return errors


# =============================================================
# PRUEBA
# =============================================================

if __name__ == "__main__":

    compiler = (
        ArmTrajectoryCompiler()
    )

    print(
        "=== SIGNMUSIC ARM TRAJECTORY COMPILER ==="
    )

    movement = {
        "path": "pull_up",
        "duration": 0.8,
        "points": [
            {
                "position": [
                    0.0,
                    0.0,
                    0.0,
                ]
            },
            {
                "position": [
                    0.0,
                    0.35,
                    0.0,
                ]
            },
            {
                "position": [
                    0.0,
                    0.75,
                    0.0,
                ]
            },
            {
                "position": [
                    0.0,
                    1.0,
                    0.0,
                ]
            },
        ],
    }

    trajectory = (
        compiler.compile_trajectory(
            movement,
            total_duration=0.8,
        )
    )

    print()
    print(
        "Trayectoria:"
    )

    for point in trajectory[
        "points"
    ]:

        print(
            point
        )

    print()
    print(
        "Validation:"
    )

    print(
        compiler.validate_trajectory(
            trajectory
        )
        or "OK"
    )

    print()
    print(
        "Motion factors:"
    )

    for time in (
        0.0,
        0.2,
        0.4,
        0.6,
        0.8,
        1.0,
    ):

        factor = (
            compiler.get_motion_factor(
                trajectory,
                time,
            )
        )

        position = (
            compiler.evaluate_at_time(
                trajectory,
                time,
            )
        )

        print(
            f"Time {time:.2f}s → "
            f"factor={factor:.3f} "
            f"position={position}"
        )

    print()
    print(
        "Status: OK"
    )