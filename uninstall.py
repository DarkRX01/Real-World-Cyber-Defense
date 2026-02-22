#!/usr/bin/env python3
"""
Cyber Defense uninstaller.

Windows-focused, best-effort:
- Removes firewall rules created by the VPN kill-switch
- Removes scheduled tasks (if used)
- Removes registry autorun entries
- Optionally deletes the quarantine folder
- Deletes config/logs under %APPDATA%\\.cyber-defense
- Schedules removal of the app folder itself (self-deleting pattern on Windows)
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path
from typing import Tuple


APP_ROOT = Path(getattr(sys, "frozen", False) and sys.executable or __file__).resolve().parent
APPDATA_DIR = Path(os.environ.get("APPDATA", os.path.expanduser("~"))) / ".cyber-defense"
QUARANTINE_DIR = APPDATA_DIR / "quarantine"


def _run_hidden(cmd: list[str], timeout: int = 15) -> Tuple[int, str]:
    """Run a command with hidden console on Windows; normal on others."""
    startupinfo = None
    creationflags = 0
    if sys.platform == "win32":
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            startupinfo=startupinfo,
            creationflags=creationflags,
        )
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode, out.strip()
    except Exception as e:
        return 1, str(e)


def remove_firewall_rules():
    """Remove Windows Firewall rules that may have been created by the app."""
    rule_names = [
        "CyberDefense KillSwitch (Outbound Block)",
        "Cyber Defense",  # placeholder for any future custom rules
    ]
    for name in rule_names:
        _run_hidden(
            [
                "netsh",
                "advfirewall",
                "firewall",
                "delete",
                "rule",
                f"name={name}",
            ],
            timeout=10,
        )


def remove_scheduled_tasks():
    """Remove any scheduled tasks the app might have registered (if any)."""
    if sys.platform != "win32":
        return
    task_names = [
        "CyberDefenseUpdate",
        "CyberDefenseStartup",
    ]
    for t in task_names:
        _run_hidden(["schtasks", "/Delete", "/TN", t, "/F"], timeout=10)


def remove_registry_autorun():
    """Remove autorun entries for Cyber Defense, if present."""
    if sys.platform != "win32":
        return
    try:
        import winreg
    except ImportError:
        return

    run_keys = [
        (winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Run"),
    ]
    value_names = ["CyberDefense", "Cyber Defense"]

    for hive, subkey in run_keys:
        try:
            key = winreg.OpenKey(hive, subkey, 0, winreg.KEY_ALL_ACCESS)
        except OSError:
            continue
        for name in value_names:
            try:
                winreg.DeleteValue(key, name)
            except OSError:
                pass
        winreg.CloseKey(key)


def prompt_yes_no(question: str) -> bool:
    try:
        answer = input(f"{question} [y/N]: ").strip().lower()
        return answer in ("y", "yes")
    except EOFError:
        return False


def delete_quarantine():
    if QUARANTINE_DIR.exists():
        if prompt_yes_no(
            f"Delete quarantine folder at {QUARANTINE_DIR}? "
            "Files cannot be restored after this."
        ):
            shutil.rmtree(QUARANTINE_DIR, ignore_errors=True)


def delete_app_root():
    """
    Self-delete pattern: spawn cmd that waits briefly, then deletes our folder.
    On non-Windows we simply try to delete the folder directly.
    """
    if sys.platform != "win32":
        shutil.rmtree(APP_ROOT, ignore_errors=True)
        return

    cmd = f'cmd /C ping 127.0.0.1 -n 3 >NUL & rmdir /S /Q "{APP_ROOT}"'
    _run_hidden(["cmd.exe", "/C", cmd], timeout=5)


def main() -> int:
    print("Cyber Defense – Uninstaller\n")

    print("Cleaning firewall rules...")
    remove_firewall_rules()

    print("Cleaning scheduled tasks...")
    remove_scheduled_tasks()

    print("Cleaning autorun entries...")
    remove_registry_autorun()

    delete_quarantine()

    if APPDATA_DIR.exists():
        print(f"Removing config/logs at {APPDATA_DIR}...")
        shutil.rmtree(APPDATA_DIR, ignore_errors=True)

    print(f"Scheduling removal of application folder at {APP_ROOT}...")
    delete_app_root()

    print("\nUninstall complete. You can now close this window.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

