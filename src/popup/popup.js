/**
 * Popup Script - Handles popup UI interactions and threat display
 */

// Load threat log and display
function loadThreatLog() {
    chrome.runtime.sendMessage({ action: 'getThreatLog' }, (response) => {
        const threatsList = document.getElementById('threatsList');

        if (!response || !response.threatLog || response.threatLog.length === 0) {
            threatsList.innerHTML = '<p class="no-threats">No threats detected yet.</p>';
            return;
        }

        // Sort threats by most recent first
        const sortedThreats = response.threatLog.sort((a, b) => {
            return new Date(b.timestamp) - new Date(a.timestamp);
        });

        // Display most recent 10 threats
        threatsList.innerHTML = sortedThreats.slice(0, 10).map(threat => {
            const time = new Date(threat.timestamp).toLocaleTimeString();
            const displayUrl = threat.url || threat.domain || 'Unknown';
            const severity = threat.severity ? threat.severity.toUpperCase() : 'UNKNOWN';

            return `
        <div class="threat-item ${threat.type}">
          <span class="threat-type">${threat.type.replace(/_/g, ' ')}</span>
          <span class="threat-severity" style="
            display: inline-block;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            font-weight: 600;
            ${threat.severity === 'high' ? 'background: #fed7d7; color: #742a2a;' :
                    threat.severity === 'medium' ? 'background: #feebc8; color: #7c2d12;' :
                        'background: #c6f6d5; color: #22543d;'}
          ">${severity}</span>
          <div class="threat-url">${escapeHtml(displayUrl.substring(0, 60))}</div>
          <div class="threat-time">${time}</div>
        </div>
      `;
        }).join('');
    });
}

// Load settings and update UI
function loadSettings() {
    chrome.runtime.sendMessage({ action: 'getSettings' }, (response) => {
        if (response && response.settings) {
            const settings = response.settings;

            // Update status badges
            document.getElementById('trackerStatus').textContent =
                settings.enableTrackerDetection ? 'Enabled' : 'Disabled';
            document.getElementById('trackerStatus').className =
                settings.enableTrackerDetection ? 'status-badge online' : 'status-badge offline';

            document.getElementById('downloadStatus').textContent =
                settings.enableDownloadScanning ? 'Enabled' : 'Disabled';
            document.getElementById('downloadStatus').className =
                settings.enableDownloadScanning ? 'status-badge online' : 'status-badge offline';
        }
    });
}

// Toggle tracker detection
document.getElementById('toggleTrackers').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'getSettings' }, (response) => {
        const newState = !response.settings.enableTrackerDetection;
        chrome.runtime.sendMessage({
            action: 'updateSettings',
            data: { enableTrackerDetection: newState }
        }, () => {
            loadSettings();
        });
    });
});

// Toggle download scanning
document.getElementById('toggleDownloadScanning').addEventListener('click', () => {
    chrome.runtime.sendMessage({ action: 'getSettings' }, (response) => {
        const newState = !response.settings.enableDownloadScanning;
        chrome.runtime.sendMessage({
            action: 'updateSettings',
            data: { enableDownloadScanning: newState }
        }, () => {
            loadSettings();
        });
    });
});

// Open settings page
document.getElementById('openSettings').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
});

// Clear threat log
document.getElementById('clearLog').addEventListener('click', () => {
    if (confirm('Clear all threat logs? This action cannot be undone.')) {
        chrome.runtime.sendMessage({ action: 'clearThreatLog' }, () => {
            loadThreatLog();
        });
    }
});

// Utility function to escape HTML characters
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load initial data
loadThreatLog();
loadSettings();

// Refresh threat log every 2 seconds
setInterval(loadThreatLog, 2000);
