"""
YARA-based detection. Use rules from MalwareBazaar or Yara-Rules.
Start with 500+ rules from https://bazaar.abuse.ch/ (export YARA).
"""

from pathlib import Path
from typing import List, Optional

# ThreatResult from parent
import sys
_parent = Path(__file__).resolve().parent.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))
from threat_engine import ThreatResult


def _load_yara():
    try:
        import yara
        return yara
    except ImportError:
        return None


def get_yara_rules_dir() -> Path:
    """Default directory for YARA rules (e.g. MalwareBazaar export)."""
    if sys.platform == "win32":
        base = Path(__file__).resolve().parent.parent
    else:
        base = Path(__file__).resolve().parent.parent
    return base / "yara_rules"


def scan_file_yara(
    filepath: str,
    rules_dir: Optional[Path] = None,
    compiled_rules_path: Optional[Path] = None,
) -> ThreatResult:
    """
    Scan file with YARA. Uses rules_dir (directory of .yar files) or
    a single compiled .yarc / rules file at compiled_rules_path.
    """
    yara = _load_yara()
    if yara is None:
        return ThreatResult(
            is_threat=False,
            threat_type="safe",
            severity="low",
            confidence=0,
            message="YARA not installed (pip install yara-python); skipping YARA scan",
            details={"yara_available": False},
        )

    path = Path(filepath)
    if not path.exists() or not path.is_file():
        return ThreatResult(
            is_threat=False,
            threat_type="error",
            severity="low",
            confidence=0,
            message="File not found",
            details={"filepath": filepath},
        )

    rules_dir = rules_dir or get_yara_rules_dir()
    try:
        if compiled_rules_path and compiled_rules_path.exists():
            rules = yara.load(str(compiled_rules_path))
        elif rules_dir.exists():
            yar_files = list(rules_dir.glob("*.yar")) + list(rules_dir.glob("*.yara"))
            if not yar_files:
                return ThreatResult(
                    is_threat=False,
                    threat_type="safe",
                    severity="low",
                    confidence=0,
                    message="No YARA rules found; add .yar files to yara_rules/ or MalwareBazaar export",
                    details={"rules_dir": str(rules_dir)},
                )
            # Compile from file list (paths dict for yara.compile)
            paths = {f"rule_{i}": str(p) for i, p in enumerate(yar_files[:500])}
            rules = yara.compile(filepaths=paths)
        else:
            return ThreatResult(
                is_threat=False,
                threat_type="safe",
                severity="low",
                confidence=0,
                message="YARA rules directory not found",
                details={"rules_dir": str(rules_dir)},
            )

        matches = rules.match(str(path))
        if matches:
            names = [m.rule for m in matches]
            return ThreatResult(
                is_threat=True,
                threat_type="malware",
                severity="high",
                confidence=90,
                message=f"YARA match: {', '.join(names[:5])}{'...' if len(names) > 5 else ''}",
                details={"yara_rules": names, "filepath": filepath},
            )
        return ThreatResult(
            is_threat=False,
            threat_type="safe",
            severity="low",
            confidence=85,
            message="No YARA matches",
            details={"filepath": filepath},
        )
    except Exception as e:
        return ThreatResult(
            is_threat=False,
            threat_type="error",
            severity="low",
            confidence=0,
            message=f"YARA scan error: {e}",
            details={"filepath": filepath, "error": str(e)},
        )


def ensure_yara_rules_dirs() -> Path:
    """Create yara_rules dir and optional malwarebazaar subdir."""
    d = get_yara_rules_dir()
    d.mkdir(parents=True, exist_ok=True)
    (d / "malwarebazaar").mkdir(exist_ok=True)
    return d
