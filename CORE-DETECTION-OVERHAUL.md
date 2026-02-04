# Core Detection Engine Overhaul

This document summarizes the **Core Detection Engine** changes: real-time file system monitoring, signature expansion, heuristics, behavioral monitoring, and ransomware protection.

## 1. Real-Time File System Monitoring

- **`realtime_monitor.py`**
  - **`get_default_watch_paths()`** – Returns Downloads, Desktop, Documents, Temp, and user home (platform-aware). Used when real-time monitor is enabled so high-risk dirs are watched 24/7.
  - **Default watch paths** – App now uses these defaults instead of only Downloads/Desktop; Temp and user dirs are included.
- **No test-virus logic** – The real-time monitor focuses on normal detection paths (hash/YARA/PE/entropy/behavioral) and does not include any special test-file handling.
  - **Optional `watch_paths`** – Constructor accepts `watch_paths=None` and falls back to `get_default_watch_paths()`.

- **`threat_engine.py`**
  - **`compute_file_hash(filepath, algorithm="sha256", max_bytes=None)`** – File hash via hashlib for signatures and forensics. Used in comprehensive scan.
  - **`scan_file_comprehensive()`** – Includes SHA256 in `details`, runs PE heuristics before YARA, and returns full `filepath` for UI/logging.

## 2. Signature Database Expansion

- **`signature_updater.py`** (new)
  - **`fetch_yara_rules_github()`** – Downloads Yara-Rules/rules from GitHub (zip), extracts `.yar`/`.yara` into `yara_rules/community`.
  - **`fetch_clamav_daily()` / `fetch_clamav_main()`** – Pulls ClamAV daily/main CVD into `data/`.
  - **`run_signature_updates()`** – Runs YARA + ClamAV updates.
  - **`SignatureUpdateScheduler`** – Background thread for periodic signature updates (e.g. daily).

- **`update_system.py`**
  - **`run_all_updates()`** – Now also calls `run_signature_updates()` so YARA rules from GitHub are updated with existing URLhaus/PhishTank/ClamAV updates.

## 3. Heuristic Analysis (PE)

- **`detection/heuristic_pe.py`** (new)
  - **`scan_file_pe_heuristics(filepath)`** – Uses `pefile` to detect:
    - Packed sections (e.g. `.upx`, `.packed`).
    - High section entropy (≥ 7.5) and high overall file entropy (≥ 7.2/7.8).
  - Returns `ThreatResult` for suspicious PE files; otherwise `None`.
  - **`scan_file_comprehensive()`** calls this for PE files before YARA.

## 4. Behavioral Monitoring

- **`detection/behavioral.py`**
  - **CPU spike detection** – `_check_cpu_spikes()` runs in the same loop as new-process checks. Tracks per-process CPU%; if a process sustains ≥ 90% CPU over several samples, emits an `anomalous_behavior` threat (e.g. mining/encryption).
  - **`check_cpu_spike(pid, threshold_percent)`** – Helper to get current CPU % for a PID if above threshold.
  - **`BehavioralMonitor`** – New optional `cpu_spike_threshold`; same API so existing app integration is unchanged.

## 5. Ransomware Shield

- **`ransomware_shield.py`** (new)
  - **`ensure_honeypot_files()`** – Creates honeypot files (`.cyberdefense_honeypot`) in Downloads, Desktop, Documents.
  - **`get_honeypot_paths()`** / **`is_honeypot_path(filepath)`** – Used by the real-time monitor to detect honeypot access.
  - **`honeypot_threat_result(filepath)`** – Returns a critical `ThreatResult` when a honeypot is touched.
  - **`MassChangeDetector`** – Counts file events in a time window; can alert when count exceeds a threshold (mass encryption).

- **`realtime_monitor.py`**
  - **`_handle_event()`** – First checks if the path is a honeypot; if so, immediately calls `on_threat` with `honeypot_threat_result(path)` and skips normal scan.

- **`app_main.py`**
  - On starting the real-time monitor, calls **`ensure_honeypot_files()`** so honeypots exist in default dirs.

## 6. Anomaly Detection (Simple Baseline)

- **`anomaly_detector.py`** (new)
  - **`SimpleAnomalyDetector`** – Rolling window of event counts per minute; alerts when current rate exceeds a multiple of the median (e.g. unusual file creation rate). Can be fed from the real-time monitor or other event sources. No torch/ML dependency; optional ML baseline can be added later.

## Files Touched / Added

| File | Change |
|------|--------|
| `realtime_monitor.py` | Default watch paths, honeypot check in `_handle_event`, event rate-limiting. |
| `threat_engine.py` | `compute_file_hash()`, comprehensive scan (hash + PE heuristics + YARA + entropy), full `filepath` in results. |
| `app_main.py` | Uses `get_default_watch_paths()`, calls `ensure_honeypot_files()` when starting real-time monitor. |
| `update_system.py` | `run_all_updates()` runs `run_signature_updates()`. |
| `detection/behavioral.py` | CPU spike tracking and `_check_cpu_spikes()`. |
| `detection/heuristic_pe.py` | **New** – PE packed/high-entropy heuristics. |
| `detection/__init__.py` | Exports `scan_file_pe_heuristics`. |
| `signature_updater.py` | **New** – YARA GitHub + ClamAV fetch and scheduler. |
| `ransomware_shield.py` | **New** – Honeypots + mass-change detector. |
| `anomaly_detector.py` | **New** – Simple rate-based anomaly detector. |

## 7. VPN Integration

- **`vpn_client.py`** (new)
  - **WireGuard connect/disconnect** – `connect_wireguard(config_path)` and `disconnect_wireguard(config_path)` via system WireGuard (Windows: `wireguard.exe /installtunnelservice`; Linux: `wg-quick up`).
  - **`VPNClient`** – Holds config path, optional kill-switch, and `on_vpn_down` callback. When kill-switch is on and VPN is expected but drops, calls `on_vpn_down()` (e.g. critical tray notification).
  - **`is_vpn_connected()`** – Best-effort check (psutil net interfaces or `wg show` / netsh).
- **`app_main.py`**
  - Settings: “VPN integration (WireGuard)”, “VPN kill-switch”, VPN config path.
  - Tray menu: “VPN: Connect” and “VPN: Disconnect” when VPN is enabled.
  - On save, creates/updates `_vpn_client` so Connect/Disconnect work without restart.
  - On quit, stops `_vpn_client`.

## Optional / Future

- **Kernel-level watching** – Minifilter (Rust) stub exists; full integration is out of scope for this overhaul.
- **ML anomaly baseline** – `SimpleAnomalyDetector` is stats-based; torch/autoencoder baseline can be added and wired to the same `on_anomaly` callback.
- **Community-submitted sigs** – YARA rules live in `yara_rules/`; users can add custom rules or point to a repo URL in a future config option.
