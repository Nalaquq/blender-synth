import blenderproc as bproc
import numpy as np

# Test 1: WITHOUT physics
print("=== TEST 1: Object WITHOUT physics ===")
bproc.init()

import bpy
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

for obj in mesh_objs:
    obj.set_cp("category_id", 1)
    obj.set_location([0, 0, 0.5])
    print(f"Object: {obj.get_name()}, category_id={obj.get_cp('category_id')}")
    print(f"  Hide viewport: {obj.blender_obj.hide_viewport}")
    print(f"  Hide render: {obj.blender_obj.hide_render}")

cam_pose = bproc.math.build_transformation_mat([0, -2, 1.5], [1.2, 0, 0])
bproc.camera.add_camera_pose(cam_pose)

bproc.renderer.enable_segmentation_output(map_by=["instance"], default_values={"category_id": 0})
data1 = bproc.renderer.render()

seg1 = data1.get("instance_segmaps", [None])[0]
unique1 = np.unique(seg1)
print(f"Segmentation unique values: {unique1}")
print(f"Non-zero pixels: {np.count_nonzero(seg1)}\n")

# Clean up
bproc.clean_up()

# Test 2: WITH physics
print("=== TEST 2: Object WITH physics ===")
bproc.init()

# Create surface
plane = bproc.object.create_primitive("PLANE", scale=[2, 2, 1])
plane.set_location([0, 0, -0.01])
plane.set_cp("category_id", 0)

plane.enable_rigidbody(active=False, collision_shape="MESH", collision_margin=0.001)

# Load object
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

for obj in mesh_objs:
    obj.set_cp("category_id", 1)
    obj.set_location([0, 0, 0.3])
    
    # Enable physics
    obj.enable_rigidbody(active=True, collision_shape="CONVEX_HULL", friction=0.5)
    
    print(f"Object: {obj.get_name()}, category_id={obj.get_cp('category_id')}")
    print(f"  Before physics - Hide viewport: {obj.blender_obj.hide_viewport}")
    print(f"  Before physics - Hide render: {obj.blender_obj.hide_render}")

# Run physics
bproc.object.simulate_physics_and_fix_final_poses(
    min_simulation_time=4.0,
    max_simulation_time=6.0,
    check_object_interval=1.0
)

# Check after physics
for obj in mesh_objs:
    print(f"  After physics - Hide viewport: {obj.blender_obj.hide_viewport}")
    print(f"  After physics - Hide render: {obj.blender_obj.hide_render}")
    print(f"  After physics - location: {obj.get_location()}")

cam_pose = bproc.math.build_transformation_mat([0, -2, 1.5], [1.2, 0, 0])
bproc.camera.add_camera_pose(cam_pose)

bproc.renderer.enable_segmentation_output(map_by=["instance"], default_values={"category_id": 0})
data2 = bproc.renderer.render()

seg2 = data2.get("instance_segmaps", [None])[0]
unique2 = np.unique(seg2)
print(f"Segmentation unique values: {unique2}")
print(f"Non-zero pixels: {np.count_nonzero(seg2)}")
