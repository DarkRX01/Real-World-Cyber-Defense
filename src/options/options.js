/**
 * Options Script - Handles settings page logic
 */

// Default settings
const DEFAULT_SETTINGS = {
    apiKeyGoogle: '',
    apiKeyVirusTotal: '',
    alertLevel: 'medium',
    enableTrackerDetection: true,
    enableDownloadScanning: true,
    privacyMode: 'balanced',
    enableLogging: true
};

// Load settings on page load
document.addEventListener('DOMContentLoaded', loadSettings);

// Save settings when save button is clicked
document.getElementById('saveButton').addEventListener('click', saveSettings);

// Reset to defaults
document.getElementById('resetButton').addEventListener('click', resetToDefaults);

/**
 * Load settings from Chrome storage and populate form
 */
function loadSettings() {
    chrome.storage.sync.get(DEFAULT_SETTINGS, (items) => {
        // Load API keys
        document.getElementById('apiKeyGoogle').value = items.apiKeyGoogle || '';
        document.getElementById('apiKeyVirusTotal').value = items.apiKeyVirusTotal || '';

        // Load alert level
        const alertLevelRadios = document.querySelectorAll('input[name="alertLevel"]');
        alertLevelRadios.forEach(radio => {
            radio.checked = radio.value === (items.alertLevel || 'medium');
        });

        // Load privacy mode
        const privacyModeRadios = document.querySelectorAll('input[name="privacyMode"]');
        privacyModeRadios.forEach(radio => {
            radio.checked = radio.value === (items.privacyMode || 'balanced');
        });

        // Load checkboxes
        document.getElementById('enableTrackerDetection').checked =
            items.enableTrackerDetection !== false;
        document.getElementById('enableDownloadScanning').checked =
            items.enableDownloadScanning !== false;
        document.getElementById('enableLogging').checked =
            items.enableLogging !== false;
    });
}

/**
 * Save settings to Chrome storage
 */
function saveSettings() {
    // Validate API key input
    const apiKeyGoogle = document.getElementById('apiKeyGoogle').value.trim();

    if (apiKeyGoogle && apiKeyGoogle.length < 10) {
        showStatus('Invalid Google API key format', 'error');
        return;
    }

    const settings = {
        apiKeyGoogle: apiKeyGoogle,
        apiKeyVirusTotal: document.getElementById('apiKeyVirusTotal').value.trim(),
        alertLevel: document.querySelector('input[name="alertLevel"]:checked').value,
        enableTrackerDetection: document.getElementById('enableTrackerDetection').checked,
        enableDownloadScanning: document.getElementById('enableDownloadScanning').checked,
        privacyMode: document.querySelector('input[name="privacyMode"]:checked').value,
        enableLogging: document.getElementById('enableLogging').checked
    };

    // Save to Chrome storage
    chrome.storage.sync.set(settings, () => {
        // Also notify background script of changes
        chrome.runtime.sendMessage({
            action: 'updateSettings',
            data: settings
        }, () => {
            showStatus('✓ Settings saved successfully!', 'success');
            setTimeout(() => {
                showStatus('');
            }, 3000);
        });
    });
}

/**
 * Reset settings to defaults
 */
function resetToDefaults() {
    if (confirm('Reset all settings to defaults? This cannot be undone.')) {
        chrome.storage.sync.set(DEFAULT_SETTINGS, () => {
            loadSettings();
            showStatus('✓ Settings reset to defaults', 'success');

            // Notify background script
            chrome.runtime.sendMessage({
                action: 'updateSettings',
                data: DEFAULT_SETTINGS
            });

            setTimeout(() => {
                showStatus('');
            }, 3000);
        });
    }
}

/**
 * Show save status message
 */
function showStatus(message, type) {
    const statusEl = document.getElementById('saveStatus');
    statusEl.textContent = message;
    statusEl.className = `save-status ${type}`;
}

/**
 * Auto-save on input changes (debounced)
 */
let saveTimeout;
const inputs = document.querySelectorAll(
    'input[type="text"], input[type="password"], input[type="radio"], input[type="checkbox"]'
);

inputs.forEach(input => {
    input.addEventListener('change', () => {
        clearTimeout(saveTimeout);
        saveTimeout = setTimeout(saveSettings, 1000);
    });
});

// Clear save status after 5 seconds
setInterval(() => {
    const statusEl = document.getElementById('saveStatus');
    if (statusEl.textContent && !statusEl.textContent.includes('Error')) {
        // Auto-clear after some time
    }
}, 5000);
