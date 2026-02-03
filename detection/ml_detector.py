"""
Static ML detection: scikit-learn on entropy, file size, PE sections.
Trains on simple features; use pre-trained or train from benign/malicious samples.
"""

import pickle
import sys
from pathlib import Path
from typing import List, Optional
_parent = Path(__file__).resolve().parent.parent
if str(_parent) not in sys.path:
    sys.path.insert(0, str(_parent))
from threat_engine import ThreatResult, calculate_entropy


def _pe_sections(filepath: Path) -> List[dict]:
    """Extract PE section stats (name, entropy, raw size, virtual size)."""
    try:
        import pefile
        pe = pefile.PE(str(filepath), fast_load=True)
        out = []
        for section in pe.sections:
            name = section.Name.decode("utf-8", errors="replace").strip("\x00")
            data = section.get_data()
            ent = calculate_entropy(data) if data else 0.0
            out.append({
                "name": name,
                "entropy": ent,
                "raw_size": section.SizeOfRawData,
                "virtual_size": section.Misc_VirtualSize,
            })
        pe.close()
        return out
    except Exception:
        return []


def extract_features(filepath: str) -> Optional[dict]:
    """
    Extract features for ML: entropy (first 1MB), file size, PE section stats.
    Returns dict with keys: entropy, size, num_sections, max_section_entropy, has_pe.
    """
    path = Path(filepath)
    if not path.exists() or not path.is_file():
        return None
    try:
        size = path.stat().st_size
        with open(path, "rb") as f:
            data = f.read(1024 * 1024)
        entropy = calculate_entropy(data)
        sections = _pe_sections(path)
        has_pe = len(sections) > 0
        max_sec_ent = max((s["entropy"] for s in sections), default=0.0)
        return {
            "entropy": entropy,
            "size": size,
            "num_sections": len(sections),
            "max_section_entropy": max_sec_ent,
            "has_pe": 1 if has_pe else 0,
        }
    except Exception:
        return None


def get_ml_model_path() -> Path:
    return Path(__file__).resolve().parent.parent / "data" / "ml_model.pkl"


def scan_file_ml(
    filepath: str,
    model_path: Optional[Path] = None,
    threshold: float = 0.5,
) -> ThreatResult:
    """
    Run ML classifier on file features. If no model exists, falls back to
    heuristic: high entropy + PE with high section entropy = suspicious.
    """
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

    model_path = model_path or get_ml_model_path()
    features = extract_features(filepath)
    if features is None:
        return ThreatResult(
            is_threat=False,
            threat_type="error",
            severity="low",
            confidence=0,
            message="Could not extract features",
            details={"filepath": filepath},
        )

    try:
        if model_path.exists():
            with open(model_path, "rb") as f:
                obj = pickle.load(f)
            # Expect dict with 'model' and 'feature_order'
            model = obj.get("model")
            order = obj.get("feature_order", ["entropy", "size", "num_sections", "max_section_entropy", "has_pe"])
            if model is not None and order:
                X = [[features.get(k, 0) for k in order]]
                proba = getattr(model, "predict_proba", None)
                if proba is not None:
                    pred = model.predict_proba(X)[0]
                    # Assume second class is malicious (index 1)
                    mal_prob = float(pred[1] if len(pred) > 1 else pred[0])
                else:
                    mal_prob = float(model.predict(X)[0])
                if mal_prob >= threshold:
                    return ThreatResult(
                        is_threat=True,
                        threat_type="suspicious_file",
                        severity="high" if mal_prob >= 0.8 else "medium",
                        confidence=int(mal_prob * 100),
                        message=f"ML classifier flagged file (score={mal_prob:.2f})",
                        details={"features": features, "score": mal_prob},
                    )
                return ThreatResult(
                    is_threat=False,
                    threat_type="safe",
                    severity="low",
                    confidence=int((1 - mal_prob) * 100),
                    message="ML: no threat",
                    details={"score": mal_prob},
                )
    except Exception as e:
        pass  # fall through to heuristic

    # Heuristic fallback: high entropy + PE with high section entropy
    if features["entropy"] >= 7.2 and features.get("max_section_entropy", 0) >= 7.0:
        return ThreatResult(
            is_threat=True,
            threat_type="suspicious_file",
            severity="medium",
            confidence=70,
            message="High entropy and PE section entropy (packed/encrypted)",
            details=features,
        )
    if features["entropy"] >= 7.8:
        return ThreatResult(
            is_threat=True,
            threat_type="suspicious_file",
            severity="medium",
            confidence=65,
            message="Very high entropy (likely packed)",
            details=features,
        )
    return ThreatResult(
        is_threat=False,
        threat_type="safe",
        severity="low",
        confidence=85,
        message="ML heuristic: no threat",
        details=features,
    )
