from __future__ import annotations

import json
from pathlib import Path
import sys
from typing import Any


PROJECT_ROOT = Path(
    __file__
).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(
        0,
        str(PROJECT_ROOT)
    )


from backend.translation.dgs_motion_compiler import (
    DGSMotionCompiler,
)


# ======================================================================
# CONFIGURATION
# ======================================================================

INPUT_LYRICS = """I need you
I cannot find you
I still need you"""

OUTPUT_PATH = (
    PROJECT_ROOT
    / "blender"
    / "output"
    / "pipeline_sequence.json"
)


# ======================================================================
# HELPERS
# ======================================================================

def print_header(
    title: str,
) -> None:

    print()
    print(
        "=" * 78
    )
    print(
        title
    )
    print(
        "=" * 78
    )


def save_json(
    payload: dict[str, Any],
    output_path: Path,
) -> None:

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with output_path.open(
        "w",
        encoding="utf-8",
    ) as file:

        json.dump(
            payload,
            file,
            ensure_ascii=False,
            indent=4,
        )


# ======================================================================
# MAIN
# ======================================================================

def main() -> None:

    print_header(
        "SIGNMUSIC DGS → PIPELINE SEQUENCE"
    )

    print(
        "Project:"
    )

    print(
        PROJECT_ROOT
    )

    print()

    print(
        "Lyrics:"
    )

    print(
        INPUT_LYRICS
    )

    # --------------------------------------------------------------
    # Compile
    # --------------------------------------------------------------

    compiler = (
        DGSMotionCompiler()
    )

    print()
    print(
        "Compiling..."
    )

    compiled = (
        compiler.compile_from_lyrics(
            INPUT_LYRICS
        )
    )

    # --------------------------------------------------------------
    # Validation
    # --------------------------------------------------------------

    print()
    print(
        "Validating..."
    )

    errors = (
        compiler.validate_compiled(
            compiled
        )
    )

    if errors:

        print(
            "VALIDATION ERRORS:"
        )

        for error in errors:

            print(
                f"  - {error}"
            )

        raise RuntimeError(
            "The generated motion sequence "
            "failed validation."
        )

    print(
        "Validation: OK"
    )

    # --------------------------------------------------------------
    # Convert to Blender pipeline format
    # --------------------------------------------------------------

    pipeline = (
        compiler._convert_to_pipeline_format(
            compiled
        )
    )

    # Add explicit source information.
    pipeline[
        "metadata"
    ][
        "source_language"
    ] = compiled.get(
        "source_language",
        "unknown",
    )

    pipeline[
        "metadata"
    ][
        "target_language"
    ] = compiled.get(
        "target_language",
        "DGS",
    )

    pipeline[
        "metadata"
    ][
        "generated_by"
    ] = (
        "scripts/compile_dgs_pipeline.py"
    )

    pipeline[
        "metadata"
    ][
        "input_lyrics"
    ] = INPUT_LYRICS

    # --------------------------------------------------------------
    # Save
    # --------------------------------------------------------------

    save_json(
        pipeline,
        OUTPUT_PATH,
    )

    # --------------------------------------------------------------
    # Statistics
    # --------------------------------------------------------------

    animations = pipeline.get(
        "animations",
        [],
    )

    total_keyframes = sum(
        len(
            animation.get(
                "keyframes",
                [],
            )
        )
        for animation
        in animations
        if isinstance(
            animation,
            dict,
        )
    )

    print()
    print_header(
        "GENERATED PIPELINE"
    )

    print(
        f"Output: {OUTPUT_PATH}"
    )

    print(
        f"FPS: "
        f"{pipeline.get('fps')}"
    )

    print(
        f"Total duration: "
        f"{pipeline.get('total_duration', 0.0):.3f}s"
    )

    print(
        f"Animations: "
        f"{len(animations)}"
    )

    print(
        f"Total keyframes: "
        f"{total_keyframes}"
    )

    print()

    for index, animation in enumerate(
        animations,
        start=1,
    ):

        concept = animation.get(
            "concept",
            "UNKNOWN",
        )

        status = animation.get(
            "status",
            "unknown",
        )

        start_time = animation.get(
            "start_time",
            0.0,
        )

        end_time = animation.get(
            "end_time",
            0.0,
        )

        keyframe_count = len(
            animation.get(
                "keyframes",
                [],
            )
        )

        print(
            f"{index:02d}. "
            f"{concept:<15} "
            f"{status:<28} "
            f"{start_time:.3f}s → "
            f"{end_time:.3f}s | "
            f"keyframes={keyframe_count}"
        )

    # --------------------------------------------------------------
    # Inspect first resolved animation
    # --------------------------------------------------------------

    print()

    for animation in animations:

        keyframes = animation.get(
            "keyframes",
            [],
        )

        if not keyframes:
            continue

        print_header(
            f"FIRST MOTION: {animation.get('concept', 'UNKNOWN')}"
        )

        for keyframe in keyframes:

            bones = keyframe.get(
                "bones",
                {},
            )

            print(
                f"Time: "
                f"{keyframe.get('time', 0.0):.3f}s"
            )

            print(
                f"Phase: "
                f"{keyframe.get('phase', '?')}"
            )

            print(
                f"Bone count: "
                f"{len(bones)}"
            )

            for bone_name in sorted(
                bones.keys()
            ):

                transform = bones[
                    bone_name
                ]

                print(
                    f"  {bone_name}: "
                    f"{transform}"
                )

            print()

        break

    print_header(
        "COMPILATION COMPLETE"
    )

    print(
        "pipeline_sequence.json generado correctamente."
    )

    print(
        "El archivo ya está listo para el executor de Blender."
    )


if __name__ == "__main__":

    main()