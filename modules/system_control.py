"""
system_control.py — voice-controlled PC power/volume actions.
Cross-platform (Windows / Linux / macOS) using OS-native commands.
Destructive actions (restart/shutdown) always ask for confirmation in main.py
before calling these — keep that guard, don't remove it.
"""

import platform
import subprocess

OS = platform.system()  # 'Windows', 'Linux', 'Darwin'


def lock_pc():
    if OS == "Windows":
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"])
    elif OS == "Darwin":
        subprocess.run(["pmset", "displaysleepnow"])
    else:  # Linux — depends on desktop environment
        for cmd in (["loginctl", "lock-session"], ["gnome-screensaver-command", "-l"], ["xdg-screensaver", "lock"]):
            try:
                subprocess.run(cmd, check=True)
                return
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue


def restart_pc():
    if OS == "Windows":
        subprocess.run(["shutdown", "/r", "/t", "5"])
    else:
        subprocess.run(["shutdown", "-r", "+1"])  # needs sudo on most Linux setups


def shutdown_pc():
    if OS == "Windows":
        subprocess.run(["shutdown", "/s", "/t", "5"])
    else:
        subprocess.run(["shutdown", "-h", "+1"])


def sleep_pc():
    if OS == "Windows":
        subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
    elif OS == "Darwin":
        subprocess.run(["pmset", "sleepnow"])
    else:
        subprocess.run(["systemctl", "suspend"])


def set_volume(percent: int):
    """Set system volume 0-100."""
    percent = max(0, min(100, percent))
    if OS == "Windows":
        # Requires: pip install pycaw (Windows-only), kept optional to avoid breaking other OSes.
        try:
            from ctypes import cast, POINTER
            from comtypes import CLSCTX_ALL
            from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

            devices = AudioUtilities.GetSpeakers()
            interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            volume = cast(interface, POINTER(IAudioEndpointVolume))
            volume.SetMasterVolumeLevelScalar(percent / 100, None)
        except ImportError:
            print("[system_control] Run: pip install pycaw comtypes  (Windows volume control)")
    elif OS == "Darwin":
        subprocess.run(["osascript", "-e", f"set volume output volume {percent}"])
    else:
        subprocess.run(["amixer", "-D", "pulse", "sset", "Master", f"{percent}%"])


def get_system_info() -> dict:
    """Real-time system stats via psutil — CPU/RAM/disk/battery. Used by the
    System page's info card (replaces the old always-guessing approach with
    actual live numbers)."""
    import psutil
    info = {
        "os": OS,
        "cpu_percent": psutil.cpu_percent(interval=0.3),
        "cpu_cores": psutil.cpu_count(logical=True),
        "ram_percent": psutil.virtual_memory().percent,
        "ram_used_gb": round(psutil.virtual_memory().used / (1024**3), 1),
        "ram_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
        "disk_percent": psutil.disk_usage("/").percent,
    }
    try:
        battery = psutil.sensors_battery()
        if battery:
            info["battery_percent"] = battery.percent
            info["battery_plugged"] = battery.power_plugged
    except Exception:
        pass
    return info


def list_top_processes(limit: int = 8) -> list:
    """Top processes by RAM usage — read-only, for the System page. No kill
    action exposed here on purpose: killing arbitrary processes from a web
    dashboard is exactly the kind of thing that goes wrong once and takes
    something important down with it."""
    import psutil
    procs = []
    for p in psutil.process_iter(["pid", "name", "memory_percent"]):
        try:
            procs.append(p.info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda p: p.get("memory_percent") or 0, reverse=True)
    return procs[:limit]


if __name__ == "__main__":
    print(f"Detected OS: {OS}")
    set_volume(50)
