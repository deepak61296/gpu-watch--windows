"""
Fix NVML Path - Helps Python find the NVIDIA NVML DLL
"""

import os
import sys
from pathlib import Path

print("="*60)
print("NVML PATH FIXER")
print("="*60)

# Common NVML DLL locations
possible_paths = [
    r"C:\Windows\System32\nvml.dll",
    r"C:\Program Files\NVIDIA Corporation\NVSMI\nvml.dll",
    r"C:\Windows\SysWOW64\nvml.dll",
]

# Check NVIDIA driver paths
nvidia_paths = [
    r"C:\Program Files\NVIDIA Corporation\NVSMI",
    r"C:\Windows\System32",
    r"C:\Windows\SysWOW64",
]

print("\nSearching for NVML DLL...")
found_dll = None

for path in possible_paths:
    if os.path.exists(path):
        print(f"FOUND: {path}")
        found_dll = path
        break
    else:
        print(f"Not found: {path}")

if not found_dll:
    print("\n" + "="*60)
    print("Searching in common NVIDIA directories...")
    for nvidia_path in nvidia_paths:
        if os.path.exists(nvidia_path):
            print(f"\nChecking: {nvidia_path}")
            for file in os.listdir(nvidia_path):
                if 'nvml' in file.lower() and file.endswith('.dll'):
                    found_dll = os.path.join(nvidia_path, file)
                    print(f"FOUND: {found_dll}")
                    break

if found_dll:
    print("\n" + "="*60)
    print("SUCCESS - NVML DLL Found!")
    print("="*60)
    print(f"Location: {found_dll}")

    # Set environment variable
    dll_dir = os.path.dirname(found_dll)
    print(f"\nDLL Directory: {dll_dir}")

    # Try to fix it by adding to PATH
    print("\nAttempting to add to PATH and test...")

    # Add to current process PATH
    os.environ['PATH'] = dll_dir + os.pathsep + os.environ.get('PATH', '')

    # Try importing pynvml now
    try:
        import pynvml
        pynvml.nvmlInit()
        print("\nSUCCESS! NVML is now working!")

        gpu_count = pynvml.nvmlDeviceGetCount()
        print(f"Detected {gpu_count} NVIDIA GPU(s)")

        for i in range(gpu_count):
            handle = pynvml.nvmlDeviceGetHandleByIndex(i)
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')
            print(f"  GPU {i}: {name}")

        pynvml.nvmlShutdown()

        print("\n" + "="*60)
        print("PERMANENT FIX:")
        print("="*60)
        print("To make this permanent, add this to your PATH:")
        print(f"\n  {dll_dir}")
        print("\nOr run GPU Watch with this batch file:")

        # Create a fixed launcher
        batch_content = f"""@echo off
set PATH={dll_dir};%PATH%
python gpu_watch.py
pause
"""
        with open('run_gpu_watch_FIXED.bat', 'w') as f:
            f.write(batch_content)

        print("\nCreated: run_gpu_watch_FIXED.bat")
        print("Use this to launch GPU Watch!")

    except Exception as e:
        print(f"\nStill failed: {e}")
        print("\nTry running PowerShell as Administrator and run this script again.")

else:
    print("\n" + "="*60)
    print("ERROR - NVML DLL NOT FOUND")
    print("="*60)
    print("\nThe NVML library is missing from your system.")
    print("\nSolutions:")
    print("1. Reinstall NVIDIA drivers from:")
    print("   https://www.nvidia.com/Download/index.aspx")
    print("2. Make sure to do a CLEAN install")
    print("3. Restart your computer after installation")

print("\n" + "="*60)
