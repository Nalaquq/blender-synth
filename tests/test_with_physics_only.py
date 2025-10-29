import blenderproc as bproc
import numpy as np

print("=== Testing object WITH physics simulation ===")
bproc.init()

import bpy

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
    
    print(f"Object: {obj.get_name()}, category_id={obj.get_cp('category_id')}")
    print(f"  BEFORE physics:")
    print(f"    Hide viewport: {obj.blender_obj.hide_viewport}")
    print(f"    Hide render: {obj.blender_obj.hide_render}")
    
    # Enable physics
    obj.enable_rigidbody(active=True, collision_shape="CONVEX_HULL", friction=0.5)

# Run physics
print("\nRunning physics simulation...")
bproc.object.simulate_physics_and_fix_final_poses(
    min_simulation_time=4.0,
    max_simulation_time=6.0,
    check_object_interval=1.0
)

# Check after physics
print("\nAfter physics simulation:")
for obj in mesh_objs:
    print(f"Object: {obj.get_name()}")
    print(f"  Hide viewport: {obj.blender_obj.hide_viewport}")
    print(f"  Hide render: {obj.blender_obj.hide_render}")
    print(f"  Location: {obj.get_location()}")
    print(f"  category_id: {obj.get_cp('category_id')}")

# Set up camera
cam_pose = bproc.math.build_transformation_mat([0, -2, 1.5], [1.2, 0, 0])
bproc.camera.add_camera_pose(cam_pose)

# Enable segmentation
bproc.renderer.enable_segmentation_output(map_by=["instance"], default_values={"category_id": 0})

# Render
print("\nRendering...")
data = bproc.renderer.render()

# Check segmentation
seg = data.get("instance_segmaps", [None])[0]
unique = np.unique(seg)
print(f"\nSegmentation results:")
print(f"  Unique values: {unique}")
print(f"  Non-zero pixels: {np.count_nonzero(seg)}")

if np.count_nonzero(seg) > 0:
    print("\n✓ SUCCESS: Segmentation captured the object after physics!")
else:
    print("\n✗ FAIL: Segmentation is empty after physics")
