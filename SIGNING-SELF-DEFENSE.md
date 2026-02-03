# Signing & Self-Defense

## Unsigned + PyInstaller = red flag

Defender and SmartScreen flag unsigned executables, especially PyInstaller-packed. Fix:

### 1. EV code signing certificate

- **Buy:** ~$80–300/year from Sectigo, DigiCert, or similar (EV required for SmartScreen reputation).
- **Sign every build:**
  ```cmd
  signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /f "MyCert.pfx" /p password CyberDefense.exe
  ```
- **Submit to Microsoft:** [SmartScreen submission](https://www.microsoft.com/en-us/wdsi/filesubmission) – submit signed hashes so SmartScreen stops blocking after enough reputation.

### 2. Self-defense: don’t let malware kill the process

- **Run as a protected service** so user-mode malware can’t easily terminate you:
  - **Windows:** Install as a service (e.g. with NSSM) and run as **SYSTEM** or under a dedicated account. Optionally use a watchdog that restarts the process if it exits.
  - **Linux:** `systemd` service with `Restart=on-failure` and correct capabilities.
- **Hooking TerminateProcess** is possible from user mode (e.g. detours) but is fragile and can be detected; better to run as a service and have a separate watchdog process.

### 3. NSSM (Windows service)

```cmd
nssm install CyberDefense "C:\Path\To\CyberDefense.exe" ""
nssm set CyberDefense AppDirectory "C:\Path\To"
sc start CyberDefense
```

Run NSSM as Administrator. The app must support running headless (tray only, no required GUI).

### 4. systemd (Linux)

```ini
[Unit]
Description=Cyber Defense
After=network.target

[Service]
Type=simple
ExecStart=/usr/local/bin/cyber-defense
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 5. What we do in-app

- **Tray-only UI:** No full-screen window by default; Win10-style notifications for critical threats only.
- **Optional real-time monitor:** Event-driven file watch (watchdog / ReadDirectoryChangesW) so we react on create/modify, not every 5 minutes.
- **Quarantine:** Move threats to a quarantine folder with metadata; support restore. No immediate delete.
- **Updates:** Pull ClamAV/PhishTank/URLhaus every 2 hours over HTTPS; optional signature verification.

Until you have an EV cert, document in the installer and README that users may need to add an exclusion in Defender and that the app is unsigned.
