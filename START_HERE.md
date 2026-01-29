# 🎮 GPU Watch - START HERE!

## ✅ WORKING VERSION FOR YOUR SYSTEM

Your system has been detected with:
- **NVIDIA GeForce RTX 4050 Laptop GPU**
- **AMD Radeon 780M Graphics** (integrated)
- **NVIDIA Driver**: 581.08
- **nvidia-smi**: Working perfectly!

## 🚀 QUICK START (Use This!)

### **Double-click this file to run:**
```
run_windows.bat
```

Or run in PowerShell:
```powershell
python gpu_watch_windows.py
```

## 📊 What You'll See

A beautiful real-time GPU monitor with:
- GPU usage with colored progress bars
- Memory usage and temperature
- Power consumption
- Clock speeds (GPU & Memory)
- Fan speed
- 60-point sparkline history graphs
- Active GPU processes
- Zero flickering!

Press `Ctrl+C` to exit

## 🎯 Why gpu_watch_windows.py?

The original `gpu_watch.py` and `gpu_watch_lite.py` require the NVML Python library
which has compatibility issues on your system. The Windows version uses `nvidia-smi`
directly, which works perfectly!

## 📁 Files in This Folder

**WORKING FILES** (Use these):
- `gpu_watch_windows.py` - The GPU monitor that works on your system
- `run_windows.bat` - Double-click to launch
- `check_gpu.py` - Diagnostic tool
- `check_gpu.bat` - Run diagnostics

**OTHER FILES** (NVML-based, won't work without fixes):
- `gpu_watch.py` - Original version (needs NVML fix)
- `gpu_watch_lite.py` - Lite version (needs NVML fix)
- `gpu_watch.ps1` - Your old PowerShell script

**FIX SCRIPTS** (If you want to try fixing NVML):
- `fix_nvml.py` - Simple NVML path fixer
- `fix_nvml_advanced.py` - Advanced NVML fixer
- May require running as Administrator

## 🔧 Troubleshooting

### If gpu_watch_windows.py doesn't work:

1. **Make sure NVIDIA drivers are installed**
   ```powershell
   nvidia-smi
   ```
   Should show your GPU info

2. **Check Python version**
   ```powershell
   python --version
   ```
   Should be Python 3.8 or higher

3. **Reinstall dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

### If you see errors:

Run the diagnostic:
```powershell
python check_gpu.py
```

## 💡 Tips

- Works best in **Windows Terminal** (download from Microsoft Store)
- Regular PowerShell works too
- Don't use old CMD.exe (limited colors)
- The monitor refreshes every 0.5 seconds
- GPU history shows last 60 data points

## 🎨 Customization

Edit `gpu_watch_windows.py` to change:
- **Refresh rate**: Line ~310 - `time.sleep(0.5)`
- **History length**: Line ~19 - `self.history_size = 60`
- **Bar width**: Line ~78 - `width=40`
- **Colors**: Search for color names and change them

## 📝 What's Different from nvidia-smi?

| Feature | nvidia-smi | GPU Watch Windows |
|---------|-----------|-------------------|
| Auto-refresh | No | Yes (2x per second) |
| Flickering | Yes | No flickering |
| History graphs | No | 60-point sparklines |
| Colors | Basic | Full color coding |
| UI | Plain text | Beautiful panels |
| Layout | Static | Dynamic |

## ⭐ Enjoy!

Your GPU monitoring experience just got a MASSIVE upgrade!

Keep it running in a terminal while gaming or working to monitor your GPU in real-time.

---

**Made with nvidia-smi + Python + Rich**

For questions or issues, check the diagnostic with `python check_gpu.py`
