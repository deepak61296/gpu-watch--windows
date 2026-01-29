# GPU Watch

Hey everyone! I'm a robotics engineer and I do some AI/ML work, so I love to analyze my GPU temps, wattage, usage, memory, etc. That's why I made this.

I used nvidia-smi but it flickers a lot and is not cool, so I just made something cooler XD

![GPU Watch Demo](https://via.placeholder.com/800x400.png?text=GPU+Watch+Demo)

## Features

- Real-time GPU monitoring (usage, memory, temperature, power, clocks)
- Beautiful terminal UI with color-coded bars
- 60-point sparkline history graphs
- GPU process monitoring
- Zero flickering (unlike nvidia-smi)
- Multi-GPU support

## Installation

1. Clone the repo:
```bash
git clone https://github.com/yourusername/gpu-watch.git
cd gpu-watch
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Windows
```bash
python gpu_watch_windows.py
```

Or just double-click `run_windows.bat`

### Controls
- `Ctrl+C` to exit

## Requirements

- Windows 10/11
- NVIDIA GPU with drivers installed
- Python 3.8+

## Build as EXE (Optional)

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole gpu_watch_windows.py
```

The executable will be in the `dist/` folder.

## License

MIT

---

Made with ❤️ for better GPU monitoring
