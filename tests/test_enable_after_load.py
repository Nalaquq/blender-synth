import blenderproc as bproc
import numpy as np

print("=== Testing enable_segmentation AFTER loading objects ===")
bproc.init()

# Create camera once
cam_pose = bproc.math.build_transformation_mat([0, -2, 1.5], [1.2, 0, 0])
bproc.camera.add_camera_pose(cam_pose)

for i in range(2):
    print(f"\n=== Render cycle {i+1} ===")
    
    # Clear all mesh objects
    for obj in bproc.object.get_all_mesh_objects():
        obj.delete()
    
    # Create surface
    plane = bproc.object.create_primitive("PLANE", scale=[2, 2, 1])
    plane.set_location([0, 0, -0.01])
    plane.set_cp("category_id", 0)
    
    # Load object
    import bpy
    existing = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath="./models/awl/Awl_75818.glb")
    new_objs = set(bpy.data.objects) - existing
    mesh_objs = [bproc.types.MeshObject(obj) for obj in new_objs if obj.type == 'MESH']
    
    for obj in mesh_objs:
        obj.set_cp("category_id", 1)
        obj.set_location([0, 0, 0.5])
    
    # Enable segmentation AFTER loading objects (on each cycle)
    try:
        bproc.renderer.enable_segmentation_output(map_by=["instance"], default_values={"category_id": 0})
        print("Successfully called enable_segmentation_output")
    except Exception as e:
        print(f"Error calling enable_segmentation_output: {e}")
    
    # Render
    print(f"Rendering...")
    data = bproc.renderer.render()
    
    # Check segmentation
    seg = data.get("instance_segmaps", [None])[0]
    if seg is not None:
        unique = np.unique(seg)
        print(f"Segmentation unique values: {unique}")
        print(f"Non-zero pixels: {np.count_nonzero(seg)}")
        
        if len(unique) > 1:
            print("✓ Segmentation works!")
        else:
            print("✗ Segmentation is empty")
    else:
        print("No segmentation data")
