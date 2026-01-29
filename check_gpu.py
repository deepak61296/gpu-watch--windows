#!/usr/bin/env python3
"""
GPU Diagnostics - Check what GPUs are available and troubleshoot
"""

import sys
import os
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
import sys

# Fix for Windows console encoding issues
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

console = Console(force_terminal=True, legacy_windows=False)

def check_nvidia():
    """Check for NVIDIA GPU and drivers"""
    console.print("\n[bold cyan]Checking for NVIDIA GPU...[/bold cyan]")

    # Try importing pynvml
    try:
        import pynvml
        console.print("[green]OK - pynvml library installed[/green]")

        # Try initializing NVML
        try:
            pynvml.nvmlInit()
            console.print("[green]OK - NVML initialized successfully[/green]")

            # Get GPU count
            gpu_count = pynvml.nvmlDeviceGetCount()
            console.print(f"[green]OK - Found {gpu_count} NVIDIA GPU(s)[/green]\n")

            # Get GPU details
            table = Table(title="NVIDIA GPUs Detected", border_style="green")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="yellow")
            table.add_column("Driver", style="blue")

            for i in range(gpu_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle)
                if isinstance(name, bytes):
                    name = name.decode('utf-8')

                driver = pynvml.nvmlSystemGetDriverVersion()
                if isinstance(driver, bytes):
                    driver = driver.decode('utf-8')

                table.add_row(str(i), name, driver)

            console.print(table)

            pynvml.nvmlShutdown()
            return True

        except Exception as e:
            console.print(f"[red]ERROR - Failed to initialize NVML: {e}[/red]")
            return False

    except ImportError:
        console.print("[red]ERROR - pynvml not installed[/red]")
        return False

def check_nvidia_smi():
    """Check if nvidia-smi is available"""
    console.print("\n[bold cyan]Checking nvidia-smi...[/bold cyan]")

    import subprocess
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            console.print("[green]OK - nvidia-smi is working[/green]")
            console.print("\n[dim]nvidia-smi output:[/dim]")
            # Show first few lines
            lines = result.stdout.split('\n')[:15]
            for line in lines:
                console.print(f"  {line}")
            return True
        else:
            console.print("[red]ERROR - nvidia-smi failed[/red]")
            return False
    except FileNotFoundError:
        console.print("[red]ERROR - nvidia-smi not found in PATH[/red]")
        return False
    except Exception as e:
        console.print(f"[red]ERROR - Error running nvidia-smi: {e}[/red]")
        return False

def check_windows_gpu():
    """Check GPU using Windows methods"""
    console.print("\n[bold cyan]Checking Windows GPU info...[/bold cyan]")

    import subprocess
    try:
        # Use WMIC to get GPU info
        result = subprocess.run(
            ['wmic', 'path', 'win32_VideoController', 'get', 'name'],
            capture_output=True,
            text=True,
            timeout=5
        )

        if result.returncode == 0:
            gpus = [line.strip() for line in result.stdout.split('\n') if line.strip() and line.strip() != 'Name']

            table = Table(title="GPUs Detected by Windows", border_style="blue")
            table.add_column("GPU Name", style="yellow")

            has_nvidia = False
            for gpu in gpus:
                table.add_row(gpu)
                if 'NVIDIA' in gpu.upper():
                    has_nvidia = True

            console.print(table)

            if has_nvidia:
                console.print("\n[green]OK - NVIDIA GPU detected by Windows[/green]")
            else:
                console.print("\n[yellow]WARNING - No NVIDIA GPU found - you may have AMD/Intel GPU[/yellow]")

            return has_nvidia

    except Exception as e:
        console.print(f"[red]Error checking Windows GPU: {e}[/red]")
        return False

def print_solutions(has_nvidia_gpu):
    """Print solutions based on findings"""
    console.print("\n" + "="*60)

    if not has_nvidia_gpu:
        panel = Panel(
            """[bold red]No NVIDIA GPU Detected[/bold red]

It looks like you don't have an NVIDIA GPU or it's not being detected by Windows.

[bold yellow]Possible reasons:[/bold yellow]
1. You have an AMD or Intel GPU (not NVIDIA)
2. NVIDIA GPU is disabled in Device Manager
3. GPU drivers are not installed

[bold cyan]Solutions:[/bold cyan]
1. Check Device Manager (Win+X → Device Manager → Display adapters)
2. If you have NVIDIA GPU, install drivers from:
   https://www.nvidia.com/Download/index.aspx
3. If you have AMD/Intel GPU, you need a different monitoring tool

[bold green]Alternative Tools:[/bold green]
• For AMD: AMD Software / Radeon Software
• For Intel: Intel Arc Control
• Universal: GPU-Z, HWiNFO64, Task Manager (Performance tab)
""",
            title="Diagnosis",
            border_style="red",
            padding=(1, 2)
        )
    else:
        panel = Panel(
            """[bold yellow]NVIDIA GPU Found but NVML Not Working[/bold yellow]

Your NVIDIA GPU is detected by Windows but the NVML library can't access it.

[bold cyan]Try these solutions:[/bold cyan]

1. [bold]Install/Update NVIDIA Drivers:[/bold]
   • Download from: https://www.nvidia.com/Download/index.aspx
   • Choose GeForce/RTX drivers
   • Do a CLEAN installation
   • Restart your computer after installation

2. [bold]Check if nvidia-smi works:[/bold]
   • Open PowerShell and run: nvidia-smi
   • If it works, the issue is with Python access
   • If it fails, reinstall drivers

3. [bold]Add NVIDIA to PATH (if drivers are installed):[/bold]
   • The DLL should be in: C:\\Program Files\\NVIDIA Corporation\\NVSMI
   • Or in: C:\\Windows\\System32

4. [bold]Run as Administrator:[/bold]
   • Right-click PowerShell → Run as Administrator
   • Try running the script again

5. [bold]Reinstall nvidia-ml-py3:[/bold]
   pip uninstall nvidia-ml-py3
   pip install nvidia-ml-py3

[bold green]After fixing, try running:[/bold green]
   python gpu_watch.py
""",
            title="Solutions",
            border_style="yellow",
            padding=(1, 2)
        )

    console.print(panel)

def main():
    """Main diagnostic routine"""
    console.print(Panel(
        "[bold cyan]GPU Watch - System Diagnostics[/bold cyan]\n"
        "Checking your system for GPU compatibility...",
        border_style="bright_blue"
    ))

    # Check Windows GPU info first
    has_nvidia_in_windows = check_windows_gpu()

    # Check nvidia-smi
    nvidia_smi_works = check_nvidia_smi()

    # Check NVML
    nvml_works = check_nvidia()

    # Print solutions
    print_solutions(has_nvidia_in_windows)

    # Summary
    console.print("\n[bold]Summary:[/bold]")
    status_table = Table(show_header=False, box=None)
    status_table.add_column("Check", style="cyan")
    status_table.add_column("Status")

    status_table.add_row(
        "Windows GPU Detection",
        "[green]OK - NVIDIA GPU found[/green]" if has_nvidia_in_windows else "[red]ERROR - No NVIDIA GPU[/red]"
    )
    status_table.add_row(
        "nvidia-smi",
        "[green]OK - Working[/green]" if nvidia_smi_works else "[red]ERROR - Not working[/red]"
    )
    status_table.add_row(
        "NVML (Python access)",
        "[green]OK - Working[/green]" if nvml_works else "[red]ERROR - Not working[/red]"
    )

    console.print(status_table)

    if nvml_works:
        console.print("\n[bold green]SUCCESS - All checks passed! GPU Watch should work fine.[/bold green]")
        console.print("[cyan]Run: python gpu_watch.py[/cyan]")
    else:
        console.print("\n[bold red]WARNING - GPU Watch cannot run until the issues above are fixed.[/bold red]")

if __name__ == "__main__":
    main()
