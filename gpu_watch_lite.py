#!/usr/bin/env python3
"""
GPU Watch Lite - Lightweight version using Rich only
Beautiful GPU monitoring with zero flickering
"""

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
from rich.align import Align
import pynvml
from datetime import datetime
from collections import deque
import time


class GPUMonitor:
    """GPU monitoring with Rich"""

    def __init__(self):
        self.console = Console()
        self.sparkline_chars = " ▁▂▃▄▅▆▇█"
        self.history_size = 60
        self.gpu_history = {}
        self.mem_history = {}
        self.temp_history = {}

        # Initialize NVML
        try:
            pynvml.nvmlInit()
            self.gpu_count = pynvml.nvmlDeviceGetCount()

            # Initialize history for each GPU
            for i in range(self.gpu_count):
                self.gpu_history[i] = deque([0] * self.history_size, maxlen=self.history_size)
                self.mem_history[i] = deque([0] * self.history_size, maxlen=self.history_size)
                self.temp_history[i] = deque([0] * self.history_size, maxlen=self.history_size)

        except Exception as e:
            self.console.print(f"[red]Error initializing NVML: {e}[/red]")
            exit(1)

    def make_sparkline(self, values):
        """Create a sparkline from values"""
        if not values or max(values) == 0:
            return Text("─" * len(values), style="dim")

        max_val = max(values)
        text = Text()

        for val in values:
            norm = val / max_val
            idx = min(int(norm * (len(self.sparkline_chars) - 1)), len(self.sparkline_chars) - 1)

            # Color based on value
            if val > 80:
                color = "red"
            elif val > 50:
                color = "yellow"
            else:
                color = "green"

            text.append(self.sparkline_chars[idx], style=color)

        return text

    def make_bar(self, value, width=40):
        """Create a colored bar"""
        filled = int(value / 100 * width)
        bar = "█" * filled + "░" * (width - filled)

        # Color based on value
        if value > 80:
            color = "red"
        elif value > 50:
            color = "yellow"
        else:
            color = "green"

        return Text(bar, style=color)

    def get_gpu_info(self, gpu_index):
        """Get information for a specific GPU"""
        try:
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)

            # Basic info
            name = pynvml.nvmlDeviceGetName(handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')

            # Utilization
            util = pynvml.nvmlDeviceGetUtilizationRates(handle)
            gpu_util = util.gpu
            mem_util = util.memory

            # Memory
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
            mem_used = mem_info.used / 1024**3  # GB
            mem_total = mem_info.total / 1024**3
            mem_percent = (mem_info.used / mem_info.total) * 100

            # Temperature
            temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)

            # Power
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000  # W
                power_limit = pynvml.nvmlDeviceGetPowerManagementLimit(handle) / 1000
            except:
                power = 0
                power_limit = 0

            # Clock speeds
            try:
                gpu_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_GRAPHICS)
                mem_clock = pynvml.nvmlDeviceGetClockInfo(handle, pynvml.NVML_CLOCK_MEM)
            except:
                gpu_clock = 0
                mem_clock = 0

            # Fan speed
            try:
                fan_speed = pynvml.nvmlDeviceGetFanSpeed(handle)
            except:
                fan_speed = 0

            # Update history
            self.gpu_history[gpu_index].append(gpu_util)
            self.mem_history[gpu_index].append(mem_percent)
            self.temp_history[gpu_index].append(temp)

            return {
                'name': name,
                'gpu_util': gpu_util,
                'mem_util': mem_util,
                'mem_used': mem_used,
                'mem_total': mem_total,
                'mem_percent': mem_percent,
                'temp': temp,
                'power': power,
                'power_limit': power_limit,
                'gpu_clock': gpu_clock,
                'mem_clock': mem_clock,
                'fan_speed': fan_speed,
            }

        except Exception as e:
            return None

    def get_processes(self):
        """Get all GPU processes"""
        processes = []

        for i in range(self.gpu_count):
            try:
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                procs = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)

                for proc in procs:
                    try:
                        proc_name = pynvml.nvmlSystemGetProcessName(proc.pid)
                        if isinstance(proc_name, bytes):
                            proc_name = proc_name.decode('utf-8')
                        proc_name = proc_name.split('\\')[-1]
                    except:
                        proc_name = "Unknown"

                    mem_mb = proc.usedGpuMemory / 1024**2 if hasattr(proc, 'usedGpuMemory') else 0

                    processes.append({
                        'gpu': i,
                        'pid': proc.pid,
                        'name': proc_name,
                        'memory': mem_mb
                    })
            except:
                continue

        return processes

    def create_gpu_panel(self, gpu_index, info):
        """Create a panel for a GPU"""
        if info is None:
            return Panel(f"[red]Error reading GPU {gpu_index}[/red]", border_style="red")

        # Create content table
        table = Table.grid(padding=(0, 1))
        table.add_column(style="bold cyan", justify="left", width=14)
        table.add_column(justify="left")

        # GPU Utilization
        gpu_bar = self.make_bar(info['gpu_util'], width=40)
        table.add_row(
            "GPU Usage:",
            Text.assemble(gpu_bar, f" {info['gpu_util']:>3.0f}%")
        )

        # Memory
        mem_bar = self.make_bar(info['mem_percent'], width=40)
        table.add_row(
            "Memory:",
            Text.assemble(
                mem_bar,
                f" {info['mem_used']:.1f}/{info['mem_total']:.1f} GB ({info['mem_percent']:.0f}%)"
            )
        )

        # Temperature
        temp_icon = "🔥" if info['temp'] > 80 else "🌡️"
        temp_color = "red" if info['temp'] > 80 else "yellow" if info['temp'] > 65 else "green"
        table.add_row(
            "Temperature:",
            Text(f"{temp_icon} {info['temp']}°C", style=temp_color)
        )

        # Power
        if info['power_limit'] > 0:
            power_percent = (info['power'] / info['power_limit'] * 100)
            power_bar = self.make_bar(power_percent, width=40)
            table.add_row(
                "Power:",
                Text.assemble(power_bar, f" {info['power']:.1f}/{info['power_limit']:.0f} W")
            )

        # Clocks
        table.add_row(
            "GPU Clock:",
            Text(f"⚡ {info['gpu_clock']} MHz", style="bright_blue")
        )
        table.add_row(
            "Memory Clock:",
            Text(f"💾 {info['mem_clock']} MHz", style="bright_blue")
        )

        # Fan
        if info['fan_speed'] > 0:
            fan_color = "red" if info['fan_speed'] > 80 else "yellow" if info['fan_speed'] > 50 else "green"
            table.add_row(
                "Fan Speed:",
                Text(f"🌀 {info['fan_speed']}%", style=fan_color)
            )

        # Sparklines
        table.add_row("")
        table.add_row("GPU History:", self.make_sparkline(list(self.gpu_history[gpu_index])))
        table.add_row("Mem History:", self.make_sparkline(list(self.mem_history[gpu_index])))
        table.add_row("Temp History:", self.make_sparkline(list(self.temp_history[gpu_index])))

        title = Text()
        title.append("🎮 GPU ", style="bold")
        title.append(str(gpu_index), style="bold yellow")
        title.append(f": {info['name']}", style="bold cyan")

        return Panel(table, title=title, border_style="bright_blue", padding=(1, 2))

    def create_process_table(self, processes):
        """Create process table"""
        table = Table(
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            title="🔍 GPU Processes",
            title_style="bold cyan"
        )

        table.add_column("GPU", style="cyan", width=5)
        table.add_column("PID", style="yellow", width=8)
        table.add_column("Process Name", style="green")
        table.add_column("Memory", style="blue", justify="right")

        if not processes:
            table.add_row("—", "—", "No active GPU processes", "—")
        else:
            for proc in processes:
                table.add_row(
                    str(proc['gpu']),
                    str(proc['pid']),
                    proc['name'],
                    f"{proc['memory']:.0f} MB"
                )

        return Panel(table, border_style="bright_blue")

    def create_system_info(self):
        """Create system info panel"""
        try:
            driver_version = pynvml.nvmlSystemGetDriverVersion()
            if isinstance(driver_version, bytes):
                driver_version = driver_version.decode('utf-8')

            cuda_version = pynvml.nvmlSystemGetCudaDriverVersion()
            cuda_version_str = f"{cuda_version // 1000}.{(cuda_version % 1000) // 10}"

            table = Table.grid(padding=(0, 2))
            table.add_column(style="bold cyan", justify="right")
            table.add_column(style="white")

            table.add_row("Driver:", driver_version)
            table.add_row("CUDA:", cuda_version_str)
            table.add_row("GPUs:", str(self.gpu_count))
            table.add_row("Time:", datetime.now().strftime("%H:%M:%S"))

            return Panel(table, title="💻 System", border_style="green", padding=(0, 2))

        except Exception as e:
            return Panel(f"[red]Error: {e}[/red]", border_style="red")

    def generate_layout(self):
        """Generate the display layout"""
        layout = Layout()

        # System info at top
        system_info = self.create_system_info()

        # Get all GPU info
        gpu_panels = []
        for i in range(self.gpu_count):
            info = self.get_gpu_info(i)
            gpu_panels.append(self.create_gpu_panel(i, info))

        # Get processes
        processes = self.get_processes()
        process_table = self.create_process_table(processes)

        # Build layout
        layout.split_column(
            Layout(system_info, size=7),
            Layout(name="gpus"),
            Layout(process_table, size=12)
        )

        # Split GPU section
        if len(gpu_panels) == 1:
            layout["gpus"].update(gpu_panels[0])
        else:
            layout["gpus"].split_column(*[Layout(panel) for panel in gpu_panels])

        return layout

    def run(self):
        """Run the monitor"""
        try:
            with Live(self.generate_layout(), refresh_per_second=2, console=self.console) as live:
                while True:
                    live.update(self.generate_layout())
                    time.sleep(0.5)

        except KeyboardInterrupt:
            self.console.print("\n[yellow]Monitoring stopped.[/yellow]")
        finally:
            pynvml.nvmlShutdown()


def main():
    """Main entry point"""
    monitor = GPUMonitor()
    monitor.run()


if __name__ == "__main__":
    main()
