"""
YARA-based detection with curated rules and custom rule support.
Loads high-confidence rules from curated_ruleset.yaml and custom rules from
~/.cyber-defense/custom_rules/ directory.
"""

from pathlib import Path
from typing import List, Optional, Dict, Tuple
import logging
import yaml

# ThreatResult from parent
import sys
_parent = Path(__file__).resolve().parent.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))
from threat_engine import ThreatResult

_log = logging.getLogger("CyberDefense.YARAEngine")


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


def get_custom_rules_dir() -> Path:
    """Get custom rules directory path (~/.cyber-defense/custom_rules/)."""
    return Path.home() / ".cyber-defense" / "custom_rules"


def load_curated_ruleset() -> Dict:
    """Load curated ruleset configuration from YAML file."""
    ruleset_path = get_yara_rules_dir() / "curated_ruleset.yaml"
    if not ruleset_path.exists():
        _log.warning(f"Curated ruleset not found at {ruleset_path}")
        return {}
    
    try:
        with open(ruleset_path, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception as e:
        _log.error(f"Failed to load curated ruleset: {e}")
        return {}


def get_enabled_rules_from_curated() -> List[str]:
    """Get list of enabled rules from curated ruleset."""
    ruleset = load_curated_ruleset()
    enabled_rules = []
    
    for rule in ruleset.get("rules", []):
        if rule.get("enabled", True):
            enabled_rules.append(rule.get("id", ""))
    
    return [r for r in enabled_rules if r]


def get_custom_rules_files() -> List[Path]:
    """Get list of custom YARA rule files from custom rules directory."""
    custom_dir = get_custom_rules_dir()
    if not custom_dir.exists():
        return []
    
    yar_files = list(custom_dir.glob("*.yar")) + list(custom_dir.glob("*.yara"))
    return sorted(yar_files)


def scan_file_yara(
    filepath: str,
    rules_dir: Optional[Path] = None,
    compiled_rules_path: Optional[Path] = None,
    include_custom_rules: bool = True,
) -> ThreatResult:
    """
    Scan file with YARA using curated rules and custom rules.
    
    Args:
        filepath: Path to file to scan
        rules_dir: Directory containing YARA rule files (default: yara_rules/)
        compiled_rules_path: Path to pre-compiled YARA rules (.yarc)
        include_custom_rules: Whether to include custom rules from ~/.cyber-defense/custom_rules/
    
    Returns:
        ThreatResult with detection status and details
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
        rules_to_compile = {}
        
        # Load from compiled rules if available
        if compiled_rules_path and compiled_rules_path.exists():
            rules = yara.load(str(compiled_rules_path))
        else:
            # Collect curated rules from rules_dir
            if rules_dir.exists():
                yar_files = list(rules_dir.glob("*.yar")) + list(rules_dir.glob("*.yara"))
                for i, rule_file in enumerate(yar_files[:500]):
                    rules_to_compile[f"curated_{i}"] = str(rule_file)
            
            # Collect custom rules if enabled
            if include_custom_rules:
                custom_files = get_custom_rules_files()
                for i, rule_file in enumerate(custom_files[:250]):
                    rules_to_compile[f"custom_{i}"] = str(rule_file)
            
            if not rules_to_compile:
                return ThreatResult(
                    is_threat=False,
                    threat_type="safe",
                    severity="low",
                    confidence=0,
                    message="No YARA rules found; add .yar files to yara_rules/ or ~/.cyber-defense/custom_rules/",
                    details={"rules_dir": str(rules_dir), "custom_dir": str(get_custom_rules_dir())},
                )
            
            rules = yara.compile(filepaths=rules_to_compile)

        matches = rules.match(str(path))
        if matches:
            names = [m.rule for m in matches]
            
            # Calculate confidence based on number of rule matches
            confidence = min(95, 75 + len(names) * 5)
            
            return ThreatResult(
                is_threat=True,
                threat_type="malware",
                severity="high" if confidence >= 85 else "medium",
                confidence=confidence,
                message=f"YARA match: {', '.join(names[:5])}{'...' if len(names) > 5 else ''}",
                details={
                    "yara_rules": names,
                    "filepath": filepath,
                    "rule_count": len(names),
                    "detection_source": "YARA"
                },
            )
        
        return ThreatResult(
            is_threat=False,
            threat_type="safe",
            severity="low",
            confidence=85,
            message="No YARA matches",
            details={"filepath": filepath, "detection_source": "YARA"},
        )
    except Exception as e:
        _log.error(f"YARA scan error for {filepath}: {e}")
        return ThreatResult(
            is_threat=False,
            threat_type="error",
            severity="low",
            confidence=0,
            message=f"YARA scan error: {e}",
            details={"filepath": filepath, "error": str(e)},
        )


def ensure_yara_rules_dirs() -> Path:
    """Create yara_rules and custom_rules directories."""
    d = get_yara_rules_dir()
    d.mkdir(parents=True, exist_ok=True)
    (d / "malwarebazaar").mkdir(exist_ok=True)
    
    # Create custom rules directory
    custom_dir = get_custom_rules_dir()
    custom_dir.mkdir(parents=True, exist_ok=True)
    
    return d
