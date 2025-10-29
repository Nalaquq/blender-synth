import blenderproc as bproc
import numpy as np
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

# Initialize
bproc.init()

# Load a model and check its properties
import bpy
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

print(f"Loaded {len(mesh_objs)} mesh objects")

# Set category_id
for idx, obj in enumerate(mesh_objs):
    obj.set_cp("category_id", idx + 1)
    print(f"Object: {obj.get_name()}, category_id: {obj.get_cp('category_id')}")
    # Make sure it's visible
    obj.set_location([0, 0, 0.5])

# Create camera
cam_pose = bproc.math.build_transformation_mat([0, -2, 1.5], [1.2, 0, 0])
bproc.camera.add_camera_pose(cam_pose)

# Enable segmentation
bproc.renderer.enable_segmentation_output(
    map_by=["class", "instance"],
    default_values={"category_id": 0}
)

# Render
print("\nRendering...")
data = bproc.renderer.render()

# Check segmentation
if "instance_segmaps" in data:
    seg = data["instance_segmaps"][0]
    unique = np.unique(seg)
    print(f"\nSegmentation map unique values: {unique}")
    print(f"Segmentation map shape: {seg.shape}")
    print(f"Non-zero pixels: {np.count_nonzero(seg)}")
else:
    print("No instance_segmaps in render data!")

# Check all objects in scene
print("\nAll mesh objects in scene:")
for obj in bproc.object.get_all_mesh_objects():
    cat_id = obj.get_cp("category_id") if obj.has_cp("category_id") else "None"
    print(f"  {obj.get_name()}: category_id={cat_id}")
