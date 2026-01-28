/**
 * Constants - Global configuration and data
 */

// API Configuration
export const API_CONFIG = {
    GOOGLE_SAFE_BROWSING: {
        baseUrl: 'https://safebrowsing.googleapis.com/v4',
        endpoint: '/threatMatches:find',
        rateLimit: 1000, // 1 request per second
        threatTypes: ['MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE', 'POTENTIALLY_HARMFUL_APPLICATION'],
        platformTypes: ['ALL_PLATFORMS'],
        threatEntryTypes: ['URL']
    },
    VIRUS_TOTAL: {
        baseUrl: 'https://www.virustotal.com/api/v3',
        rateLimit: 4000, // 1 request per 4 seconds (free tier)
    }
};

// Alert Levels
export const ALERT_LEVELS = {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high'
};

// Threat Types
export const THREAT_TYPES = {
    MALWARE: 'malware',
    PHISHING: 'phishing',
    UNWANTED_SOFTWARE: 'unwanted_software',
    POTENTIALLY_HARMFUL: 'potentially_harmful',
    TRACKER: 'tracker',
    SUSPICIOUS_DOWNLOAD: 'suspicious_download',
    SUSPICIOUS_ACTIVITY: 'suspicious_activity'
};

// Severity Levels
export const SEVERITY_LEVELS = {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
    CRITICAL: 'critical'
};

// Privacy Modes
export const PRIVACY_MODES = {
    BALANCED: 'balanced',
    STRICT: 'strict'
};

// Storage Keys
export const STORAGE_KEYS = {
    API_KEY_GOOGLE: 'apiKeyGoogle',
    API_KEY_VIRUSTOTAL: 'apiKeyVirusTotal',
    ALERT_LEVEL: 'alertLevel',
    ENABLE_TRACKER_DETECTION: 'enableTrackerDetection',
    ENABLE_DOWNLOAD_SCANNING: 'enableDownloadScanning',
    PRIVACY_MODE: 'privacyMode',
    ENABLE_LOGGING: 'enableLogging',
    THREAT_LOG: 'threatLog'
};

// Logging Configuration
export const LOGGING_CONFIG = {
    MAX_LOG_ENTRIES: 100,
    LOG_RETENTION_MS: null, // Ephemeral - cleared on browser close
    ENABLE_CONSOLE_LOGGING: true
};

// Notification Configuration
export const NOTIFICATION_CONFIG = {
    DEFAULT_ICON: '/icons/shield-128.png',
    TIMEOUT_MS: 10000,
    TYPES: {
        BASIC: 'basic',
        PROGRESS: 'progress',
        LIST: 'list'
    }
};

// Dangerous File Extensions
export const DANGEROUS_EXTENSIONS = [
    '.exe',
    '.bat',
    '.cmd',
    '.com',
    '.pif',
    '.scr',
    '.vbs',
    '.js',
    '.jar',
    '.msi',
    '.msp',
    '.ps1',
    '.dll',
    '.sys',
    '.drv',
    '.ocx'
];

// Archive Types (for future extension)
export const ARCHIVE_TYPES = [
    '.zip',
    '.rar',
    '.7z',
    '.tar',
    '.gz',
    '.iso'
];

// Trusted Domains (for download scanning)
export const TRUSTED_DOMAINS = [
    'github.com',
    'microsoft.com',
    'google.com',
    'mozilla.org',
    'apple.com',
    'docker.com',
    'python.org',
    'nodejs.org',
    'npm.com',
    'wikipedia.org',
    'github.io'
];

// URL Shortener Services (suspicious for downloads)
export const URL_SHORTENERS = [
    'bit.ly',
    'tinyurl.com',
    'goo.gl',
    'ow.ly',
    'short.link',
    'buff.ly',
    'adf.ly'
];

// Heuristic Patterns
export const HEURISTIC_PATTERNS = {
    PHISHING_KEYWORDS: ['login', 'verify', 'confirm', 'update', 'urgent', 'validate', 'authenticate', 'expire', 'password'],
    MALWARE_PATTERNS: [/paypal.*verify/i, /amazon.*account.*confirm/i, /bank.*login/i, /update.*credentials/i],
    SUSPICIOUS_PATTERNS: [/admin\.php/i, /wp-admin/i, /shell\.php/i, /webshell/i]
};

// Extension Metadata
export const EXTENSION_META = {
    NAME: 'Real-World Cyber Defense',
    VERSION: '1.0.0',
    CLIENT_ID: 'cyber-defense-extension',
    CONTACT: 'security@cyberdefense.local'
};

export default {
    API_CONFIG,
    ALERT_LEVELS,
    THREAT_TYPES,
    SEVERITY_LEVELS,
    PRIVACY_MODES,
    STORAGE_KEYS,
    LOGGING_CONFIG,
    NOTIFICATION_CONFIG,
    DANGEROUS_EXTENSIONS,
    ARCHIVE_TYPES,
    TRUSTED_DOMAINS,
    URL_SHORTENERS,
    HEURISTIC_PATTERNS,
    EXTENSION_META
};
