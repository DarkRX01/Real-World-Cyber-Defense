/**
 * Helper Functions - Utility functions for common operations
 */

/**
 * Parse URL safely
 */
export function parseUrlSafely(urlString) {
    try {
        return new URL(urlString);
    } catch (error) {
        console.error('[Cyber Defense] Invalid URL:', urlString, error);
        return null;
    }
}

/**
 * Extract domain from URL
 */
export function extractDomain(urlString) {
    const url = parseUrlSafely(urlString);
    return url ? url.hostname : null;
}

/**
 * Check if URL is HTTPS
 */
export function isHttps(urlString) {
    const url = parseUrlSafely(urlString);
    return url ? url.protocol === 'https:' : false;
}

/**
 * Check if string is valid IP address
 */
export function isIpAddress(str) {
    const ipv4Regex = /^(\d{1,3}\.){3}\d{1,3}$/;
    const ipv6Regex = /^(([0-9a-fA-F]{1,4}:){7,7}[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,7}:|([0-9a-fA-F]{1,4}:){1,6}:[0-9a-fA-F]{1,4}|([0-9a-fA-F]{1,4}:){1,5}(:[0-9a-fA-F]{1,4}){1,2}|([0-9a-fA-F]{1,4}:){1,4}(:[0-9a-fA-F]{1,4}){1,3}|([0-9a-fA-F]{1,4}:){1,3}(:[0-9a-fA-F]{1,4}){1,4}|([0-9a-fA-F]{1,4}:){1,2}(:[0-9a-fA-F]{1,4}){1,5}|[0-9a-fA-F]{1,4}:((:[0-9a-fA-F]{1,4}){1,6})|:((:[0-9a-fA-F]{1,4}){1,7}|:)|fe80:(:[0-9a-fA-F]{0,4}){0,4}%[0-9a-zA-Z]{1,}|::(ffff(:0{1,4}){0,1}:){0,1}((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])|([0-9a-fA-F]{1,4}:){1,4}:((25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9])\.){3,3}(25[0-5]|(2[0-4]|1{0,1}[0-9]){0,1}[0-9]))$/;

    return ipv4Regex.test(str) || ipv6Regex.test(str);
}

/**
 * Check if domain is third-party (not first-party)
 */
export function isThirdPartyDomain(mainDomain, checkDomain) {
    const main = mainDomain.toLowerCase().split('.').slice(-2).join('.');
    const check = checkDomain.toLowerCase().split('.').slice(-2).join('.');
    return main !== check;
}

/**
 * Format timestamp to readable string
 */
export function formatTimestamp(isoString) {
    try {
        const date = new Date(isoString);
        return date.toLocaleTimeString();
    } catch (error) {
        return 'Unknown time';
    }
}

/**
 * Truncate string to max length
 */
export function truncateString(str, maxLength = 60) {
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
}

/**
 * Escape HTML special characters
 */
export function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * Debounce function
 */
export function debounce(func, delay = 300) {
    let timeoutId;
    return (...args) => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

/**
 * Throttle function
 */
export function throttle(func, limit = 1000) {
    let inThrottle;
    return (...args) => {
        if (!inThrottle) {
            func(...args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Deep clone object
 */
export function deepClone(obj) {
    return JSON.parse(JSON.stringify(obj));
}

/**
 * Merge objects
 */
export function mergeObjects(target, source) {
    return { ...target, ...source };
}

/**
 * Check if string matches pattern
 */
export function matchesPattern(str, patterns) {
    return patterns.some(pattern => {
        if (pattern instanceof RegExp) {
            return pattern.test(str);
        }
        return str.toLowerCase().includes(pattern.toLowerCase());
    });
}

/**
 * Generate unique ID
 */
export function generateId() {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
}

/**
 * Sleep function (promise-based)
 */
export function sleep(ms = 1000) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Check if object is empty
 */
export function isEmpty(obj) {
    return Object.keys(obj).length === 0;
}

/**
 * Get file extension
 */
export function getFileExtension(filename) {
    const lastDot = filename.lastIndexOf('.');
    return lastDot > 0 ? filename.substring(lastDot).toLowerCase() : '';
}

/**
 * Check if file extension is dangerous
 */
export function isDangerousExtension(ext, dangerousList) {
    return dangerousList.some(dangerous => ext.toLowerCase() === dangerous.toLowerCase());
}

/**
 * Sanitize URL for display
 */
export function sanitizeUrl(url) {
    try {
        const urlObj = new URL(url);
        return `${urlObj.protocol}//${urlObj.hostname}${urlObj.pathname.substring(0, 40)}`;
    } catch {
        return truncateString(url);
    }
}

export default {
    parseUrlSafely,
    extractDomain,
    isHttps,
    isIpAddress,
    isThirdPartyDomain,
    formatTimestamp,
    truncateString,
    escapeHtml,
    debounce,
    throttle,
    deepClone,
    mergeObjects,
    matchesPattern,
    generateId,
    sleep,
    isEmpty,
    getFileExtension,
    isDangerousExtension,
    sanitizeUrl
};
