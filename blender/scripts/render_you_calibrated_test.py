$content = @'
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
    / "you_calibrated_test"
)

ARMATURE_NAME = "Armature"

FRAMES = [1, 10, 20]

RIGHT_ARM = "mixamorig7:RightArm"
RIGHT_FOREARM = "mixamorig7:RightForeArm"

ARM_X_ANGLES = {
    1: 0.0,
    10: 15.0,
    20: 30.0,
}

FOREARM_X_ANGLES = {
    1: 0.0,
    10: 7.5,
    20: 15.0,
}


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
            points.append(
                obj.matrix_world @ Vector(corner)
            )

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


def get_or_create_camera(target, radius):
    camera = bpy.data.objects.get(
        "SignmusicValidationCamera"
    )

    if camera is None:
        camera_data = bpy.data.cameras.new(
            "SignmusicValidationCameraData"
        )

        camera = bpy.data.objects.new(
            "SignmusicValidationCamera",
            camera_data,
        )

        bpy.context.scene.collection.objects.link(
            camera
        )

    camera.location = Vector((
        target.x,
        target.y - radius * 2.8,
        target.z,
    ))

    camera.data.lens = 55

    look_at(
        camera,
        target,
    )

    bpy.context.scene.camera = camera

    return camera


def get_or_create_area_light(
    name,
    location,
    energy,
    size,
    target,
):
    light = bpy.data.objects.get(name)

    if light is None:
        data = bpy.data.lights.new(
            f"{name}_DATA",
            type="AREA",
        )

        light = bpy.data.objects.new(
            name,
            data,
        )

        bpy.context.scene.collection.objects.link(
            light
        )

    light.data.energy = energy
    light.data.shape = "DISK"
    light.data.size = size

    light.location = location

    look_at(
        light,
        target,
    )

    return light


def setup_lighting(target, radius):
    get_or_create_area_light(
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

    get_or_create_area_light(
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

    get_or_create_area_light(
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


def apply_calibrated_you_pose(
    armature,
    frame,
):
    arm = armature.pose.bones.get(
        RIGHT_ARM
    )

    forearm = armature.pose.bones.get(
        RIGHT_FOREARM
    )

    if arm is None:
        raise RuntimeError(
            f"No se encontro {RIGHT_ARM}"
        )

    if forearm is None:
        raise RuntimeError(
            f"No se encontro {RIGHT_FOREARM}"
        )

    arm.rotation_mode = "XYZ"
    forearm.rotation_mode = "XYZ"

    arm_rotation = arm.rotation_euler.copy()
    forearm_rotation = forearm.rotation_euler.copy()

    # Eliminamos la rotacion Z del movimiento anterior.
    arm_rotation.z = 0.0
    forearm_rotation.z = 0.0

    # Aplicamos la direccion calibrada:
    # +X = hacia la camara / hacia delante.
    arm_rotation.x = ARM_X_ANGLES[frame] * 3.141592653589793 / 180.0
    forearm_rotation.x = FOREARM_X_ANGLES[frame] * 3.141592653589793 / 180.0

    arm.rotation_euler = arm_rotation
    forearm.rotation_euler = forearm_rotation

    bpy.context.view_layer.update()


def main():
    print("=" * 70)
    print("SIGNMUSIC - TEST VISUAL YOU CALIBRADO")
    print("=" * 70)

    print()
    print(f"Blend: {BLEND_PATH}")

    if not BLEND_PATH.exists():
        print()
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
        print()
        print(
            f"ERROR: No se encontro '{ARMATURE_NAME}'."
        )
        return 1

    print(
        f"Armature encontrado: {armature.name}"
    )

    minimum, maximum = get_scene_bounds()

    if minimum is None:
        print()
        print(
            "ERROR: No se encontraron meshes."
        )
        return 1

    center = (
        minimum + maximum
    ) / 2.0

    size = max(
        maximum.x - minimum.x,
        maximum.y - minimum.y,
        maximum.z - minimum.z,
    )

    radius = max(
        size * 0.5,
        1.0,
    )

    get_or_create_camera(
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

        print()
        print("-" * 70)
        print(
            f"TEST FRAME {frame}"
        )

        scene.frame_set(frame)

        bpy.context.view_layer.update()

        apply_calibrated_you_pose(
            armature,
            frame,
        )

        output_path = (
            OUTPUT_DIR
            / f"you_calibrated_{frame:03d}.png"
        )

        scene.render.filepath = str(
            output_path
        )

        print(
            f"RightArm X: {ARM_X_ANGLES[frame]} degrees"
        )

        print(
            f"RightForeArm X: {FOREARM_X_ANGLES[frame]} degrees"
        )

        print(
            f"Output: {output_path}"
        )

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
            print(
                "ERROR DURANTE EL RENDER:"
            )
            print(
                repr(exc)
            )
            return 1

        print(
            "Render completado."
        )

    print()
    print("=" * 70)
    print("TEST VISUAL COMPLETADO")
    print("=" * 70)

    print()
    print("Archivos:")

    for frame in FRAMES:
        print(
            OUTPUT_DIR
            / f"you_calibrated_{frame:03d}.png"
        )

    print()
    print(
        "Este test NO modifica ni guarda el .blend."
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
'@

[System.IO.File]::WriteAllText(
    "blender\scripts\render_you_calibrated_test.py",
    $content,
    [System.Text.UTF8Encoding]::new($false)
)

Write-Host "ARCHIVO CREADO: blender\scripts\render_you_calibrated_test.py"