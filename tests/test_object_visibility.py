import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from blender_synth.pipeline.config import GenerationConfig, RenderConfig, PhysicsConfig
from blender_synth.core.scene import SceneManager
from blender_synth.core.camera import CameraOrbit
from blender_synth.core.physics import PhysicsSimulator

# Initialize
render_config = RenderConfig(samples=64, use_gpu=False)
camera_config = GenerationConfig.model_fields['camera'].default_factory()
physics_config = PhysicsConfig()
background_config = GenerationConfig.model_fields['background'].default_factory()

scene_manager = SceneManager(render_config, background_config)
scene_manager.initialize()

camera_orbit = CameraOrbit(camera_config)
camera_orbit.setup_camera()

# Enable outputs  
bproc.renderer.enable_normals_output()
bproc.renderer.enable_depth_output(activate_antialiasing=False)
bproc.renderer.enable_segmentation_output(
    map_by=["instance"],
    default_values={"category_id": 0}
)

surface = scene_manager.create_drawer_surface()

# Load object
import bpy
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

for obj in mesh_objs:
    obj.set_cp("category_id", 1)

# Run physics
physics_sim = PhysicsSimulator(physics_config)
physics_sim.drop_objects(mesh_objs, surface)

# Set camera
scene_center = np.array([0, 0, 0.0])
camera_orbit.generate_orbit_poses(scene_center)
camera_orbit.set_random_pose()

# Check camera info
import bpy as blender
camera = blender.context.scene.camera
print(f"Camera location: {camera.location}")
print(f"Camera rotation: {camera.rotation_euler}")

# Check object visibility
for obj in mesh_objs:
    print(f"\nObject: {obj.get_name()}")
    print(f"  Location: {obj.get_location()}")
    print(f"  Scale: {obj.get_scale()}")
    bbox = obj.get_bound_box()
    print(f"  Bounding box size: {np.ptp(bbox, axis=0)}")

# Render
print("\nRendering...")
data = bproc.renderer.render()

# Save image to inspect
from PIL import Image
image_data = data["colors"][0]
if image_data.dtype == np.float32 or image_data.dtype == np.float64:
    image_data = (image_data * 255).astype(np.uint8)
Image.fromarray(image_data).save("/tmp/test_visibility.jpg")
print("Saved image to /tmp/test_visibility.jpg")

# Check depth to see if object is in frame
depth_data = data["depth"][0]
print(f"\nDepth stats:")
print(f"  Min depth: {np.min(depth_data)}")
print(f"  Max depth: {np.max(depth_data)}")
print(f"  Mean depth: {np.mean(depth_data)}")
print(f"  Non-inf pixels: {np.sum(np.isfinite(depth_data))}")

# Check if object pixels exist in depth map
finite_depth = depth_data[np.isfinite(depth_data)]
if len(finite_depth) > 0:
    print(f"  Finite depth range: {np.min(finite_depth)} to {np.max(finite_depth)}")
    # Object should be around z=0.02, camera is ~1-1.5m away
    object_depth_pixels = np.sum((finite_depth > 0.5) & (finite_depth < 2.0))
    print(f"  Pixels at reasonable object distance (0.5-2.0m): {object_depth_pixels}")

# Check segmentation
seg_data = data.get("instance_segmaps", [None])[0]
unique = np.unique(seg_data)
print(f"\nSegmentation unique values: {unique}")
