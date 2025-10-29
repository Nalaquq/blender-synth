import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from blender_synth.pipeline.config import GenerationConfig, RenderConfig, PhysicsConfig
from blender_synth.core.scene import SceneManager
from blender_synth.core.camera import CameraOrbit
from blender_synth.core.physics import PhysicsSimulator

# Initialize scene manager
render_config = RenderConfig(samples=64, use_gpu=False)
camera_config = GenerationConfig.model_fields['camera'].default_factory()
physics_config = PhysicsConfig()
background_config = GenerationConfig.model_fields['background'].default_factory()

scene_manager = SceneManager(render_config, background_config)
scene_manager.initialize()

camera_orbit = CameraOrbit(camera_config)
camera_orbit.setup_camera()

# Enable outputs with BOTH class and instance (instead of just instance)
bproc.renderer.enable_normals_output()
bproc.renderer.enable_depth_output(activate_antialiasing=False)
bproc.renderer.enable_segmentation_output(
    map_by=["class", "instance"],  # <-- CHANGED from ["instance"] to ["class", "instance"]
    default_values={"category_id": 0}
)

# Create surface
surface = scene_manager.create_drawer_surface()

# Load object
import bpy
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

# Set properties
for obj in mesh_objs:
    obj.set_cp("class_name", "awl")
    obj.set_cp("class_id", 3)
    obj.set_cp("category_id", 4)

# Run physics
physics_sim = PhysicsSimulator(physics_config)
physics_sim.drop_objects(mesh_objs, surface)

# Set camera
scene_center = np.array([0, 0, 0.0])
camera_orbit.generate_orbit_poses(scene_center)
camera_orbit.set_random_pose()

# Render
print("Rendering with map_by=['class', 'instance']...")
data = bproc.renderer.render()

# Check segmentation
seg_data = data.get("instance_segmaps", [None])[0]
if seg_data is not None:
    unique_instances = np.unique(seg_data)
    print(f"Unique values in segmentation: {unique_instances}")
    print(f"Non-zero pixels: {np.count_nonzero(seg_data)}")
    
    unique_nonzero = unique_instances[unique_instances > 0]
    print(f"Non-background instances: {unique_nonzero}")
    
    if len(unique_nonzero) > 0:
        print("\n✓ SUCCESS: Segmentation captured the object!")
    else:
        print("\n✗ FAIL: Segmentation is still empty")
else:
    print("✗ FAIL: No instance_segmaps in render data")
