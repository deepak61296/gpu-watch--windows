"""
Advanced NVML Fix - Forces Python to load the correct NVML DLL
"""

import os
import sys
import ctypes
from pathlib import Path

print("="*70)
print("ADVANCED NVML PATH FIXER")
print("="*70)

# Possible DLL locations
dll_paths = [
    r"C:\Windows\System32\nvml.dll",
    r"C:\Program Files\NVIDIA Corporation\NVSMI\nvml.dll",
    r"C:\Windows\SysWOW64\nvml.dll",
]

print("\nSearching for nvml.dll...")
found_dll = None

for dll_path in dll_paths:
    if os.path.exists(dll_path):
        print(f"  Found: {dll_path}")
        try:
            # Try to load the DLL directly
            lib = ctypes.CDLL(dll_path)
            print(f"  -> Successfully loaded!")
            found_dll = dll_path
            break
        except Exception as e:
            print(f"  -> Failed to load: {e}")
    else:
        print(f"  Not found: {dll_path}")

if found_dll:
    print(f"\n{'='*70}")
    print(f"SUCCESS - NVML DLL found and loadable: {found_dll}")
    print(f"{'='*70}")

    # Now patch pynvml to use this DLL
    print("\nPatching pynvml to use the correct DLL...")

    # Set environment variable before importing
    os.environ['NVML_DLL_PATH'] = found_dll
    dll_dir = os.path.dirname(found_dll)
    os.environ['PATH'] = dll_dir + os.pathsep + os.environ.get('PATH', '')

    # Try importing and monkey-patching pynvml
    try:
        import pynvml

        # Force pynvml to use our DLL path
        if hasattr(pynvml, '_nvmlLib_refcount'):
            pynvml._nvmlLib_refcount = None

        # Monkey patch the DLL loading
        original_load = pynvml._LoadNvmlLibrary if hasattr(pynvml, '_LoadNvmlLibrary') else None

        def _loadNvmlLibrary():
            try:
                return ctypes.CDLL(found_dll)
            except:
                # Fallback to original if it exists
                if original_load:
                    return original_load()
                raise

        if hasattr(pynvml, '_LoadNvmlLibrary'):
            pynvml._LoadNvmlLibrary = _loadNvmlLibrary

        # Try to initialize
        pynvml.nvmlInit()
        print("SUCCESS! NVML initialized!")

        gpu_count = pynvml.nvmlDeviceGetCount()
        print(f"\nDetected {gpu_count} NVIDIA GPU(s):")

        for i in range(gpu_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            print(f"  GPU {i}: {name}")

        pynvml.nvmlShutdown()

        # Create a wrapper script
        print(f"\n{'='*70}")
        print("Creating patched GPU Watch launcher...")
        print(f"{'='*70}")

        wrapper_code = f'''"""
GPU Watch with NVML Path Fix
"""
import os
import sys
import ctypes

# Force load the correct NVML DLL
os.environ['PATH'] = r"{dll_dir}" + os.pathsep + os.environ.get('PATH', '')

try:
    _nvml_dll = ctypes.CDLL(r"{found_dll}")
except Exception as e:
    print(f"Error loading NVML DLL: {{e}}")
    print("Try running as Administrator")
    input("Press Enter to exit...")
    sys.exit(1)

# Patch pynvml before importing
import pynvml

def _custom_load():
    return _nvml_dll

if hasattr(pynvml, '_LoadNvmlLibrary'):
    pynvml._LoadNvmlLibrary = _custom_load

# Now run the main app
if __name__ == "__main__":
    from gpu_watch import GPUWatchApp
    app = GPUWatchApp()
    app.run()
'''

        with open('gpu_watch_FIXED.py', 'w', encoding='utf-8') as f:
            f.write(wrapper_code)

        print("\nCreated: gpu_watch_FIXED.py")

        # Create batch file
        batch_content = f'''@echo off
set PATH={dll_dir};%PATH%
python gpu_watch_FIXED.py
pause
'''
        with open('run_gpu_watch_FIXED.bat', 'w') as f:
            f.write(batch_content)

        print("Created: run_gpu_watch_FIXED.bat")

        # Also create a lite version
        wrapper_lite = f'''"""
GPU Watch Lite with NVML Path Fix
"""
import os
import sys
import ctypes

# Force load the correct NVML DLL
os.environ['PATH'] = r"{dll_dir}" + os.pathsep + os.environ.get('PATH', '')

try:
    _nvml_dll = ctypes.CDLL(r"{found_dll}")
except Exception as e:
    print(f"Error loading NVML DLL: {{e}}")
    print("Try running as Administrator")
    input("Press Enter to exit...")
    sys.exit(1)

# Patch pynvml before importing
import pynvml

def _custom_load():
    return _nvml_dll

if hasattr(pynvml, '_LoadNvmlLibrary'):
    pynvml._LoadNvmlLibrary = _custom_load

# Now run the main app
if __name__ == "__main__":
    from gpu_watch_lite import GPUMonitor
    monitor = GPUMonitor()
    monitor.run()
'''

        with open('gpu_watch_lite_FIXED.py', 'w', encoding='utf-8') as f:
            f.write(wrapper_lite)

        print("Created: gpu_watch_lite_FIXED.py")

        batch_lite = f'''@echo off
set PATH={dll_dir};%PATH%
python gpu_watch_lite_FIXED.py
pause
'''
        with open('run_gpu_watch_lite_FIXED.bat', 'w') as f:
            f.write(batch_lite)

        print("Created: run_gpu_watch_lite_FIXED.bat")

        print(f"\n{'='*70}")
        print("FIX COMPLETE!")
        print(f"{'='*70}")
        print("\nTo run GPU Watch, use ONE of these:")
        print("  1. Double-click: run_gpu_watch_FIXED.bat (Full version)")
        print("  2. Double-click: run_gpu_watch_lite_FIXED.bat (Lite version)")
        print("  3. Or run: python gpu_watch_FIXED.py")
        print(f"\n{'='*70}")

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

        print("\n" + "="*70)
        print("ALTERNATIVE SOLUTION")
        print("="*70)
        print("\n1. Try running PowerShell as Administrator")
        print("2. Run: python fix_nvml_advanced.py")
        print("\nOr reinstall NVIDIA drivers:")
        print("https://www.nvidia.com/Download/index.aspx")

else:
    print("\n" + "="*70)
    print("ERROR - nvml.dll not found")
    print("="*70)
    print("\nReinstall NVIDIA drivers from:")
    print("https://www.nvidia.com/Download/index.aspx")
