import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from blender_synth.pipeline.config import GenerationConfig, RenderConfig, PhysicsConfig
from blender_synth.core.scene import SceneManager
from blender_synth.core.camera import CameraOrbit
from blender_synth.core.physics import PhysicsSimulator

# Initialize scene manager like the generator does
render_config = RenderConfig(samples=64, use_gpu=False)  # CPU for faster debug
camera_config = GenerationConfig.model_fields['camera'].default_factory()
physics_config = PhysicsConfig()
background_config = GenerationConfig.model_fields['background'].default_factory()

scene_manager = SceneManager(render_config, background_config)
scene_manager.initialize()

camera_orbit = CameraOrbit(camera_config)
camera_orbit.setup_camera()

# Enable outputs BEFORE creating objects (like in generator.py)
bproc.renderer.enable_normals_output()
bproc.renderer.enable_depth_output(activate_antialiasing=False)
bproc.renderer.enable_segmentation_output(
    map_by=["instance"],
    default_values={"category_id": 0}
)

# Create surface
surface = scene_manager.create_drawer_surface()
print(f"Surface created: {surface.get_name()}, category_id={surface.get_cp('category_id') if surface.has_cp('category_id') else 'None'}")

# Load object
import bpy
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

print(f"\nLoaded {len(mesh_objs)} objects")

# Set properties like ModelLoader does
for obj in mesh_objs:
    obj.set_cp("class_name", "awl")
    obj.set_cp("class_id", 3)
    obj.set_cp("category_id", 4)  # class_idx + 1
    print(f"Object: {obj.get_name()}, class_id={obj.get_cp('class_id')}, category_id={obj.get_cp('category_id')}")

# Run physics like the generator does
physics_sim = PhysicsSimulator(physics_config)
physics_sim.drop_objects(mesh_objs, surface)

# Set camera
scene_center = np.array([0, 0, 0.0])
camera_orbit.generate_orbit_poses(scene_center)
camera_orbit.set_random_pose()

# Check objects before rendering
print("\n=== Before Rendering ===")
all_objects = bproc.object.get_all_mesh_objects()
print(f"Total mesh objects in scene: {len(all_objects)}")
for obj in all_objects:
    cat_id = obj.get_cp("category_id") if obj.has_cp("category_id") else "None"
    class_id = obj.get_cp("class_id") if obj.has_cp("class_id") else "None"
    print(f"  {obj.get_name()}: class_id={class_id}, category_id={cat_id}, location={obj.get_location()}")

# Render
print("\n=== Rendering ===")
data = bproc.renderer.render()

# Check segmentation
print("\n=== Segmentation Results ===")
print(f"Render data keys: {list(data.keys())}")

seg_data = data.get("instance_segmaps", [None])[0]
if seg_data is not None:
    unique_instances = np.unique(seg_data)
    print(f"Unique values in segmentation: {unique_instances}")
    print(f"Non-zero pixels: {np.count_nonzero(seg_data)}")
    print(f"Segmentation shape: {seg_data.shape}")
    
    # Check which instance IDs are present
    unique_nonzero = unique_instances[unique_instances > 0]
    print(f"Non-background instances: {unique_nonzero}")
else:
    print("No instance_segmaps in render data!")

# Also check instance_attribute_maps
if "instance_attribute_maps" in data:
    attr_map = data["instance_attribute_maps"][0]
    print(f"\nInstance attribute map unique values: {np.unique(attr_map)}")
