import blenderproc as bproc
# Diagnostic script to check what Blender can see

import bpy

print("=" * 70)
print("Blender GPU Diagnostic Information")
print("=" * 70)

try:
    prefs = bpy.context.preferences
    cycles_prefs = prefs.addons.get('cycles')

    if cycles_prefs is None:
        print("ERROR: Cycles addon not found")
    else:
        print(f"\nCurrent compute device type: {cycles_prefs.preferences.compute_device_type}")
        print("\nAvailable compute device types:")

        # Try all possible device types
        device_types = ['OPTIX', 'CUDA', 'HIP', 'METAL', 'ONEAPI', 'OPENCL']

        for device_type in device_types:
            try:
                cycles_prefs.preferences.compute_device_type = device_type
                cycles_prefs.preferences.get_devices()
                devices = cycles_prefs.preferences.devices

                print(f"\n  {device_type}:")
                if devices:
                    for device in devices:
                        print(f"    - {device.name} (Type: {device.type}, Use: {device.use})")
                else:
                    print(f"    No devices found")

            except Exception as e:
                print(f"    ERROR: {e}")

        print("\n" + "=" * 70)

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
