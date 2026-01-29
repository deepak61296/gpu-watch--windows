# 🎮 GPU Watch - Amazing Terminal GPU Monitor

A **stunning, professional-grade GPU monitoring terminal application** for Windows that makes nvidia-smi look ancient!

## ✨ Features

### 🚀 Way Better Than nvidia-smi
- **Zero flickering** - Smooth, professional async updates
- **Real-time sparkline graphs** - See GPU usage history at a glance
- **Beautiful color-coded metrics** - Red/Yellow/Green based on usage
- **Progress bars for everything** - GPU, Memory, Power, Temperature
- **Multi-GPU support** - Monitor all your GPUs simultaneously
- **Process monitoring** - See what's using your GPU
- **Live clock speeds** - GPU and Memory clocks in real-time
- **Fan speed monitoring** - Keep track of cooling
- **Power consumption** - Track watts in real-time

### 🎨 Visual Features
- Gorgeous terminal UI with panels and colors
- Real-time sparkline charts (60-point history)
- Color-coded temperature warnings
- Dynamic progress bars
- Emoji indicators for quick status
- Professional panel layouts

## 🔧 Installation

### Prerequisites
- Windows 10/11
- Python 3.8 or higher
- NVIDIA GPU with drivers installed

### Quick Setup

1. **Double-click** `setup_gpu_watch.bat` to install dependencies

   OR manually:
   ```cmd
   pip install -r requirements.txt
   ```

## 🚀 Usage

### Two versions available:

#### 1. **GPU Watch (Full Version)** - Textual-based TUI
```cmd
python gpu_watch.py
```
- Best experience with full interactive UI
- Keyboard shortcuts (q=quit, r=refresh)
- Modern async terminal framework

#### 2. **GPU Watch Lite** - Rich-based (Lighter)
```cmd
python gpu_watch_lite.py
```
- Lighter weight, uses only Rich library
- Simpler but still beautiful
- Great for lower-end terminals

### Quick Launch
Double-click `run_gpu_watch.bat` for instant monitoring!

## ⌨️ Keyboard Shortcuts (Full Version)

- `q` - Quit
- `r` - Force refresh
- `Ctrl+C` - Exit

## 📊 What You'll See

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 🎮 GPU 0: NVIDIA GeForce RTX 4090            ┃
┠───────────────────────────────────────────────┨
┃ GPU Usage:      ████████████░░░ 65%          ┃
┃ Memory:         ████████░░░░░░░ 8.2/24.0 GB  ┃
┃ Temperature:    🌡️ 72°C                      ┃
┃ Power:          ███████░░░░░░░░ 285/450 W    ┃
┃ GPU Clock:      ⚡ 2520 MHz                   ┃
┃ Memory Clock:   💾 9501 MHz                   ┃
┃ Fan Speed:      🌀 55%                        ┃
┃                                               ┃
┃ GPU History:    ▃▄▅▆▇█▇▆▅▄▃▃▄▅▆▇█▇▆▅▄        ┃
┃ Mem History:    ▄▄▅▅▅▅▄▄▄▅▅▅▆▆▆▅▄▄▃▃        ┃
┃ Temp History:   ▅▅▅▆▆▆▆▅▅▅▅▆▆▇▇▆▆▅▅▅        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
```

## 🎯 Why This is Better

| Feature | nvidia-smi | GPU Watch |
|---------|-----------|-----------|
| Updates | Manual refresh | Real-time auto-update |
| Flickering | Yes, lots | Zero flickering ✨ |
| History | None | 60-point sparklines |
| Colors | Minimal | Full color coding |
| UI | Plain text | Beautiful panels |
| Processes | Basic list | Formatted table |
| Graphs | None | Real-time sparklines |
| Layout | Static | Dynamic responsive |
| Experience | 1990s | 2026 🚀 |

## 🔍 Troubleshooting

### "Failed to initialize NVML"
- Make sure NVIDIA drivers are installed
- Run as administrator if needed
- Restart your computer after driver installation

### Import errors
- Run `setup_gpu_watch.bat` again
- Or manually: `pip install textual rich nvidia-ml-py3`

### Display issues
- Try the Lite version: `python gpu_watch_lite.py`
- Use Windows Terminal for best experience
- Make sure your terminal supports Unicode

### High CPU usage
- Normal - real-time monitoring uses some CPU
- Adjust refresh rate in code if needed (line with `set_interval`)

## 🎨 Terminal Recommendations

For the best experience, use:
- **Windows Terminal** (recommended) - Get from Microsoft Store
- **Supports full colors and Unicode**
- Modern, fast, and beautiful

Avoid:
- Old CMD.exe (limited color support)
- Very old PowerShell hosts

## 🛠️ Customization

### Change refresh rate
Edit the Python files:
- In `gpu_watch.py`: Line ~129, 148 - `set_interval(0.5, ...)`
- In `gpu_watch_lite.py`: Line ~312 - `time.sleep(0.5)`

### Change sparkline length
- In `gpu_watch.py`: Line ~34 - `Sparkline(max_points=60)`
- In `gpu_watch_lite.py`: Line ~18 - `self.history_size = 60`

### Colors
Edit the color strings in either file:
- `"red"`, `"green"`, `"yellow"`, `"blue"`, `"cyan"`, `"magenta"`

## 📦 Files Included

- `gpu_watch.py` - Full version with Textual framework
- `gpu_watch_lite.py` - Lightweight version with Rich only
- `requirements.txt` - Python dependencies
- `setup_gpu_watch.bat` - Easy installation
- `run_gpu_watch.bat` - Quick launcher
- `README_GPU_WATCH.md` - This file

## 🚀 Future Ideas

Want to add:
- [ ] Export to JSON/CSV
- [ ] Alerts for high temps
- [ ] Clock speed controls
- [ ] Power limit adjustment
- [ ] Custom themes
- [ ] Web dashboard mode
- [ ] Historical data logging
- [ ] Comparison between GPUs

## 📝 License

Free to use, modify, and share! Make it your own!

## 🤝 Credits

Made with:
- [Textual](https://github.com/Textualize/textual) - Amazing TUI framework
- [Rich](https://github.com/Textualize/rich) - Beautiful terminal formatting
- [nvidia-ml-py3](https://pypi.org/project/nvidia-ml-py3/) - NVIDIA Management Library bindings

---

**Enjoy your amazing GPU monitoring experience! 🎮🚀**

Press `q` to quit when you've seen enough! Or just keep it running 24/7 because it looks so cool! 😎
