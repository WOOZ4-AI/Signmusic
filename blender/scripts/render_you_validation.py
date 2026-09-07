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
    objects = [
        obj
        for obj in bpy.context.scene.objects
        if obj.type == "MESH"
        and obj.visible_get()
    ]

    if not objects:
        return None, None

    points = []

    for obj in objects:
        for corner in obj.bound_box:
            points.append(obj.matrix_world @ Vector(corner))

    minimum = Vector((
        min(p.x for p in points),
        min(p.y for p in points),
        min(p.z for p in points),
    ))

    maximum = Vector((
        max(p.x for p in points),
        max(p.y for p in points),
        max(p.z for p in points),
    ))

    return minimum, maximum


def look_at(obj, target):
    direction = target - obj.location

    if direction.length == 0:
        return

    obj.rotation_euler = direction.to_track_quat(
        "-Z",
        "Y",
    ).to_euler()


def create_camera(target, radius):
    camera_data = bpy.data.cameras.get(
        "SignmusicValidationCameraData"
    )

    if camera_data is None:
        camera_data = bpy.data.cameras.new(
            "SignmusicValidationCameraData"
        )

    camera = bpy.data.objects.get(
        "SignmusicValidationCamera"
    )

    if camera is None:
        camera = bpy.data.objects.new(
            "SignmusicValidationCamera",
            camera_data,
        )
        bpy.context.scene.collection.objects.link(camera)

    camera.data.lens = 55

    camera.location = Vector((
        target.x,
        target.y - radius * 2.8,
        target.z,
    ))

    look_at(camera, target)

    bpy.context.scene.camera = camera


def create_area_light(
    name,
    location,
    energy,
    size,
    target,
):
    light_data = bpy.data.lights.get(
        f"{name}_DATA"
    )

    if light_data is None:
        light_data = bpy.data.lights.new(
            f"{name}_DATA",
            type="AREA",
        )

    light_data.energy = energy
    light_data.shape = "DISK"
    light_data.size = size

    light = bpy.data.objects.get(name)

    if light is None:
        light = bpy.data.objects.new(
            name,
            light_data,
        )
        bpy.context.scene.collection.objects.link(light)

    light.location = location

    look_at(light, target)


def setup_lighting(target, radius):
    create_area_light(
        "Signmusic_Key_Light",
        Vector((
            target.x - radius,
            target.y - radius,
            target.z + radius,
        )),
        900,
        radius * 1.5,
        target,
    )

    create_area_light(
        "Signmusic_Fill_Light",
        Vector((
            target.x + radius,
            target.y - radius * 0.5,
            target.z + radius * 0.5,
        )),
        500,
        radius,
        target,
    )

    create_area_light(
        "Signmusic_Rim_Light",
        Vector((
            target.x,
            target.y + radius,
            target.z + radius,
        )),
        700,
        radius,
        target,
    )


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
    print(f"Blend: {BLEND_PATH}")

    if not BLEND_PATH.exists():
        print("ERROR: No existe el archivo .blend.")
        return 1

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    armature = bpy.data.objects.get(
        ARMATURE_NAME
    )

    if armature is None:
        print(
            f"ERROR: No se encontro '{ARMATURE_NAME}'."
        )
        return 1

    print(
        f"Armature encontrado: {armature.name}"
    )

    minimum, maximum = get_scene_bounds()

    if minimum is None:
        print("ERROR: No se encontraron meshes.")
        return 1

    center = (minimum + maximum) / 2.0

    size = max(
        maximum.x - minimum.x,
        maximum.y - minimum.y,
        maximum.z - minimum.z,
    )

    radius = max(
        size * 0.5,
        1.0,
    )

    print()
    print(
        f"Centro: {tuple(round(v, 3) for v in center)}"
    )

    print(
        f"Tamaño: {round(size, 3)}"
    )

    create_camera(
        center,
        radius,
    )

    setup_lighting(
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
        scene.frame_set(frame)

        bpy.context.view_layer.update()

        output_path = (
            OUTPUT_DIR
            / f"you_frame_{frame:03d}.png"
        )

        scene.render.filepath = str(output_path)

        print()
        print("-" * 70)
        print(f"RENDER FRAME {frame}")
        print(f"Output: {output_path}")

        try:
            result = bpy.ops.render.render(
                write_still=True
            )

            if "FINISHED" not in result:
                print(
                    f"Render no finalizado: {result}"
                )
                return 1

        except Exception as exc:
            print()
            print("ERROR DURANTE EL RENDER:")
            print(repr(exc))
            return 1

        print("Render completado.")

    print()
    print("=" * 70)
    print("RENDER DE VALIDACION COMPLETADO")
    print("=" * 70)

    for frame in FRAMES:
        print(
            OUTPUT_DIR
            / f"you_frame_{frame:03d}.png"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())