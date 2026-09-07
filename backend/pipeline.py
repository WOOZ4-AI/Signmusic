from typing import Dict, Any

from song_processor import SongProcessor
from sign_dictionary import SignDictionary
from sign_generator import SignGenerator
from sign_to_motion_compiler import SignToMotionCompiler
from motion_generator import MotionGenerator
from motion_compiler import MotionCompiler
from blender_renderer import BlenderRenderer


class SignMusicPipeline:
    """
    Pipeline principal de Signmusic.

    Flujo:

        canción
          ↓
        SongProcessor
          ↓
        conceptos
          ↓
        SignGenerator
          ↓
        SignToMotionCompiler
          ↓
        MotionGenerator
          ↓
        MotionCompiler
          ↓
        BlenderRenderer
    """

    def __init__(
        self,
        song_processor=None,
        sign_dictionary=None,
        sign_generator=None,
        sign_to_motion_compiler=None,
        motion_generator=None,
        motion_compiler=None,
        blender_renderer=None,
    ):

        self.song_processor = (
            song_processor
            or SongProcessor()
        )

        self.sign_dictionary = (
            sign_dictionary
            or SignDictionary()
        )

        self.sign_generator = (
            sign_generator
            or SignGenerator()
        )

        self.sign_to_motion_compiler = (
            sign_to_motion_compiler
            or SignToMotionCompiler()
        )

        self.motion_generator = (
            motion_generator
            or MotionGenerator()
        )

        self.motion_compiler = (
            motion_compiler
            or MotionCompiler()
        )

        self.blender_renderer = (
            blender_renderer
            or BlenderRenderer()
        )

    # =========================================================
    # PROCESAR CANCIÓN
    # =========================================================

    def process_song(
        self,
        song: Dict[str, Any],
        bpm: float = 120,
    ) -> Dict[str, Any]:
        """
        Procesa una canción hasta producir una secuencia
        preparada para Blender.

        Todavía NO ejecuta Blender.
        """

        # -----------------------------------------------------
        # 1. PROCESAR CANCIÓN
        # -----------------------------------------------------

        processed_song = (
            self.song_processor.process_song(
                song
            )
        )

        # -----------------------------------------------------
        # 2. PREPARAR ANIMACIÓN
        # -----------------------------------------------------

        prepared_song = (
            self.song_processor.prepare_for_animation(
                processed_song
            )
        )

        animation_input = (
            self.song_processor.create_animation_input(
                prepared_song
            )
        )

        concepts = animation_input.get(
            "concepts",
            [],
        )

        # -----------------------------------------------------
        # 3. GENERAR SIGNOS
        # -----------------------------------------------------

        generated_signs = (
            self.sign_generator.generate_sequence(
                concepts,
                language="DGS",
            )
        )

        # -----------------------------------------------------
        # 4. PREPARAR ESTADO
        # -----------------------------------------------------

        sign_status = []

        available_concepts = []

        unavailable_concepts = []

        sign_models = {}

        for generated in generated_signs:

            concept = str(
                generated.get(
                    "concept",
                    "",
                )
            ).strip().upper()

            status = generated.get(
                "status",
                "unknown",
            )

            sign_status.append(
                {
                    "concept": concept,
                    "status": status,
                    "language": generated.get(
                        "language",
                        "DGS",
                    ),
                    "confidence": float(
                        generated.get(
                            "confidence",
                            0.0,
                        )
                    ),
                }
            )

            sign = (
                self.sign_dictionary.get_sign(
                    concept
                )
            )

            if sign is None:

                unavailable_concepts.append(
                    concept
                )

                continue

            sign_models[
                concept
            ] = sign

            if status in (
                "mapped",
                "prototype",
                "verified",
                "defined",
            ):

                available_concepts.append(
                    concept
                )

            else:

                unavailable_concepts.append(
                    concept
                )

        # -----------------------------------------------------
        # 5. GENERAR MOVIMIENTOS
        # -----------------------------------------------------

        motion_plans = []

        animations = []

        current_time = 0.0

        fps = self.motion_generator.fps

        beat_duration = (
            60.0
            / float(bpm)
        )

        for generated in generated_signs:

            concept = str(
                generated.get(
                    "concept",
                    "",
                )
            ).strip().upper()

            confidence = float(
                generated.get(
                    "confidence",
                    0.0,
                )
            )

            raw_sign = generated.get(
                "sign"
            )

            # -------------------------------------------------
            # SIGNO NO DISPONIBLE
            # -------------------------------------------------

            if raw_sign is None:

                duration = beat_duration

                animations.append(
                    {
                        "concept": concept,

                        "start_time": (
                            current_time
                        ),

                        "duration": duration,

                        "end_time": (
                            current_time
                            + duration
                        ),

                        "status": "undefined",

                        "confidence": 0.0,

                        "keyframes": [],
                    }
                )

                current_time += duration

                continue

            # -------------------------------------------------
            # COMPILAR SIGNO → MOTION
            # -------------------------------------------------

            try:

                motion_input = (
                    self.sign_to_motion_compiler
                    .compile_sign(
                        raw_sign
                    )
                )

            except Exception as exc:

                print(
                    f"WARNING: no se pudo "
                    f"compilar {concept}: {exc}"
                )

                duration = (
                    beat_duration
                )

                animations.append(
                    {
                        "concept": concept,

                        "start_time": (
                            current_time
                        ),

                        "duration": duration,

                        "end_time": (
                            current_time
                            + duration
                        ),

                        "status": "undefined",

                        "confidence": 0.0,

                        "keyframes": [],
                    }
                )

                current_time += duration

                continue

            # -------------------------------------------------
            # DURACIÓN EXPERIMENTAL
            # -------------------------------------------------

            duration = float(
                beat_duration
            )

            # Algunas pruebas pueden proporcionar
            # una duración explícita.

            if "duration" in motion_input:

                try:

                    duration = float(
                        motion_input[
                            "duration"
                        ]
                    )

                except (
                    TypeError,
                    ValueError,
                ):

                    duration = (
                        beat_duration
                    )

            if duration <= 0:

                duration = (
                    beat_duration
                )

            # -------------------------------------------------
            # PREPARAR SIGNO PARA MOTION GENERATOR
            # -------------------------------------------------

            motion_sign = {
                "concept": concept,

                "duration": duration,

                "hand_shape": (
                    motion_input.get(
                        "hand_shape",
                        {},
                    )
                ),

                "orientation": (
                    motion_input.get(
                        "orientation",
                        {},
                    )
                ),

                "location": (
                    motion_input.get(
                        "location",
                        {},
                    )
                ),

                "movement": (
                    motion_input.get(
                        "movement",
                        {},
                    )
                ),

                "non_manual": (
                    motion_input.get(
                        "non_manual",
                        {},
                    )
                ),
            }

            # -------------------------------------------------
            # GENERAR MOTION PLAN
            # -------------------------------------------------

            try:

                plan = (
                    self.motion_generator
                    .generate_motion(
                        motion_sign
                    )
                )

            except Exception as exc:

                print(
                    f"WARNING: no se pudo "
                    f"generar movimiento para "
                    f"{concept}: {exc}"
                )

                animations.append(
                    {
                        "concept": concept,

                        "start_time": (
                            current_time
                        ),

                        "duration": duration,

                        "end_time": (
                            current_time
                            + duration
                        ),

                        "status": "undefined",

                        "confidence": confidence,

                        "keyframes": [],
                    }
                )

                current_time += duration

                continue

            # -------------------------------------------------
            # VALIDAR PLAN
            # -------------------------------------------------

            errors = plan.validate()

            if errors:

                raise RuntimeError(
                    f"MotionPlan inválido para "
                    f"{concept}: "
                    + "; ".join(
                        errors
                    )
                )

            # -------------------------------------------------
            # COMPILAR PLAN
            # -------------------------------------------------

            compiled = (
                self.motion_compiler.compile(
                    plan
                )
            )

            animation = {
                "concept": concept,

                "start_time": (
                    current_time
                ),

                "duration": float(
                    compiled[
                        "duration"
                    ]
                ),

                "end_time": (
                    current_time
                    + float(
                        compiled[
                            "duration"
                        ]
                    )
                ),

                "status": "defined",

                "confidence": confidence,

                "keyframes": (
                    compiled[
                        "keyframes"
                    ]
                ),
            }

            motion_plans.append(
                plan
            )

            animations.append(
                animation
            )

            current_time = (
                animation[
                    "end_time"
                ]
            )

        # -----------------------------------------------------
        # 6. CREAR SECUENCIA
        # -----------------------------------------------------

        sequence = {
            "bpm": int(
                bpm
            ),

            "fps": fps,

            "beat_duration": (
                beat_duration
            ),

            "total_duration": (
                current_time
            ),

            "animations": (
                animations
            ),
        }

        # -----------------------------------------------------
        # 7. PREPARAR PARA BLENDER
        # -----------------------------------------------------

        prepared_sequence = (
            self.blender_renderer
            .prepare_sequence(
                sequence
            )
        )

        # -----------------------------------------------------
        # 8. METADATOS
        # -----------------------------------------------------

        prepared_sequence[
            "song"
        ] = {
            "title": processed_song[
                "title"
            ],

            "word_count": processed_song[
                "word_count"
            ],
        }

        prepared_sequence[
            "concepts"
        ] = sign_status

        prepared_sequence[
            "available_concepts"
        ] = available_concepts

        prepared_sequence[
            "unavailable_concepts"
        ] = unavailable_concepts

        prepared_sequence[
            "generated_signs"
        ] = generated_signs

        prepared_sequence[
            "motion_plans"
        ] = [
            plan.to_dict()
            for plan
            in motion_plans
        ]

        prepared_sequence[
            "pipeline_status"
        ] = "ready_for_renderer"

        return prepared_sequence


# =============================================================
# PRUEBA DIRECTA
# =============================================================

if __name__ == "__main__":

    pipeline = SignMusicPipeline()

    song = {
        "title": "Save Me, Save You",

        "lyrics": (
            "Save me, save you"
        ),
    }

    result = pipeline.process_song(
        song,
        bpm=120,
    )

    print()
    print(
        "=== SIGNMUSIC FULL PIPELINE ==="
    )

    print(
        "Pipeline:",
        result[
            "pipeline_status"
        ],
    )

    print(
        "Song:",
        result[
            "song"
        ],
    )

    print(
        "Concepts:",
        result[
            "concepts"
        ],
    )

    print(
        "Generated signs:",
        len(
            result[
                "generated_signs"
            ]
        ),
    )

    print(
        "Available:",
        result[
            "available_concepts"
        ],
    )

    print(
        "Unavailable:",
        result[
            "unavailable_concepts"
        ],
    )

    print(
        "Animations:",
        len(
            result[
                "animations"
            ]
        ),
    )

    print(
        "Animation concepts:",
        [
            animation[
                "concept"
            ]
            for animation
            in result[
                "animations"
            ]
        ],
    )

    print(
        "Motion plans:",
        len(
            result[
                "motion_plans"
            ]
        ),
    )

    print(
        "Total duration:",
        result[
            "total_duration"
        ],
    )

    print(
        "Renderer:",
        result[
            "renderer"
        ],
    )