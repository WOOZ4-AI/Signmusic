import bpy
from pathlib import Path
from mathutils import Vector


PROJECT_ROOT = Path.cwd()

BLEND_PATH = (
    PROJECT_ROOT
    / "blender"
    / "output"
    / "signmusic_pipeline_generated.blend"
)

OUTPUT_DIR = (
    PROJECT_ROOT
    / "blender"
    / "output"
    / "you_validation"
)

ARMATURE_NAME = "Armature"

FRAMES = [1, 10, 20]


def get_scene_bounds():
    mesh_objects = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "MESH"
        and obj.visible_get()
    ]

    if not mesh_objects:
        return None, None

    points = []

    for obj in mesh_objects:
        for corner in obj.bound_box:
            world_corner = obj.matrix_world @ Vector(corner)
            points.append(world_corner)

    min_corner = Vector(
        (
            min(p.x for p in points),
            min(p.y for p in points),
            min(p.z for p in points),
        )
    )

    max_corner = Vector(
        (
            max(p.x for p in points),
            max(p.y for p in points),
            max(p.z for p in points),
        )
    )

    return min_corner, max_corner


def look_at(camera, target):
    direction = target - camera.location

    if direction.length == 0:
        return

    camera.rotation_euler = direction.to_track_quat(
        "-Z",
        "Y",
    ).to_euler()


def find_or_create_camera(target, radius):
    camera = bpy.context.scene.camera

    if camera is None:
        camera_data = bpy.data.cameras.new(
            "SignmusicValidationCamera"
        )

        camera = bpy.data.objects.new(
            "SignmusicValidationCamera",
            camera_data,
        )

        bpy.context.scene.collection.objects.link(
            camera
        )

    camera.location = Vector(
        (
            target.x,
            target.y - radius * 2.8,
            target.z,
        )
    )

    camera.data.lens = 55

    look_at(
        camera,
        target,
    )

    bpy.context.scene.camera = camera

    return camera


def create_light(
    name,
    location,
    energy,
    size,
    target,
):
    data = bpy.data.lights.new(
        name,
        type="AREA",
    )

    data.energy = energy
    data.shape = "DISK"
    data.size = size

    light = bpy.data.objects.new(
        name,
        data,
    )

    bpy.context.scene.collection.objects.link(
        light
    )

    light.location = location

    look_at(
        light,
        target,
    )

    return light


def create_lights(target, radius):
    existing_names = {
        obj.name
        for obj in bpy.context.scene.objects
    }

    created = []

    if "Signmusic_Key_Light" not in existing_names:
        created.append(
            create_light(
                "Signmusic_Key_Light",
                Vector(
                    (
                        target.x - radius,
                        target.y - radius,
                        target.z + radius,
                    )
                ),
                900,
                radius * 1.5,
                target,
            )
        )

    if "Signmusic_Fill_Light" not in existing_names:
        created.append(
            create_light(
                "Signmusic_Fill_Light",
                Vector(
                    (
                        target.x + radius,
                        target.y - radius * 0.5,
                        target.z + radius * 0.5,
                    )
                ),
                500,
                radius,
                target,
            )
        )

    if "Signmusic_Rim_Light" not in existing_names:
        created.append(
            create_light(
                "Signmusic_Rim_Light",
                Vector(
                    (
                        target.x,
                        target.y + radius,
                        target.z + radius,
                    )
                ),
                700,
                radius,
                target,
            )
        )

    return created


def configure_render():
    scene = bpy.context.scene

    scene.render.engine = "BLENDER_EEVEE"

    scene.render.resolution_x = 700
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100

    scene.render.image_settings.file_format = "PNG"

    scene.render.film_transparent = False

    scene.world.color = (
        0.025,
        0.025,
        0.025,
    )


def main():
    print("=" * 70)
    print("SIGNMUSIC - RENDER DE VALIDACION YOU")
    print("=" * 70)

    print()
    print(f"Archivo: {BLEND_PATH}")

    if not BLEND_PATH.exists():
        print()
        print("ERROR: No existe:")
        print(BLEND_PATH)
        return 1

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    armature = bpy.data.objects.get(
        ARMATURE_NAME
    )

    if armature is None:
        print()
        print(
            f"ERROR: No se encontro '{ARMATURE_NAME}'."
        )
        return 1

    print(
        f"Armature encontrado: {armature.name}"
    )

    min_corner, max_corner = get_scene_bounds()

    if min_corner is None:
        print()
        print(
            "ERROR: No se encontraron objetos MESH."
        )
        return 1

    center = (
        min_corner + max_corner
    ) / 2.0

    size_x = max_corner.x - min_corner.x
    size_y = max_corner.y - min_corner.y
    size_z = max_corner.z - min_corner.z

    size = max(
        size_x,
        size_y,
        size_z,
    )

    radius = max(
        size * 0.5,
        1.0,
    )

    print()
    print("Bounds del avatar:")
    print(
        f"  Min: {tuple(round(v, 3) for v in min_corner)}"
    )
    print(
        f"  Max: {tuple(round(v, 3) for v in max_corner)}"
    )

    print()
    print(
        f"Centro: {tuple(round(v, 3) for v in center)}"
    )

    print(
        f"Tamano: {round(size, 3)}"
    )

    find_or_create_camera(
        center,
        radius,
    )

    create_lights(
        center,
        radius,
    )

    configure_render()

    scene = bpy.context.scene

    print()
    print(
        f"Motor de render: {scene.render.engine}"
    )

    for frame in FRAMES:
        print()
        print("-" * 70)
        print(
            f"RENDER FRAME {frame}"
        )

        scene.frame_set(frame)

        bpy.context.view_layer.update()

        output_path = (
            OUTPUT_DIR
            / f"you_frame_{frame:03d}.png"
        )

        scene.render.filepath = str(
            output_path
        )

        print(
            f"Output: {output_path}"
        )

        try:
            bpy.ops.render.render(
                write_still=True
            )
        except Exception as exc:
            print()
            print("ERROR DURANTE EL RENDER:")
            print(repr(exc))
            return 1

        print(
            "Render completado."
        )

    print()
    print("=" * 70)
    print("RENDER DE VALIDACION COMPLETADO")
    print("=" * 70)

    print()
    print("Archivos generados:")

    for frame in FRAMES:
        path = (
            OUTPUT_DIR
            / f"you_frame_{frame:03d}.png"
        )

        print(
            f"  - {path}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())