"""
Quarantine: move threats to virtual folder with metadata. Optional VSS shadow copy for rollback.
Do not delete immediately — quarantine first, allow rollback.
"""

import hashlib
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Optional Windows VSS via ctypes or subprocess
if sys.platform == "win32":
    try:
        import ctypes
        from ctypes import wintypes
        VSS_AVAILABLE = hasattr(ctypes, "windll")
    except Exception:
        VSS_AVAILABLE = False
else:
    VSS_AVAILABLE = False


def get_quarantine_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("PROGRAMDATA", Path.home()))  # noqa: F821
    else:
        base = Path.home()
    d = base / ".cyber-defense" / "quarantine"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _file_hash(path: Path, size: int = 65536) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read(size))
    return h.hexdigest()


def quarantine_file(
    filepath: str,
    threat_type: str = "unknown",
    threat_message: str = "",
    copy_instead_of_move: bool = True,
) -> Dict[str, Any]:
    """
    Move (or copy) file to quarantine folder. Record metadata for rollback.
    Returns dict with quarantine_path, metadata_path, original_path, checksum.
    """
    path = Path(filepath).resolve()
    if not path.exists() or not path.is_file():
        return {"error": "File not found", "filepath": filepath}

    qdir = get_quarantine_dir()
    # Unique name: timestamp + original name (sanitized)
    safe_name = path.name.replace(" ", "_").replace("..", "_")[:200]
    stamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    base_id = f"{stamp}_{safe_name}"
    q_path = qdir / base_id
    # Avoid overwrite
    idx = 0
    while q_path.exists():
        idx += 1
        q_path = qdir / f"{stamp}_{idx}_{safe_name}"

    checksum = _file_hash(path)
    metadata = {
        "original_path": str(path),
        "original_name": path.name,
        "quarantine_path": str(q_path),
        "threat_type": threat_type,
        "threat_message": threat_message,
        "quarantine_time": datetime.utcnow().isoformat() + "Z",
        "sha256_prefix": checksum[:32],
        "size": path.stat().st_size,
    }

    try:
        if copy_instead_of_move:
            shutil.copy2(path, q_path)
        else:
            shutil.move(str(path), str(q_path))
        meta_path = q_path.with_suffix(q_path.suffix + ".meta.json")
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
    except Exception as e:
        return {"error": str(e), "filepath": filepath}

    return {
        "quarantine_path": str(q_path),
        "metadata_path": str(meta_path),
        "original_path": str(path),
        "checksum": checksum,
        "metadata": metadata,
    }


def list_quarantine() -> List[Dict[str, Any]]:
    """List all quarantined items (from .meta.json files)."""
    qdir = get_quarantine_dir()
    out = []
    for meta_file in qdir.glob("*.meta.json"):
        try:
            with open(meta_file, "r", encoding="utf-8") as f:
                out.append(json.load(f))
        except Exception:
            pass
    return sorted(out, key=lambda x: x.get("quarantine_time", ""), reverse=True)


def restore_from_quarantine(quarantine_path: str) -> Dict[str, Any]:
    """
    Restore file from quarantine to original path (if possible).
    Returns dict with success, message, restored_path.
    """
    q_path = Path(quarantine_path)
    meta_path = q_path.with_suffix(q_path.suffix + ".meta.json")
    if not meta_path.exists():
        return {"success": False, "message": "Metadata not found"}
    try:
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
    except Exception as e:
        return {"success": False, "message": str(e)}

    orig = meta.get("original_path")
    if not orig:
        return {"success": False, "message": "No original_path in metadata"}
    orig_path = Path(orig)
    if orig_path.exists():
        return {"success": False, "message": "Original path already exists; move or rename it first"}

    try:
        orig_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(str(q_path), str(orig_path))
        return {"success": True, "restored_path": orig, "message": "Restored"}
    except Exception as e:
        return {"success": False, "message": str(e)}


def delete_from_quarantine(quarantine_path: str, secure: bool = False) -> Dict[str, Any]:
    """Remove file from quarantine (optionally overwrite before delete for secure wipe)."""
    q_path = Path(quarantine_path)
    meta_path = q_path.with_suffix(q_path.suffix + ".meta.json")
    try:
        if q_path.exists():
            if secure and q_path.is_file():
                with open(q_path, "rb+") as f:
                    length = f.seek(0, 2)
                    f.seek(0)
                    f.write(b"\x00" * min(length, 1024 * 1024))
            q_path.unlink()
        if meta_path.exists():
            meta_path.unlink()
        return {"success": True, "message": "Deleted"}
    except Exception as e:
        return {"success": False, "message": str(e)}


# VSS: document only; actual shadow copy create/restore requires admin + WMI or vssadmin
def create_shadow_copy_volume(volume: str) -> Optional[str]:
    """Create VSS shadow copy for volume. Returns shadow path or None. Requires admin."""
    if not VSS_AVAILABLE or sys.platform != "win32":
        return None
    # Minimal: use vssadmin via subprocess (requires elevated)
    import subprocess
    try:
        r = subprocess.run(
            ["vssadmin", "create", "shadow", f"/For={volume}"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        if r.returncode != 0:
            return None
        # Parse output for shadow path (implementation-specific)
        return None
    except Exception:
        return None
