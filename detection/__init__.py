# Detection modules: YARA, ML, behavioral, PE heuristics
from .yara_engine import scan_file_yara, get_yara_rules_dir
from .behavioral import BehavioralMonitor, is_suspicious_process, get_network_connections_summary
from .heuristic_pe import scan_file_pe_heuristics

__all__ = [
    "scan_file_yara",
    "get_yara_rules_dir",
    "BehavioralMonitor",
    "is_suspicious_process",
    "get_network_connections_summary",
    "scan_file_pe_heuristics",
]
