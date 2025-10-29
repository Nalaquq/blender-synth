import blenderproc as bproc
import numpy as np

# Initialize
bproc.init()

# Load object
import bpy
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

# Set category_id
for idx, obj in enumerate(mesh_objs):
    obj.set_cp("category_id", idx + 1)
    obj.set_location([0, 0, 0.5])
    print(f"Object: {obj.get_name()}, category_id: {obj.get_cp('category_id')}")

# Camera
cam_pose = bproc.math.build_transformation_mat([0, -2, 1.5], [1.2, 0, 0])
bproc.camera.add_camera_pose(cam_pose)

# Test 1: map_by=["instance"] only
print("\n=== Test 1: map_by=['instance'] ===")
bproc.renderer.enable_segmentation_output(
    map_by=["instance"],
    default_values={"category_id": 0}
)
data1 = bproc.renderer.render()
seg1 = data1.get("instance_segmaps", [None])[0]
if seg1 is not None:
    unique1 = np.unique(seg1)
    print(f"Unique values: {unique1}, Non-zero: {np.count_nonzero(seg1)}")
else:
    print("No segmentation data")

# Clear and try again with both class and instance
print("\n=== Test 2: map_by=['class', 'instance'] ===")

# Re-init to clear previous segmentation setup
bproc.clean_up()
bproc.init()

# Reload
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

for idx, obj in enumerate(mesh_objs):
    obj.set_cp("category_id", idx + 1)
    obj.set_location([0, 0, 0.5])

cam_pose = bproc.math.build_transformation_mat([0, -2, 1.5], [1.2, 0, 0])
bproc.camera.add_camera_pose(cam_pose)

bproc.renderer.enable_segmentation_output(
    map_by=["class", "instance"],
    default_values={"category_id": 0}
)

data2 = bproc.renderer.render()
seg2 = data2.get("instance_segmaps", [None])[0]
if seg2 is not None:
    unique2 = np.unique(seg2)
    print(f"Unique values: {unique2}, Non-zero: {np.count_nonzero(seg2)}")
else:
    print("No segmentation data")
