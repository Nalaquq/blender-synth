import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from blender_synth.core.camera import CameraOrbit
from blender_synth.pipeline.config import CameraConfig

# Test if camera can actually see the objects
bproc.init()

# Import GLTF model
import bpy
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

# Set category_id
for obj in mesh_objs:
    obj.set_cp("category_id", 1)

# Create table
table = bproc.object.create_primitive("PLANE", scale=[2, 2, 1])
table.set_location([0, 0, -0.01])
table.set_cp("category_id", 0)
table.enable_rigidbody(active=False, collision_shape="MESH")

# Drop object with physics
for obj in mesh_objs:
    obj.set_location([0, 0, 0.3])
    obj.enable_rigidbody(active=True, collision_shape="CONVEX_HULL")

# Run physics
bproc.object.simulate_physics_and_fix_final_poses(
    min_simulation_time=4.0,
    max_simulation_time=6.0,
    check_object_interval=1.0
)

# Adjust position like pipeline does
for obj in mesh_objs:
    loc = obj.get_location()
    if loc[2] < 0.01:
        obj.set_location([loc[0], loc[1], 0.02])
    loc = obj.get_location()
    print(f"Object {obj.get_name()} at {loc}")

# Use the SAME camera setup as pipeline
camera_config = CameraConfig()
camera_orbit = CameraOrbit(camera_config)
camera_orbit.setup_camera()

# Generate poses aimed at z=0.0 like pipeline
scene_center = np.array([0, 0, 0.0])
camera_orbit.generate_orbit_poses(scene_center)
camera_orbit.set_random_pose()

# Get camera info
cam = bpy.context.scene.camera
print(f"\nCamera location: {cam.location}")
print(f"Camera rotation: {cam.rotation_euler}")

# Enable segmentation AFTER objects are positioned
bproc.renderer.enable_segmentation_output(
    map_by=["instance"],
    default_values={"category_id": 0}
)

# Render
print("\nRendering with pipeline camera setup...")
data = bproc.renderer.render()

# Check segmentation
seg = data["instance_segmaps"][0]
unique = np.unique(seg)
print(f"\nSegmentation unique values: {unique}")
print(f"Non-zero pixels: {np.count_nonzero(seg)}")

# Save image for visual inspection
from PIL import Image
img = Image.fromarray((data["colors"][0] * 255).astype(np.uint8))
img.save("/tmp/test_camera_view.jpg")
print("Saved image to /tmp/test_camera_view.jpg")
