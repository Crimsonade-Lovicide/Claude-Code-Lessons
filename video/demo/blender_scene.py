"""Build and render a massing study of Wright's mile-high Illinois tower with Blender's Python API.

    blender -b -P blender_scene.py -- --out <dir> --seconds 7.3 --camera orbit \
        [--res 960x540] [--samples 16] [--fps 24] [--engine CYCLES|CYCLES_GPU|EEVEE] [--frames 1,48]

Writes <dir>/0001.png, 0002.png, ... Runs headless, so Claude Code (or a cron job) can
render without anyone opening Blender. The model is a massing study: the height and floor
count are documented, the shape is a simplified reading of the published drawings.
"""
import argparse
import math
import random
import sys

import bpy
from mathutils import Vector

MILE_M = 1609.0  # documented: one mile


def args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--seconds", type=float, required=True)
    p.add_argument("--camera", choices=["orbit", "rise"], default="orbit")
    p.add_argument("--res", default="960x540")
    p.add_argument("--samples", type=int, default=16)
    p.add_argument("--fps", type=int, default=24)
    p.add_argument("--engine", default="CYCLES")
    p.add_argument("--frames", default="", help="render only these frames, e.g. 1,48 (for previews)")
    return p.parse_args(argv)


def material(name, color, metallic=0.0, roughness=0.5, emission=None):
    m = bpy.data.materials.new(name)
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*color, 1)
    bsdf.inputs["Metallic"].default_value = metallic
    bsdf.inputs["Roughness"].default_value = roughness
    if emission:
        bsdf.inputs["Emission Color"].default_value = (*emission[0], 1)
        bsdf.inputs["Emission Strength"].default_value = emission[1]
    return m


def window_material(name):
    """Dark facade with a procedural grid of lit windows; each building gets its own mix."""
    m = bpy.data.materials.new(name)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (0.05, 0.05, 0.06, 1)
    bsdf.inputs["Roughness"].default_value = 0.6
    geometry = nt.nodes.new("ShaderNodeNewGeometry")  # world position, so windows are sized in meters
    # Facade coordinates: horizontal = x + y (runs along any wall), vertical = z.
    split = nt.nodes.new("ShaderNodeSeparateXYZ")
    along = nt.nodes.new("ShaderNodeMath")
    along.operation = "ADD"
    facade = nt.nodes.new("ShaderNodeCombineXYZ")
    bricks = nt.nodes.new("ShaderNodeTexBrick")  # a brick pattern doubles as a window grid
    bricks.inputs["Scale"].default_value = 0.12
    bricks.inputs["Mortar Size"].default_value = 0.05
    bricks.inputs["Color1"].default_value = (1.0, 0.72, 0.42, 1)
    bricks.inputs["Color2"].default_value = (0.25, 0.18, 0.1, 1)  # some windows dark
    bricks.inputs["Mortar"].default_value = (0.0, 0.0, 0.0, 1)
    info = nt.nodes.new("ShaderNodeObjectInfo")
    strength = nt.nodes.new("ShaderNodeMath")
    strength.operation = "MULTIPLY"
    strength.inputs[1].default_value = 0.18
    nt.links.new(geometry.outputs["Position"], split.inputs["Vector"])
    nt.links.new(split.outputs["X"], along.inputs[0])
    nt.links.new(split.outputs["Y"], along.inputs[1])
    nt.links.new(along.outputs["Value"], facade.inputs["X"])
    nt.links.new(split.outputs["Z"], facade.inputs["Y"])
    nt.links.new(facade.outputs["Vector"], bricks.inputs["Vector"])
    nt.links.new(bricks.outputs["Color"], bsdf.inputs["Emission Color"])
    nt.links.new(info.outputs["Random"], strength.inputs[0])
    nt.links.new(strength.outputs["Value"], bsdf.inputs["Emission Strength"])
    return m


def tapered_prism(name, sides, r_bottom, r_top, z0, z1, rotation=0.0):
    """A straight-sided tapering prism: the basic massing unit."""
    verts, faces = [], []
    for r, z in ((r_bottom, z0), (r_top, z1)):
        for i in range(sides):
            a = rotation + 2 * math.pi * i / sides
            verts.append((r * math.cos(a), r * math.sin(a), z))
    for i in range(sides):
        j = (i + 1) % sides
        faces.append((i, j, sides + j, sides + i))
    faces.append(tuple(range(sides - 1, -1, -1)))
    faces.append(tuple(range(sides, 2 * sides)))
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(verts, [], faces)
    obj = bpy.data.objects.new(name, mesh)
    bpy.context.collection.objects.link(obj)
    return obj


def build_tower(mat_body, mat_fin, mat_lights):
    # Main shaft: a triangular plan that tapers continuously to the spire.
    tapered_prism("SM_Illinois_Shaft", 3, 70, 8, 0, MILE_M * 0.93, rotation=math.pi / 2).data.materials.append(mat_body)
    tapered_prism("SM_Illinois_Spire", 3, 8, 0.5, MILE_M * 0.93, MILE_M, rotation=math.pi / 2).data.materials.append(mat_body)
    # Three buttress fins, one per corner, tallest at the base.
    for k in range(3):
        a = math.pi / 2 + 2 * math.pi * k / 3
        fin = tapered_prism(f"SM_Illinois_Fin{k}", 4, 16, 2, 0, MILE_M * 0.55, rotation=math.pi / 4)
        fin.scale = (2.6, 0.35, 1.0)
        fin.rotation_euler = (0, 0, a)
        fin.location = (62 * math.cos(a), 62 * math.sin(a), 0)
        fin.data.materials.append(mat_fin)
    # Floor bands: thin glowing rings every 40 floors so the scale reads at dusk.
    for floor in range(40, 528, 40):
        z = MILE_M * floor / 528
        r = 70 + (8 - 70) * (z / (MILE_M * 0.93))
        band = tapered_prism(f"SM_Illinois_Band{floor}", 3, r + 0.6, r + 0.6, z, z + 2.5, rotation=math.pi / 2)
        band.data.materials.append(mat_lights)


def build_city(mat_blocks, mat_ground, mat_water):
    rng = random.Random(1956)
    # Planes reach past the horizon (about 110 km from 1 km up) so their edges never show.
    bpy.ops.mesh.primitive_plane_add(size=400000, location=(0, 0, -0.5))
    bpy.context.object.data.materials.append(mat_ground)
    # Lake to the east, as on Chicago's lakefront.
    bpy.ops.mesh.primitive_plane_add(size=400000, location=(201600, 0, -0.3))
    bpy.context.object.data.materials.append(mat_water)
    # City blocks: one joined mesh keeps the scene light for CPU rendering.
    bpy.ops.mesh.primitive_cube_add(size=1)
    block = bpy.context.object
    block.data.materials.append(mat_blocks)
    for x in range(-12, 13):
        for y in range(-12, 13):
            if abs(x) < 2 and abs(y) < 2:
                continue  # plaza around the tower
            if rng.random() < 0.15:
                continue
            h = rng.choice([12, 20, 30, 45, 60, 90, 140]) * (1.5 if abs(x) + abs(y) < 6 else 1.0)
            dup = block.copy()
            dup.data = block.data
            dup.scale = (rng.uniform(55, 90), rng.uniform(55, 90), h)
            dup.location = (x * 120, y * 120, h / 2)
            bpy.context.collection.objects.link(dup)
    bpy.data.objects.remove(block)


def build_world(sun_elevation_deg=1.5, sun_rotation_deg=40.0):
    world = bpy.context.scene.world or bpy.data.worlds.new("World")
    bpy.context.scene.world = world
    nt = world.node_tree
    nt.nodes.clear()
    sky = nt.nodes.new("ShaderNodeTexSky")
    # Physical sky model; the enum was renamed across Blender versions, so take the first available.
    for sky_type in ("MULTIPLE_SCATTERING", "SINGLE_SCATTERING", "NISHITA"):
        try:
            sky.sky_type = sky_type
            break
        except TypeError:
            continue
    sky.sun_disc = False  # the sun lamp below provides the one sun; two would mean two reflections
    sky.sun_elevation = math.radians(sun_elevation_deg)
    sky.sun_rotation = math.radians(sun_rotation_deg)
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Strength"].default_value = 0.18
    out = nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    sun = bpy.data.lights.new("Sun", "SUN")
    sun.energy = 3.0
    sun.color = (1.0, 0.62, 0.38)
    sun_obj = bpy.data.objects.new("Sun", sun)
    sun_obj.rotation_euler = (math.radians(90 - sun_elevation_deg), 0, math.radians(sun_rotation_deg + 90))
    bpy.context.collection.objects.link(sun_obj)


def animate_camera(mode, frames):
    cam_data = bpy.data.cameras.new("Camera")
    cam = bpy.data.objects.new("Camera", cam_data)
    bpy.context.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    cam_data.clip_end = 60000
    target = bpy.data.objects.new("Target", None)
    bpy.context.collection.objects.link(target)
    track = cam.constraints.new("TRACK_TO")
    track.target = target
    track.track_axis = "TRACK_NEGATIVE_Z"
    track.up_axis = "UP_Y"

    for f in range(1, frames + 1):
        t = (f - 1) / max(frames - 1, 1)
        ease = t * t * (3 - 2 * t)  # smoothstep: no sudden start or stop
        if mode == "orbit":
            a = math.radians(205 + 35 * ease)
            dist = 3600
            cam.location = (dist * math.cos(a), dist * math.sin(a), 260 + 120 * ease)
            target.location = (0, 0, MILE_M * 0.42)
            cam_data.lens = 35
        else:  # rise: start near the base, tilt up the shaft
            a = math.radians(250)
            # Start outside the city grid (blocks reach about 1,490 m out) so the lens is never inside a building.
            cam.location = (1750 * math.cos(a), 1750 * math.sin(a), 160 + 800 * ease)
            target.location = (0, 0, 300 + 1100 * ease)
            cam_data.lens = 28
        cam.keyframe_insert("location", frame=f)
        target.keyframe_insert("location", frame=f)
        cam_data.keyframe_insert("lens", frame=f)


def use_gpu(scene):
    """Render Cycles on the GPU: Metal on Apple Silicon (M1 to M4), CUDA/OptiX on NVIDIA."""
    prefs = bpy.context.preferences.addons["cycles"].preferences
    for backend in ("METAL", "OPTIX", "CUDA", "HIP", "ONEAPI"):
        try:
            prefs.compute_device_type = backend
        except TypeError:
            continue
        prefs.get_devices()
        gpus = [d for d in prefs.devices if d.type == backend]
        if gpus:
            for d in prefs.devices:
                d.use = d.type == backend
            scene.cycles.device = "GPU"
            print(f"Cycles on {backend}: {', '.join(d.name for d in gpus)}")
            return
    print("No supported GPU found; rendering on CPU")


def main():
    a = args()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    w, h = (int(v) for v in a.res.split("x"))
    scene.render.resolution_x, scene.render.resolution_y = w, h
    scene.render.fps = a.fps
    frames = max(1, round(a.seconds * a.fps))
    scene.frame_start, scene.frame_end = 1, frames

    body = material("M_Tower", (0.78, 0.66, 0.42), metallic=0.85, roughness=0.32)
    fin = material("M_Fin", (0.55, 0.48, 0.36), metallic=0.6, roughness=0.45)
    lights = material("M_Bands", (1.0, 0.85, 0.6), emission=((1.0, 0.78, 0.5), 6.0))
    blocks = window_material("M_City")
    ground = material("M_Ground", (0.025, 0.025, 0.028), roughness=0.95)
    water = material("M_Lake", (0.01, 0.02, 0.035), roughness=0.18)

    build_tower(body, fin, lights)
    build_city(blocks, ground, water)
    build_world()
    animate_camera(a.camera, frames)

    if a.engine.upper().startswith("EEVEE"):
        scene.render.engine = "BLENDER_EEVEE"
    else:
        scene.render.engine = "CYCLES"
        scene.cycles.samples = a.samples
        scene.cycles.use_denoising = True
        scene.cycles.device = "CPU"
        if a.engine.upper() == "CYCLES_GPU":
            use_gpu(scene)
    scene.view_settings.view_transform = "AgX"
    scene.view_settings.look = "AgX - Medium High Contrast"
    scene.render.image_settings.file_format = "PNG"

    wanted = [int(f) for f in a.frames.split(",")] if a.frames else range(1, frames + 1)
    for f in wanted:
        scene.frame_set(f)
        scene.render.filepath = f"{a.out}/{f:04d}.png"
        bpy.ops.render.render(write_still=True)
        print(f"rendered frame {f}/{frames}", flush=True)


main()
