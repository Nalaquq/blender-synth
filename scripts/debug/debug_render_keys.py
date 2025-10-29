import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Initialize
bproc.init()

# Load a simple model
import bpy
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

print(f"Loaded {len(mesh_objs)} mesh objects")

# Set category_id
for idx, obj in enumerate(mesh_objs):
    obj.set_cp("category_id", idx + 1)
    obj.set_location([0, 0, 0.5])
    print(f"Object: {obj.get_name()}, category_id: {obj.get_cp('category_id')}")

# Create camera
cam_pose = bproc.math.build_transformation_mat([0, -2, 1.5], [1.2, 0, 0])
bproc.camera.add_camera_pose(cam_pose)

# Enable outputs
bproc.renderer.enable_normals_output()
bproc.renderer.enable_depth_output(activate_antialiasing=False)
bproc.renderer.enable_segmentation_output(
    map_by=["instance"],
    default_values={"category_id": 0}
)

# Render
print("\nRendering...")
data = bproc.renderer.render()

# Print all keys in render data
print(f"\nRender data keys: {list(data.keys())}")

# Check each segmentation key
for key in data.keys():
    if 'seg' in key.lower():
        print(f"\n{key}:")
        seg = data[key][0]
        unique = np.unique(seg)
        print(f"  Shape: {seg.shape}")
        print(f"  Unique values: {unique}")
        print(f"  Non-zero pixels: {np.count_nonzero(seg)}")
