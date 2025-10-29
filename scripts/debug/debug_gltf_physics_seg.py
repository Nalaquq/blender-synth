import blenderproc as bproc
import numpy as np

# Test GLTF import + physics + segmentation
bproc.init()

# Import GLTF model
import bpy
existing = set(bpy.data.objects)
bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
new_objs = set(bpy.data.objects) - existing
mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']

print(f"Loaded {len(mesh_objs)} mesh objects from GLTF")

# Set category_id
for obj in mesh_objs:
    obj.set_cp("category_id", 1)
    print(f"Set category_id=1 on {obj.get_name()}")

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

# Check positions after physics
for obj in mesh_objs:
    loc = obj.get_location()
    cat_id = obj.get_cp("category_id") if obj.has_cp("category_id") else "None"
    print(f"After physics: {obj.get_name()} at {loc}, category_id={cat_id}")

# Create camera
cam_pose = bproc.math.build_transformation_mat([0, -2, 1.5], [1.2, 0, 0])
bproc.camera.add_camera_pose(cam_pose)

# Enable segmentation
bproc.renderer.enable_segmentation_output(
    map_by=["instance"],
    default_values={"category_id": 0}
)

# Render
print("\nRendering...")
data = bproc.renderer.render()

# Check segmentation
seg = data["instance_segmaps"][0]
unique = np.unique(seg)
print(f"\nSegmentation unique values: {unique}")
print(f"Non-zero pixels: {np.count_nonzero(seg)}")
