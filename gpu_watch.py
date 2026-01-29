#!/usr/bin/env python3
"""
GPU Watch - Beautiful GPU Monitoring Terminal App
Better than nvidia-smi with stunning visuals and zero flickering
"""

from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Label, ProgressBar
from textual.reactive import reactive
from rich.console import RenderableType
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.bar import Bar
from rich.progress import Progress
import pynvml
from datetime import datetime
import time
from collections import deque


class Sparkline(Static):
    """A sparkline widget for showing GPU usage history"""

    values = reactive(list)

    def __init__(self, max_points: int = 50, **kwargs):
        super().__init__(**kwargs)
        self.max_points = max_points
        self.values = deque([0] * max_points, maxlen=max_points)
        self.chars = " ▁▂▃▄▅▆▇█"

    def add_value(self, value: float):
        """Add a new value to the sparkline"""
        self.values.append(value)
        self.refresh()

    def render(self) -> RenderableType:
        if not self.values:
            return ""

        max_val = max(self.values) if max(self.values) > 0 else 1
        text = Text()

        for val in self.values:
            norm = val / max_val
            idx = min(int(norm * (len(self.chars) - 1)), len(self.chars) - 1)

            # Color based on value
            if val > 80:
                color = "red"
            elif val > 50:
                color = "yellow"
            else:
                color = "green"

            text.append(self.chars[idx], style=color)

        return text


class GPUCard(Static):
    """Widget for displaying a single GPU's information"""

    def __init__(self, gpu_index: int, **kwargs):
        super().__init__(**kwargs)
        self.gpu_index = gpu_index
        self.handle = None
        self.gpu_sparkline = Sparkline(max_points=60)
        self.mem_sparkline = Sparkline(max_points=60)
        self.temp_sparkline = Sparkline(max_points=60)

        try:
            self.handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_index)
        except Exception as e:
            self.handle = None

    def compose(self) -> ComposeResult:
        yield self.gpu_sparkline
        yield self.mem_sparkline
        yield self.temp_sparkline

    def on_mount(self):
        self.set_interval(0.5, self.update_gpu_info)

    def update_gpu_info(self):
        """Update GPU information"""
        if not self.handle:
            return

        try:
            # Get GPU info
            name = pynvml.nvmlDeviceGetName(self.handle)
            if isinstance(name, bytes):
                name = name.decode('utf-8')

            # Utilization
            util = pynvml.nvmlDeviceGetUtilizationRates(self.handle)
            gpu_util = util.gpu
            mem_util = util.memory

            # Memory
            mem_info = pynvml.nvmlDeviceGetMemoryInfo(self.handle)
            mem_used = mem_info.used / 1024**3  # Convert to GB
            mem_total = mem_info.total / 1024**3
            mem_percent = (mem_info.used / mem_info.total) * 100

            # Temperature
            temp = pynvml.nvmlDeviceGetTemperature(self.handle, pynvml.NVML_TEMPERATURE_GPU)

            # Power
            try:
                power = pynvml.nvmlDeviceGetPowerUsage(self.handle) / 1000  # Convert to W
                power_limit = pynvml.nvmlDeviceGetPowerManagementLimit(self.handle) / 1000
            except:
                power = 0
                power_limit = 0

            # Clock speeds
            try:
                gpu_clock = pynvml.nvmlDeviceGetClockInfo(self.handle, pynvml.NVML_CLOCK_GRAPHICS)
                mem_clock = pynvml.nvmlDeviceGetClockInfo(self.handle, pynvml.NVML_CLOCK_MEM)
            except:
                gpu_clock = 0
                mem_clock = 0

            # Fan speed
            try:
                fan_speed = pynvml.nvmlDeviceGetFanSpeed(self.handle)
            except:
                fan_speed = 0

            # Update sparklines
            self.gpu_sparkline.add_value(gpu_util)
            self.mem_sparkline.add_value(mem_percent)
            self.temp_sparkline.add_value(temp)

            # Create rich table for display
            table = Table.grid(padding=(0, 2))
            table.add_column(style="bold cyan", justify="right")
            table.add_column(style="bold white")

            # Title
            title_text = Text(f"🎮 GPU {self.gpu_index}: {name}", style="bold magenta")

            # GPU Utilization with color
            gpu_color = "red" if gpu_util > 80 else "yellow" if gpu_util > 50 else "green"
            gpu_bar = "█" * int(gpu_util / 2) + "░" * (50 - int(gpu_util / 2))

            # Memory bar
            mem_color = "red" if mem_percent > 80 else "yellow" if mem_percent > 50 else "green"
            mem_bar = "█" * int(mem_percent / 2) + "░" * (50 - int(mem_percent / 2))

            # Temperature color
            temp_color = "red" if temp > 80 else "yellow" if temp > 65 else "green"

            # Power bar
            power_percent = (power / power_limit * 100) if power_limit > 0 else 0
            power_color = "red" if power_percent > 80 else "yellow" if power_percent > 50 else "green"
            power_bar = "█" * int(power_percent / 2) + "░" * (50 - int(power_percent / 2))

            content = Table.grid(padding=(0, 1))
            content.add_column(style="bold cyan", justify="left", width=12)
            content.add_column(justify="left")

            content.add_row(
                "GPU Usage:",
                Text(f"[{gpu_color}]{gpu_bar}[/{gpu_color}] {gpu_util:3.0f}%")
            )
            content.add_row(
                "Memory:",
                Text(f"[{mem_color}]{mem_bar}[/{mem_color}] {mem_used:.1f}/{mem_total:.1f} GB ({mem_percent:.0f}%)")
            )
            content.add_row(
                "Temperature:",
                Text(f"{'🔥' if temp > 80 else '🌡️ '} {temp}°C", style=temp_color)
            )
            content.add_row(
                "Power:",
                Text(f"[{power_color}]{power_bar}[/{power_color}] {power:.1f}/{power_limit:.0f} W")
            )
            content.add_row(
                "GPU Clock:",
                Text(f"⚡ {gpu_clock} MHz", style="blue")
            )
            content.add_row(
                "Memory Clock:",
                Text(f"💾 {mem_clock} MHz", style="blue")
            )
            if fan_speed > 0:
                fan_color = "red" if fan_speed > 80 else "yellow" if fan_speed > 50 else "green"
                content.add_row(
                    "Fan Speed:",
                    Text(f"🌀 {fan_speed}%", style=fan_color)
                )

            # Add sparklines
            content.add_row("")
            content.add_row("GPU History:", self.gpu_sparkline.render())
            content.add_row("Memory History:", self.mem_sparkline.render())
            content.add_row("Temp History:", self.temp_sparkline.render())

            panel = Panel(
                content,
                title=title_text,
                border_style="bright_blue",
                padding=(1, 2)
            )

            self.update(panel)

        except Exception as e:
            error_panel = Panel(
                f"[red]Error reading GPU {self.gpu_index}:[/red]\n{str(e)}",
                border_style="red"
            )
            self.update(error_panel)


class ProcessTable(Static):
    """Widget for displaying GPU processes"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.gpu_count = 0

    def on_mount(self):
        try:
            self.gpu_count = pynvml.nvmlDeviceGetCount()
        except:
            self.gpu_count = 0

        self.set_interval(2.0, self.update_processes)

    def update_processes(self):
        """Update process information"""
        try:
            table = Table(
                title="🔍 GPU Processes",
                show_header=True,
                header_style="bold magenta",
                border_style="blue",
                title_style="bold cyan"
            )

            table.add_column("GPU", style="cyan", width=4)
            table.add_column("PID", style="yellow", width=8)
            table.add_column("Process Name", style="green")
            table.add_column("Memory", style="blue", justify="right")

            has_processes = False

            for i in range(self.gpu_count):
                try:
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    processes = pynvml.nvmlDeviceGetComputeRunningProcesses(handle)

                    for proc in processes:
                        has_processes = True
                        try:
                            proc_name = pynvml.nvmlSystemGetProcessName(proc.pid)
                            if isinstance(proc_name, bytes):
                                proc_name = proc_name.decode('utf-8')
                            proc_name = proc_name.split('\\')[-1]  # Get just filename
                        except:
                            proc_name = "Unknown"

                        mem_mb = proc.usedGpuMemory / 1024**2 if hasattr(proc, 'usedGpuMemory') else 0

                        table.add_row(
                            str(i),
                            str(proc.pid),
                            proc_name,
                            f"{mem_mb:.0f} MB"
                        )
                except:
                    continue

            if not has_processes:
                table.add_row("—", "—", "No active GPU processes", "—")

            panel = Panel(table, border_style="bright_blue")
            self.update(panel)

        except Exception as e:
            self.update(f"[red]Error getting processes: {str(e)}[/red]")


class SystemInfo(Static):
    """Widget for displaying system information"""

    def on_mount(self):
        self.set_interval(5.0, self.update_system_info)
        self.update_system_info()

    def update_system_info(self):
        """Update system information"""
        try:
            driver_version = pynvml.nvmlSystemGetDriverVersion()
            if isinstance(driver_version, bytes):
                driver_version = driver_version.decode('utf-8')

            cuda_version = pynvml.nvmlSystemGetCudaDriverVersion()
            cuda_version_str = f"{cuda_version // 1000}.{(cuda_version % 1000) // 10}"

            gpu_count = pynvml.nvmlDeviceGetCount()

            table = Table.grid(padding=(0, 2))
            table.add_column(style="bold cyan", justify="right")
            table.add_column(style="white")

            table.add_row("Driver Version:", driver_version)
            table.add_row("CUDA Version:", cuda_version_str)
            table.add_row("GPU Count:", str(gpu_count))
            table.add_row("Updated:", datetime.now().strftime("%H:%M:%S"))

            panel = Panel(
                table,
                title="💻 System Info",
                border_style="green",
                padding=(1, 2)
            )

            self.update(panel)

        except Exception as e:
            self.update(f"[red]Error: {str(e)}[/red]")


class GPUWatchApp(App):
    """A GPU monitoring terminal application"""

    CSS = """
    Screen {
        background: $surface;
    }

    #gpu_container {
        height: auto;
        margin: 1;
    }

    #info_container {
        height: auto;
        margin: 1;
    }

    GPUCard {
        height: auto;
        margin: 1 2;
    }

    ProcessTable {
        height: auto;
        margin: 1;
    }

    SystemInfo {
        height: auto;
        margin: 1;
    }
    """

    TITLE = "GPU Watch - Real-time GPU Monitoring"
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("r", "refresh", "Refresh"),
    ]

    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()

        try:
            gpu_count = pynvml.nvmlDeviceGetCount()

            with ScrollableContainer(id="gpu_container"):
                for i in range(gpu_count):
                    yield GPUCard(i)

            with Vertical(id="info_container"):
                yield SystemInfo()
                yield ProcessTable()

        except Exception as e:
            yield Static(f"[red]Error initializing GPU monitoring:[/red]\n{str(e)}")

        yield Footer()

    def on_mount(self):
        """Initialize NVML on mount"""
        try:
            pynvml.nvmlInit()
        except Exception as e:
            self.exit(message=f"Failed to initialize NVML: {str(e)}")

    def on_unmount(self):
        """Shutdown NVML on exit"""
        try:
            pynvml.nvmlShutdown()
        except:
            pass

    def action_refresh(self):
        """Refresh all widgets"""
        for widget in self.query(GPUCard):
            widget.update_gpu_info()

        for widget in self.query(ProcessTable):
            widget.update_processes()

        for widget in self.query(SystemInfo):
            widget.update_system_info()


def main():
    """Main entry point"""
    app = GPUWatchApp()
    app.run()


if __name__ == "__main__":
    main()
