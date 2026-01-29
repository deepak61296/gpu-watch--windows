#!/usr/bin/env python3
"""GPU Watch - Real-time NVIDIA GPU Monitor for Windows"""

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.text import Text
import subprocess
import time
from collections import deque
from datetime import datetime

console = Console()

class WindowsGPUMonitor:
    """GPU monitoring using nvidia-smi"""

    def __init__(self):
        self.sparkline_chars = " ▁▂▃▄▅▆▇█"
        self.history_size = 60
        self.gpu_history = {}
        self.mem_history = {}
        self.temp_history = {}
        self.gpu_count = 0
        self.detect_gpus()

    def detect_gpus(self):
        """Detect NVIDIA GPUs"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=count', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                self.gpu_count = int(result.stdout.strip())
                console.print(f"[green]Detected {self.gpu_count} NVIDIA GPU(s)[/green]")

                for i in range(self.gpu_count):
                    self.gpu_history[i] = deque([0] * self.history_size, maxlen=self.history_size)
                    self.mem_history[i] = deque([0] * self.history_size, maxlen=self.history_size)
                    self.temp_history[i] = deque([0] * self.history_size, maxlen=self.history_size)
            else:
                raise Exception("nvidia-smi failed")

        except Exception as e:
            console.print(f"[red]Error detecting GPUs: {e}[/red]")
            console.print("[yellow]Make sure NVIDIA drivers are installed[/yellow]")
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

    def get_gpu_info(self):
        """Get GPU information"""
        try:
            query = 'index,name,utilization.gpu,utilization.memory,memory.used,memory.total,temperature.gpu,power.draw,power.limit,power.max_limit,clocks.gr,clocks.mem,fan.speed'

            result = subprocess.run(
                ['nvidia-smi', f'--query-gpu={query}', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=2
            )

            if result.returncode != 0:
                return None

            gpus = []
            for line in result.stdout.strip().split('\n'):
                parts = [p.strip() for p in line.split(',')]

                if len(parts) >= 13:
                    try:
                        power_limit = float(parts[8]) if parts[8] != '[N/A]' else 0
                        if power_limit == 0:
                            power_limit = float(parts[9]) if parts[9] != '[N/A]' else 0

                        gpu_info = {
                            'index': int(parts[0]),
                            'name': parts[1],
                            'gpu_util': float(parts[2]) if parts[2] != '[N/A]' else 0,
                            'mem_util': float(parts[3]) if parts[3] != '[N/A]' else 0,
                            'mem_used': float(parts[4]) if parts[4] != '[N/A]' else 0,
                            'mem_total': float(parts[5]) if parts[5] != '[N/A]' else 0,
                            'temp': float(parts[6]) if parts[6] != '[N/A]' else 0,
                            'power': float(parts[7]) if parts[7] != '[N/A]' else 0,
                            'power_limit': power_limit,
                            'gpu_clock': int(parts[10]) if parts[10] != '[N/A]' else 0,
                            'mem_clock': int(parts[11]) if parts[11] != '[N/A]' else 0,
                            'fan_speed': float(parts[12]) if parts[12] != '[N/A]' and parts[12] != '[Unknown Error]' else 0,
                        }

                        if gpu_info['mem_total'] > 0:
                            gpu_info['mem_percent'] = (gpu_info['mem_used'] / gpu_info['mem_total']) * 100
                        else:
                            gpu_info['mem_percent'] = 0

                        idx = gpu_info['index']
                        self.gpu_history[idx].append(gpu_info['gpu_util'])
                        self.mem_history[idx].append(gpu_info['mem_percent'])
                        self.temp_history[idx].append(gpu_info['temp'])

                        gpus.append(gpu_info)

                    except (ValueError, IndexError) as e:
                        console.print(f"[red]Error parsing GPU data: {e}[/red]")
                        continue

            return gpus

        except Exception as e:
            console.print(f"[red]Error getting GPU info: {e}[/red]")
            return None

    def get_processes(self):
        """Get GPU processes"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-compute-apps=gpu_name,pid,process_name,used_memory', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=2
            )

            processes = []
            if result.returncode == 0 and result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 4:
                        processes.append({
                            'gpu': parts[0],
                            'pid': parts[1],
                            'name': parts[2].split('\\')[-1],
                            'memory': parts[3]
                        })

            return processes

        except Exception:
            return []

    def create_gpu_panel(self, info):
        """Create a panel for a GPU"""
        if info is None:
            return Panel("[red]Error reading GPU[/red]", border_style="red")

        table = Table.grid(padding=(0, 1))
        table.add_column(style="bold cyan", justify="left", width=14)
        table.add_column(justify="left")

        gpu_bar = self.make_bar(info['gpu_util'], width=40)
        table.add_row(
            "GPU Usage:",
            Text.assemble(gpu_bar, f" {info['gpu_util']:>3.0f}%")
        )

        mem_bar = self.make_bar(info['mem_percent'], width=40)
        mem_used_gb = info['mem_used'] / 1024
        mem_total_gb = info['mem_total'] / 1024
        table.add_row(
            "Memory:",
            Text.assemble(
                mem_bar,
                f" {mem_used_gb:.1f}/{mem_total_gb:.1f} GB ({info['mem_percent']:.0f}%)"
            )
        )

        temp = info.get('temp', 0)
        temp_icon = "🔥" if temp > 80 else "🌡️"
        temp_color = "red" if temp > 80 else "yellow" if temp > 65 else "green"
        table.add_row(
            "Temperature:",
            Text(f"{temp_icon} {temp:.0f}°C", style=temp_color)
        )

        power = info.get('power', 0)
        power_limit = info.get('power_limit', 0)

        if power_limit > 0:
            power_percent = (power / power_limit * 100)
            power_bar = self.make_bar(power_percent, width=40)
            table.add_row(
                "Power:",
                Text.assemble(power_bar, f" {power:.1f}/{power_limit:.0f} W")
            )
        elif power > 0:
            table.add_row(
                "Power:",
                Text(f"⚡ {power:.1f} W", style="bright_yellow")
            )

        table.add_row(
            "GPU Clock:",
            Text(f"[CLOCK] {info['gpu_clock']} MHz", style="bright_blue")
        )
        table.add_row(
            "Memory Clock:",
            Text(f"[MEM] {info['mem_clock']} MHz", style="bright_blue")
        )

        if info['fan_speed'] > 0:
            fan_color = "red" if info['fan_speed'] > 80 else "yellow" if info['fan_speed'] > 50 else "green"
            table.add_row(
                "Fan Speed:",
                Text(f"[FAN] {info['fan_speed']:.0f}%", style=fan_color)
            )

        table.add_row("")
        table.add_row("GPU History:", self.make_sparkline(list(self.gpu_history[info['index']])))
        table.add_row("Mem History:", self.make_sparkline(list(self.mem_history[info['index']])))
        table.add_row("Temp History:", self.make_sparkline(list(self.temp_history[info['index']])))

        title = Text()
        title.append("[GPU] ", style="bold")
        title.append(str(info['index']), style="bold yellow")
        title.append(f": {info['name']}", style="bold cyan")

        return Panel(table, title=title, border_style="bright_blue", padding=(1, 2))

    def create_process_table(self, processes):
        """Create process table"""
        table = Table(
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            title="[PROCESSES] GPU Processes",
            title_style="bold cyan"
        )

        table.add_column("PID", style="yellow", width=8)
        table.add_column("Process Name", style="green")
        table.add_column("Memory", style="blue", justify="right")

        if not processes:
            table.add_row("—", "No active GPU processes", "—")
        else:
            for proc in processes:
                table.add_row(
                    proc['pid'],
                    proc['name'],
                    proc['memory']
                )

        return Panel(table, border_style="bright_blue")

    def create_system_info(self):
        """Create system info panel"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=driver_version', '--format=csv,noheader'],
                capture_output=True,
                text=True,
                timeout=2
            )
            driver = result.stdout.strip().split('\n')[0] if result.returncode == 0 else "Unknown"

            table = Table.grid(padding=(0, 2))
            table.add_column(style="bold cyan", justify="right")
            table.add_column(style="white")

            table.add_row("Driver:", driver)
            table.add_row("GPUs:", str(self.gpu_count))
            table.add_row("Time:", datetime.now().strftime("%H:%M:%S"))
            table.add_row("Method:", "nvidia-smi (Windows)")

            return Panel(table, title="[SYSTEM] Info", border_style="green", padding=(0, 2))

        except Exception as e:
            return Panel(f"[red]Error: {e}[/red]", border_style="red")

    def generate_layout(self):
        """Generate the display layout"""
        layout = Layout()

        system_info = self.create_system_info()

        gpus = self.get_gpu_info()
        if not gpus:
            return Panel("[red]Error reading GPU data[/red]", border_style="red")

        gpu_panels = [self.create_gpu_panel(gpu) for gpu in gpus]

        processes = self.get_processes()
        process_table = self.create_process_table(processes)

        layout.split_column(
            Layout(system_info, size=8),
            Layout(name="gpus"),
            Layout(process_table, size=10)
        )

        if len(gpu_panels) == 1:
            layout["gpus"].update(gpu_panels[0])
        else:
            layout["gpus"].split_column(*[Layout(panel) for panel in gpu_panels])

        return layout

    def run(self):
        """Run the monitor"""
        console.print(Panel(
            "[bold cyan]GPU Watch for Windows[/bold cyan]\n"
            "[yellow]Press Ctrl+C to exit[/yellow]",
            border_style="bright_blue"
        ))

        time.sleep(1)

        try:
            with Live(self.generate_layout(), refresh_per_second=2, console=console) as live:
                while True:
                    live.update(self.generate_layout())
                    time.sleep(0.5)

        except KeyboardInterrupt:
            console.print("\n[yellow]Monitoring stopped.[/yellow]")


def main():
    """Main entry point"""
    try:
        monitor = WindowsGPUMonitor()
        monitor.run()
    except KeyboardInterrupt:
        console.print("\n[yellow]Exiting...[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        console.print("\n[yellow]Press Enter to exit...[/yellow]")
        input()


if __name__ == "__main__":
    main()
