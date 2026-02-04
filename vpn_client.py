"""
VPN client integration: WireGuard/OpenVPN config, connect/disconnect, kill-switch.
Uses system WireGuard (wg-quick on Linux, WireGuard GUI/service on Windows).
Kill-switch: when VPN is expected on but drops, alert user (no telemetry; local-only).
"""

import os
import sys
import subprocess
import threading
from pathlib import Path
from typing import Callable, Optional

# Optional: psutil for interface check
try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False


def _is_windows() -> bool:
    return sys.platform == "win32"


def get_wireguard_paths() -> tuple:
    """Return (wireguard_exe, configs_dir) for current platform."""
    if _is_windows():
        # Typical WireGuard install
        pf = os.environ.get("ProgramFiles", "C:\\Program Files")
        wg = Path(pf) / "WireGuard" / "wireguard.exe"
        configs = Path(os.environ.get("LOCALAPPDATA", "")) / "WireGuard" / "Configurations"
        if not configs.exists():
            configs = Path(pf) / "WireGuard" / "Data" / "Configurations"
        return (wg, configs)
    # Linux: wg-quick is usually in PATH
    return ("wg-quick", Path("/etc/wireguard"))


def is_vpn_connected(interface_hint: Optional[str] = None) -> bool:
    """
    Best-effort check if a VPN (WireGuard-style) interface is up.
    On Linux looks for wg0 or similar; on Windows looks for adapter name containing 'WireGuard'.
    """
    if HAS_PSUTIL:
        try:
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            for name, addrs_list in addrs.items():
                if not stats.get(name) or not stats[name].isup:
                    continue
                name_lower = name.lower()
                if "wireguard" in name_lower or name_lower.startswith("wg"):
                    if addrs_list:
                        return True
        except Exception:
            pass
    if _is_windows():
        try:
            r = subprocess.run(
                ["netsh", "interface", "show", "interface"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if r.returncode == 0 and "WireGuard" in (r.stdout or ""):
                return True
        except Exception:
            pass
    else:
        try:
            r = subprocess.run(
                ["wg", "show"],
                capture_output=True,
                text=True,
                timeout=3,
            )
            if r.returncode == 0 and r.stdout.strip():
                return True
        except Exception:
            pass
    return False


def connect_wireguard(config_path: str) -> tuple:
    """
    Start WireGuard tunnel. Returns (success: bool, message: str).
    Linux: wg-quick up <conf>
    Windows: wireguard.exe /installtunnelservice <conf>
    """
    path = Path(config_path).resolve()
    if not path.exists():
        return (False, f"Config not found: {config_path}")

    wg_exe, _ = get_wireguard_paths()
    if _is_windows():
        wg_path = Path(wg_exe)
        if not wg_path.exists():
            return (False, "WireGuard not found. Install from https://www.wireguard.com/install/")
        try:
            subprocess.run(
                [str(wg_path), "/installtunnelservice", str(path)],
                capture_output=True,
                text=True,
                timeout=30,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            return (True, "Tunnel install requested. Check WireGuard tray for status.")
        except Exception as e:
            return (False, str(e))
    else:
        try:
            r = subprocess.run(
                ["wg-quick", "up", str(path)],
                capture_output=True,
                text=True,
                timeout=15,
            )
            if r.returncode == 0:
                return (True, "Connected")
            return (False, r.stderr or r.stdout or "Unknown error")
        except FileNotFoundError:
            return (False, "wg-quick not found. Install wireguard-tools.")
        except Exception as e:
            return (False, str(e))


def disconnect_wireguard(config_path: Optional[str] = None, tunnel_name: Optional[str] = None) -> tuple:
    """
    Stop WireGuard tunnel. Returns (success: bool, message: str).
    Linux: wg-quick down <conf>
    Windows: wireguard.exe /uninstalltunnelservice <name> (name = config stem)
    """
    wg_exe, configs_dir = get_wireguard_paths()
    if _is_windows():
        wg_path = Path(wg_exe)
        if not wg_path.exists():
            return (False, "WireGuard not found.")
        name = tunnel_name
        if not name and config_path:
            name = Path(config_path).stem
        if not name:
            return (False, "Specify tunnel name or config path.")
        try:
            subprocess.run(
                [str(wg_path), "/uninstalltunnelservice", name],
                capture_output=True,
                text=True,
                timeout=15,
                creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, "CREATE_NO_WINDOW") else 0,
            )
            return (True, "Tunnel stopped.")
        except Exception as e:
            return (False, str(e))
    else:
        if not config_path:
            return (False, "Config path required on Linux.")
        path = Path(config_path).resolve()
        try:
            r = subprocess.run(
                ["wg-quick", "down", str(path)],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if r.returncode == 0:
                return (True, "Disconnected")
            return (False, r.stderr or r.stdout or "Unknown error")
        except Exception as e:
            return (False, str(e))


class VPNClient:
    """
    Manages VPN connection and optional kill-switch.
    When kill_switch is True and VPN is expected on but drops, on_vpn_down() is called.
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        kill_switch: bool = False,
        on_vpn_down: Optional[Callable[[], None]] = None,
        check_interval_seconds: float = 10.0,
    ):
        self.config_path = config_path or ""
        self.kill_switch = kill_switch
        self.on_vpn_down = on_vpn_down or (lambda: None)
        self.check_interval = check_interval_seconds
        self._user_wants_connected = False
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def set_config(self, path: str) -> None:
        self.config_path = path or ""

    def connect(self) -> tuple:
        """Start VPN. Returns (success, message)."""
        self._user_wants_connected = True
        if self.kill_switch and not self._thread or not self._thread.is_alive():
            self._start_kill_switch_thread()
        return connect_wireguard(self.config_path)

    def disconnect(self) -> tuple:
        """Stop VPN. Returns (success, message)."""
        self._user_wants_connected = False
        return disconnect_wireguard(self.config_path)

    def is_connected(self) -> bool:
        return is_vpn_connected()

    def _start_kill_switch_thread(self) -> None:
        self._stop.clear()
        self._thread = threading.Thread(target=self._kill_switch_loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        self._user_wants_connected = False
        if self._thread:
            self._thread.join(timeout=5.0)
            self._thread = None

    def _kill_switch_loop(self) -> None:
        while not self._stop.is_set():
            self._stop.wait(timeout=self.check_interval)
            if self._stop.is_set():
                break
            if not self._user_wants_connected or not self.kill_switch:
                continue
            if not is_vpn_connected():
                try:
                    self.on_vpn_down()
                except Exception:
                    pass
