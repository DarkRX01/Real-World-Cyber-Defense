"""
PE heuristic analysis: packed EXEs, high entropy sections, suspicious section names.
Uses pefile to dissect binaries; rule-based heuristics for zero-day style detection.
"""

import sys
from pathlib import Path
from typing import Optional

_parent = Path(__file__).resolve().parent.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))
from threat_engine import ThreatResult, calculate_entropy


# Packer / suspicious section names (common in malware)
PACKED_SECTION_NAMES = frozenset([
    ".upx", ".packed", ".pelock", ".themida", ".vmprotect",
    ".aspack", ".nspack", ".fsg", ".pepack", ".petite",
    ".winzip", ".mew", ".mpress", ".yoda", ".enigma",
    ".rsrc",  # often repurposed
])
SUSPICIOUS_SECTION_NAMES = frozenset([
    ".text",  # high entropy .text = packed
    ".data", ".rdata", ".idata",
])
ENTROPY_PACKED_THRESHOLD = 7.2
ENTROPY_SECTION_SUSPICIOUS = 7.5


def _load_pe(path: Path):
    try:
        import pefile
        return pefile.PE(str(path), fast_load=True)
    except Exception:
        return None


def scan_file_pe_heuristics(filepath: str) -> Optional[ThreatResult]:
    """
    Scan PE (.exe/.dll/.scr) for packed/suspicious heuristics.
    Returns ThreatResult if threat else None. Caller can skip non-PE files.
    """
    path = Path(filepath)
    if not path.exists() or not path.is_file():
        return None
    suf = path.suffix.lower()
    if suf not in (".exe", ".dll", ".scr", ".sys", ".com"):
        return None

    pe = _load_pe(path)
    if pe is None:
        return None

    try:
        reasons = []
        max_section_entropy = 0.0
        packed_section_count = 0
        high_entropy_sections = []

        for section in pe.sections:
            name = section.Name.decode("utf-8", errors="replace").strip("\x00").lower()
            raw = section.SizeOfRawData
            if raw == 0:
                continue
            try:
                data = section.get_data()
                ent = calculate_entropy(data) if data else 0.0
            except Exception:
                ent = 0.0
            if ent > max_section_entropy:
                max_section_entropy = ent
            if name in PACKED_SECTION_NAMES:
                packed_section_count += 1
                reasons.append(f"packed_section:{name}")
            if ent >= ENTROPY_SECTION_SUSPICIOUS:
                high_entropy_sections.append((name, ent))
                reasons.append(f"high_entropy_section:{name}={ent:.2f}")

        # Overall file entropy (first 1MB)
        try:
            with path.open("rb") as f:
                head = f.read(1024 * 1024)
            file_entropy = calculate_entropy(head)
        except Exception:
            file_entropy = 0.0

        if packed_section_count > 0:
            return ThreatResult(
                is_threat=True,
                threat_type="suspicious_file",
                severity="high",
                confidence=85,
                message=f"PE has packed sections: {', '.join(reasons[:5])}",
                details={
                    "filepath": filepath,
                    "packed_sections": reasons,
                    "max_section_entropy": max_section_entropy,
                    "file_entropy": file_entropy,
                },
            )
        if max_section_entropy >= ENTROPY_SECTION_SUSPICIOUS and file_entropy >= ENTROPY_PACKED_THRESHOLD:
            return ThreatResult(
                is_threat=True,
                threat_type="suspicious_file",
                severity="medium",
                confidence=75,
                message=f"PE has high entropy sections (likely packed): max={max_section_entropy:.2f}",
                details={
                    "filepath": filepath,
                    "max_section_entropy": max_section_entropy,
                    "file_entropy": file_entropy,
                    "high_entropy_sections": high_entropy_sections[:10],
                },
            )
        if file_entropy >= 7.8:
            return ThreatResult(
                is_threat=True,
                threat_type="suspicious_file",
                severity="medium",
                confidence=65,
                message=f"PE has very high overall entropy ({file_entropy:.2f}) - possibly packed",
                details={"filepath": filepath, "file_entropy": file_entropy},
            )
        return None
    finally:
        try:
            pe.close()
        except Exception:
            pass
