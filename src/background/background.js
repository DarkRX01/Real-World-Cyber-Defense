/**
 * Background Service Worker - Main orchestrator for Cyber Defense extension
 * Handles URL scanning, tracker detection, download monitoring, and threat logging
 */

// Import modules (Note: These will be injected/loaded separately in MV3)
// In MV3, we use dynamic imports or load scripts in manifest

let SETTINGS = {
    apiKeyGoogle: '',
    apiKeyVirusTotal: '',
    alertLevel: 'medium', // 'low', 'medium', 'high'
    enableTrackerDetection: true,
    enableDownloadScanning: true,
    privacyMode: 'balanced', // 'strict', 'balanced'
    enableLogging: true
};

let THREAT_LOG = []; // Ephemeral log, cleared on browser close
const MAX_LOG_ENTRIES = 100;
const API_CALL_INTERVAL_MS = 1000; // Rate limit: 1 request per second
let lastApiCallTime = 0;

// Known tracking domains (built-in blocklist)
const TRACKER_BLOCKLIST = [
    'google-analytics.com',
    'analytics.google.com',
    'googletagmanager.com',
    'facebook.com',
    'facebook.net',
    'connect.facebook.net',
    'cdn.facebook.com',
    'graph.facebook.com',
    'platform.instagram.com',
    'platform.twitter.com',
    'twitter.com',
    'ads.twitter.com',
    'analytics.twitter.com',
    'matomo.org',
    'doubleclick.net',
    'pagead2.googlesyndication.com',
    'adservice.google.com',
    'ads.google.com',
    'amazon-adsystem.com',
    'api.mixpanel.com',
    'segment.com',
    'amplitude.com',
    'app.adjust.com',
    'appsflyer.com'
];

/**
 * Initialize extension - load saved settings from storage
 */
async function initExtension() {
    const stored = await chrome.storage.sync.get(['apiKeyGoogle', 'apiKeyVirusTotal', 'alertLevel', 'enableTrackerDetection', 'enableDownloadScanning', 'privacyMode', 'enableLogging']);

    if (stored.apiKeyGoogle) SETTINGS.apiKeyGoogle = stored.apiKeyGoogle;
    if (stored.apiKeyVirusTotal) SETTINGS.apiKeyVirusTotal = stored.apiKeyVirusTotal;
    if (stored.alertLevel) SETTINGS.alertLevel = stored.alertLevel;
    if (stored.enableTrackerDetection !== undefined) SETTINGS.enableTrackerDetection = stored.enableTrackerDetection;
    if (stored.enableDownloadScanning !== undefined) SETTINGS.enableDownloadScanning = stored.enableDownloadScanning;
    if (stored.privacyMode) SETTINGS.privacyMode = stored.privacyMode;
    if (stored.enableLogging !== undefined) SETTINGS.enableLogging = stored.enableLogging;

    console.log('[Cyber Defense] Extension initialized with settings:', SETTINGS);
}

/**
 * Intercept web requests and scan URLs for threats
 */
chrome.webRequest.onBeforeRequest.addListener(
    async (details) => {
        const url = details.url;
        const tabId = details.tabId;

        // Skip extension internal URLs and data URLs
        if (url.startsWith('chrome-extension://') || url.startsWith('data:')) {
            return { cancel: false };
        }

        // Check for trackers
        if (SETTINGS.enableTrackerDetection) {
            const trackerResult = checkForTracker(url);
            if (trackerResult.isTracker) {
                logThreat({
                    type: 'tracker',
                    url: url,
                    domain: trackerResult.domain,
                    severity: 'low',
                    timestamp: new Date().toISOString()
                });

                if (SETTINGS.privacyMode === 'strict') {
                    // Block tracker in strict mode
                    showNotification('Tracker Blocked', `Blocked tracking domain: ${trackerResult.domain}`);
                    return { cancel: true };
                } else if (SETTINGS.privacyMode === 'balanced') {
                    // Alert only in balanced mode
                    notifyAboutThreat('tracker', trackerResult.domain);
                }
            }
        }

        // Scan URL for malware/phishing
        const threatResult = await scanUrlForThreats(url);

        if (threatResult.isThreat) {
            logThreat({
                type: threatResult.threatType,
                url: url,
                severity: threatResult.severity,
                threat: threatResult.threat,
                timestamp: new Date().toISOString()
            });

            const shouldBlock = shouldBlockRequest(threatResult.severity);

            showNotification(
                `Warning: ${threatResult.threatType.toUpperCase()}`,
                `URL may be ${threatResult.threatType}: ${new URL(url).hostname}`
            );

            if (shouldBlock && SETTINGS.alertLevel === 'high') {
                return { cancel: true };
            }
        }

        return { cancel: false };
    },
    { urls: ['<all_urls>'] },
    ['blocking']
);

/**
 * Monitor downloads for suspicious files
 */
if (SETTINGS.enableDownloadScanning) {
    chrome.downloads.onChanged.addListener(async (downloadDelta) => {
        if (downloadDelta.state && downloadDelta.state.current === 'in_progress') {
            const downloadItem = await chrome.downloads.search({ id: downloadDelta.id });

            if (downloadItem.length > 0) {
                const download = downloadItem[0];
                const downloadResult = analyzeDownload(download);

                if (downloadResult.isSuspicious) {
                    logThreat({
                        type: 'suspicious_download',
                        url: download.url,
                        filename: download.filename,
                        severity: downloadResult.severity,
                        reason: downloadResult.reason,
                        timestamp: new Date().toISOString()
                    });

                    showNotification(
                        'Suspicious Download Detected',
                        `Warning: ${downloadResult.reason}\nFile: ${download.filename}`
                    );

                    if (SETTINGS.alertLevel === 'high') {
                        chrome.downloads.cancel(downloadDelta.id);
                    }
                }
            }
        }
    });
}

/**
 * Scan URL against Google Safe Browsing API
 */
async function scanUrlForThreats(url) {
    // Rate limiting
    const now = Date.now();
    if (now - lastApiCallTime < API_CALL_INTERVAL_MS) {
        // Return cached/heuristic result
        return performHeuristicCheck(url);
    }

    if (!SETTINGS.apiKeyGoogle) {
        // Fallback to heuristic check
        return performHeuristicCheck(url);
    }

    try {
        lastApiCallTime = Date.now();

        // Google Safe Browsing API (Lookup API v4)
        const apiUrl = `https://safebrowsing.googleapis.com/v4/threatMatches:find?key=${SETTINGS.apiKeyGoogle}`;

        const payload = {
            client: {
                clientId: 'cyber-defense-extension',
                clientVersion: '1.0.0'
            },
            threatInfo: {
                threatTypes: ['MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE', 'POTENTIALLY_HARMFUL_APPLICATION'],
                platformTypes: ['ALL_PLATFORMS'],
                threatEntryTypes: ['URL'],
                threatEntries: [{ url: url }]
            }
        };

        const response = await fetch(apiUrl, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            console.error('[Cyber Defense] Google Safe Browsing API error:', response.status);
            return performHeuristicCheck(url);
        }

        const data = await response.json();

        if (data.matches && data.matches.length > 0) {
            const match = data.matches[0];
            return {
                isThreat: true,
                threatType: mapThreatType(match.threatType),
                threat: match.threatType,
                severity: 'high'
            };
        }

        return { isThreat: false };
    } catch (error) {
        console.error('[Cyber Defense] Error scanning URL:', error);
        return performHeuristicCheck(url);
    }
}

/**
 * Fallback heuristic check for URLs
 */
function performHeuristicCheck(url) {
    try {
        const urlObj = new URL(url);
        const hostname = urlObj.hostname.toLowerCase();
        const pathname = urlObj.pathname.toLowerCase();

        // Check for suspicious patterns
        const suspiciousPatterns = [
            /paypal.*verify/i,
            /amazon.*account.*confirm/i,
            /bank.*login/i,
            /update.*credentials/i,
            /verify.*payment/i,
            /confirm.*identity/i
        ];

        // Check hostname against known phishing domains
        const knownPhishingKeywords = ['login', 'verify', 'confirm', 'update', 'urgent'];
        const isOnHTTPS = urlObj.protocol === 'https:';

        for (const pattern of suspiciousPatterns) {
            if (pattern.test(pathname)) {
                if (!isOnHTTPS) {
                    return {
                        isThreat: true,
                        threatType: 'phishing',
                        threat: 'SOCIAL_ENGINEERING',
                        severity: 'high'
                    };
                }
            }
        }

        // Check for suspicious IP addresses (direct IP navigation)
        if (/^\d+\.\d+\.\d+\.\d+$/.test(hostname) && !isOnHTTPS) {
            return {
                isThreat: true,
                threatType: 'suspicious',
                threat: 'SUSPICIOUS_ACTIVITY',
                severity: 'medium'
            };
        }

        return { isThreat: false };
    } catch (error) {
        console.error('[Cyber Defense] Heuristic check error:', error);
        return { isThreat: false };
    }
}

/**
 * Check if URL contains known tracker domain
 */
function checkForTracker(url) {
    try {
        const urlObj = new URL(url);
        const hostname = urlObj.hostname.toLowerCase();

        for (const tracker of TRACKER_BLOCKLIST) {
            if (hostname.includes(tracker) && hostname !== tracker) {
                // It's a third-party tracker
                return { isTracker: true, domain: hostname };
            }
        }

        return { isTracker: false, domain: null };
    } catch (error) {
        console.error('[Cyber Defense] Tracker detection error:', error);
        return { isTracker: false, domain: null };
    }
}

/**
 * Analyze download for suspicious characteristics
 */
function analyzeDownload(download) {
    const filename = download.filename.toLowerCase();
    const url = download.url.toLowerCase();

    // Dangerous file extensions
    const dangerousExtensions = ['.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', '.jar', '.zip'];

    // Suspicious filename patterns
    const suspiciousPatterns = [
        /invoice.*\d+.*exe/,
        /document.*exe/,
        /tax.*form.*exe/,
        /payment.*confirmation.*exe/
    ];

    for (const ext of dangerousExtensions) {
        if (filename.endsWith(ext)) {
            // Check if downloaded from reputable source
            const trustedDomains = ['github.com', 'microsoft.com', 'google.com', 'mozilla.org'];
            const isTrusted = trustedDomains.some(domain => url.includes(domain));

            if (!isTrusted && url.includes('bit.ly') || url.includes('tinyurl')) {
                return {
                    isSuspicious: true,
                    severity: 'high',
                    reason: `Executable from shortened URL`
                };
            }

            if (!isTrusted) {
                return {
                    isSuspicious: true,
                    severity: 'high',
                    reason: `Executable file from untrusted source`
                };
            }
        }
    }

    for (const pattern of suspiciousPatterns) {
        if (pattern.test(filename)) {
            return {
                isSuspicious: true,
                severity: 'high',
                reason: `Suspicious filename pattern detected`
            };
        }
    }

    return { isSuspicious: false };
}

/**
 * Determine if request should be blocked based on threat severity
 */
function shouldBlockRequest(severity) {
    if (SETTINGS.alertLevel === 'high') return true;
    if (SETTINGS.alertLevel === 'medium') return severity === 'critical';
    return false;
}

/**
 * Map Google Safe Browsing threat types to human-readable format
 */
function mapThreatType(threatType) {
    const threatMap = {
        'MALWARE': 'malware',
        'SOCIAL_ENGINEERING': 'phishing',
        'UNWANTED_SOFTWARE': 'unwanted_software',
        'POTENTIALLY_HARMFUL_APPLICATION': 'potentially_harmful'
    };
    return threatMap[threatType] || 'threat';
}

/**
 * Show browser notification for threat
 */
function showNotification(title, message, options = {}) {
    chrome.notifications.create({
        type: 'basic',
        iconUrl: '/icons/shield-128.png',
        title: title,
        message: message,
        ...options
    });
}

/**
 * Notify user about threat (wrapper for showNotification)
 */
function notifyAboutThreat(threatType, domain) {
    showNotification(
        `${threatType.toUpperCase()} Detected`,
        `Potential threat detected: ${domain}`
    );
}

/**
 * Log threat to ephemeral in-memory log
 */
function logThreat(threatData) {
    if (!SETTINGS.enableLogging) return;

    THREAT_LOG.push(threatData);

    // Keep log size manageable
    if (THREAT_LOG.length > MAX_LOG_ENTRIES) {
        THREAT_LOG.shift();
    }

    console.log('[Cyber Defense] Threat logged:', threatData);
}

/**
 * Expose threat log to popup/options pages via message handler
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'getThreatLog') {
        sendResponse({ threatLog: THREAT_LOG });
    } else if (request.action === 'clearThreatLog') {
        THREAT_LOG = [];
        sendResponse({ success: true });
    } else if (request.action === 'getSettings') {
        sendResponse({ settings: SETTINGS });
    } else if (request.action === 'updateSettings') {
        // Update settings (handled by options page)
        Object.assign(SETTINGS, request.data);
        chrome.storage.sync.set(request.data);
        sendResponse({ success: true });
    }
});

// Initialize extension on startup
initExtension();

// Clear threat log on browser close (ephemeral logging)
window.addEventListener('beforeunload', () => {
    THREAT_LOG = [];
    console.log('[Cyber Defense] Threat log cleared on browser close');
});
