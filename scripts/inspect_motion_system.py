from __future__ import annotations

import ast
import inspect
import importlib
import sys
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


TARGET_MODULES = [
    "backend.motion_plan",
    "backend.motion_generator",
    "backend.movement_compiler",
    "backend.motion_compiler",
    "backend.arm_motion_solver",
    "backend.arm_trajectory_compiler",
    "backend.blender_bridge",
    "backend.blender_renderer",
    "backend.avatar_renderer",
]


def print_header(title: str) -> None:
    print()
    print("=" * 78)
    print(title)
    print("=" * 78)


def safe_signature(
    obj: Any,
) -> str:

    try:
        return str(
            inspect.signature(obj)
        )
    except (
        TypeError,
        ValueError,
    ):
        return "(signature unavailable)"


def describe_class(
    cls: type,
) -> None:

    print()
    print(
        f"CLASS: {cls.__name__}"
    )

    print(
        f"  Module: {cls.__module__}"
    )

    print(
        f"  Constructor: "
        f"{safe_signature(cls)}"
    )

    try:
        source_file = inspect.getsourcefile(
            cls
        )

        if source_file:
            print(
                f"  File: {source_file}"
            )

    except (
        TypeError,
        OSError,
    ):
        pass

    print(
        "  Methods:"
    )

    for name in sorted(
        cls.__dict__.keys()
    ):

        if name.startswith("__"):
            continue

        try:
            value = getattr(
                cls,
                name,
            )
        except Exception:
            continue

        if callable(value):

            print(
                f"    - {name}"
                f"{safe_signature(value)}"
            )

    # Dataclass fields.
    dataclass_fields = getattr(
        cls,
        "__dataclass_fields__",
        None,
    )

    if dataclass_fields:

        print(
            "  Dataclass fields:"
        )

        for name, field in dataclass_fields.items():

            print(
                f"    - {name}"
            )


def inspect_module(
    module_name: str,
) -> None:

    print_header(
        f"MODULE: {module_name}"
    )

    try:

        module = importlib.import_module(
            module_name
        )

    except Exception as exc:

        print(
            f"IMPORT ERROR: "
            f"{type(exc).__name__}: {exc}"
        )

        return

    print(
        f"Loaded from: "
        f"{getattr(module, '__file__', None)}"
    )

    classes = []

    for name, obj in inspect.getmembers(
        module,
        inspect.isclass,
    ):

        if obj.__module__ != module_name:
            continue

        classes.append(
            obj
        )

    if not classes:

        print(
            "  No classes defined directly "
            "in this module."
        )

    for cls in classes:

        describe_class(
            cls
        )


def inspect_source_tree() -> None:

    print_header(
        "SOURCE TREE CHECK"
    )

    for relative_path in (
        "backend/motion_plan.py",
        "backend/motion_generator.py",
        "backend/movement_compiler.py",
        "backend/motion_compiler.py",
        "backend/arm_motion_solver.py",
        "backend/arm_trajectory_compiler.py",
        "backend/blender_bridge.py",
        "backend/blender_renderer.py",
        "backend/avatar_renderer.py",
    ):

        path = (
            PROJECT_ROOT
            / relative_path
        )

        print(
            f"{relative_path}: "
            f"{'FOUND' if path.exists() else 'MISSING'}"
        )


def inspect_relevant_names() -> None:

    print_header(
        "PROJECT-WIDE MOTION REFERENCES"
    )

    backend_root = (
        PROJECT_ROOT
        / "backend"
    )

    if not backend_root.exists():

        print(
            "backend directory not found."
        )

        return

    interesting_names = {
        "MotionPlan",
        "MotionGenerator",
        "MotionEvent",
        "MovementCompiler",
        "ArmMotionSolver",
        "ArmTrajectoryCompiler",
        "BlenderBridge",
        "AvatarRenderer",
    }

    found: set[str] = set()

    for path in backend_root.rglob(
        "*.py"
    ):

        try:

            source = path.read_text(
                encoding="utf-8"
            )

            tree = ast.parse(
                source
            )

        except (
            OSError,
            UnicodeDecodeError,
            SyntaxError,
        ):

            continue

        for node in ast.walk(
            tree
        ):

            if isinstance(
                node,
                ast.ClassDef,
            ):

                if node.name in interesting_names:

                    found.add(
                        node.name
                    )

                    print(
                        f"{node.name}: "
                        f"{path.relative_to(PROJECT_ROOT)}:"
                        f"{node.lineno}"
                    )

    if not found:

        print(
            "No known motion classes "
            "were found."
        )


def inspect_motion_plan_json() -> None:

    print_header(
        "EXISTING MOTION / PIPELINE JSON FILES"
    )

    candidates = [
        PROJECT_ROOT
        / "blender"
        / "output"
        / "pipeline_sequence.json",

        PROJECT_ROOT
        / "blender"
        / "output"
        / "motion_plan.json",

        PROJECT_ROOT
        / "data"
        / "motion",
    ]

    for path in candidates:

        if not path.exists():
            continue

        if path.is_file():

            print(
                f"FILE: "
                f"{path.relative_to(PROJECT_ROOT)}"
            )

            try:

                text = path.read_text(
                    encoding="utf-8"
                )

                print(
                    f"  Size: "
                    f"{len(text)} bytes"
                )

                print(
                    "  First 1200 characters:"
                )

                print(
                    text[:1200]
                )

            except OSError as exc:

                print(
                    f"  READ ERROR: {exc}"
                )

        elif path.is_dir():

            print(
                f"DIRECTORY: "
                f"{path.relative_to(PROJECT_ROOT)}"
            )

            for child in sorted(
                path.glob("*")
            ):

                print(
                    f"  - {child.name}"
                )


def main() -> None:

    print_header(
        "SIGNMUSIC MOTION SYSTEM INSPECTOR"
    )

    print(
        f"Project root:\n"
        f"{PROJECT_ROOT}"
    )

    inspect_source_tree()

    inspect_relevant_names()

    for module_name in TARGET_MODULES:

        inspect_module(
            module_name
        )

    inspect_motion_plan_json()

    print()
    print(
        "=" * 78
    )
    print(
        "INSPECTION COMPLETE"
    )
    print(
        "=" * 78
    )


if __name__ == "__main__":
    main()