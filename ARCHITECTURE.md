# Architecture & Technical Documentation

## System Overview

Real-World Cyber Defense is a Chrome extension built with Manifest V3 that provides real-time threat detection and privacy protection through multi-layered scanning.

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     CHROME BROWSER                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         BACKGROUND SERVICE WORKER                    │  │
│  │  (background.js)                                     │  │
│  │                                                      │  │
│  │  ├─ URL Request Interceptor                         │  │
│  │  ├─ Threat Scanner                                  │  │
│  │  ├─ Tracker Detector                                │  │
│  │  ├─ Download Monitor                                │  │
│  │  └─ Threat Logger (Ephemeral)                       │  │
│  └──────────────────────────────────────────────────────┘  │
│            │              │              │                   │
│            ▼              ▼              ▼                   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐         │
│  │    POPUP     │ │   OPTIONS    │ │ NOTIFICATION │         │
│  │  (popup.js)  │ │(options.js)  │ │   SYSTEM     │         │
│  └──────────────┘ └──────────────┘ └──────────────┘         │
│                                                              │
└─────────────────────────────────────────────────────────────┘
           │
           │ HTTP/HTTPS Requests
           │
┌──────────────────────────────────────┐
│   EXTERNAL APIs                      │
├──────────────────────────────────────┤
│ • Google Safe Browsing API v4        │
│ • VirusTotal API v3 (Optional)       │
│ • Blocklist Sources (Updates)        │
└──────────────────────────────────────┘
```

## Core Components

### 1. Background Service Worker (`background.js`)

The main orchestrator of the extension. Runs continuously in the background.

**Responsibilities:**
- Intercept web requests via Chrome webRequest API
- Route requests through threat scanners
- Manage API calls with rate limiting
- Log detected threats (ephemeral)
- Handle messages from popup/options pages
- Manage user settings

**Key Functions:**
```javascript
// Main interceptor
chrome.webRequest.onBeforeRequest.addListener()

// URL threat scanning
scanUrlForThreats(url)

// Fallback heuristic checks
performHeuristicCheck(url)

// Tracker detection
checkForTracker(url)

// Download analysis
analyzeDownload(download)

// Threat logging
logThreat(threatData)

// Message handler
chrome.runtime.onMessage.addListener()
```

### 2. URL Scanning Engine

**Threat Detection Flow:**
```
1. Intercept Request
   ↓
2. Check Rate Limit
   ↓
3. Query Google Safe Browsing API
   ├─ MATCH FOUND → Log threat
   └─ NO MATCH → Return safe
   
4. If API fails → Fallback to heuristic check
   ├─ Suspicious patterns found → Log threat
   └─ No patterns → Return safe

5. Based on Alert Level:
   ├─ LOW: Notify only
   ├─ MEDIUM: Notify + block critical
   └─ HIGH: Block all
```

**Heuristic Patterns Checked:**
- Phishing keywords without HTTPS
- Suspicious IP addresses
- Known malware URL patterns
- Credential submission on non-HTTPS

### 3. Tracker Detection Module

**Blocklist:**
Built-in list of known tracking domains:
- Google Analytics (`analytics.google.com`)
- Facebook pixels (`connect.facebook.net`)
- Twitter tracking (`analytics.twitter.com`)
- DoubleClick ads (`doubleclick.net`)
- And 20+ more

**Detection Logic:**
```
1. Extract hostname from request
2. Check if matches tracker blocklist
3. If third-party → Mark as tracker
4. Apply privacy mode rules:
   ├─ BALANCED: Notify only
   └─ STRICT: Block request
```

### 4. Download Scanner

**Scanning Checklist:**
- [ ] File extension in dangerous list?
- [ ] Downloaded from trusted domain?
- [ ] From shortened URL service?
- [ ] Filename matches suspicious patterns?

**Dangerous Extensions:**
`.exe`, `.bat`, `.cmd`, `.vbs`, `.msi`, `.ps1`, `.dll`, `.scr`, `.jar`, and 8 more

### 5. Threat Logger (Ephemeral)

**Architecture:**
- In-memory array: `THREAT_LOG = []`
- Max entries: 100
- Retention: Until browser close
- Exposed via: `chrome.runtime.onMessage`

**Data Structure:**
```javascript
{
  type: 'malware|phishing|tracker|suspicious_download',
  url: 'https://example.com/malicious',
  severity: 'low|medium|high',
  threat: 'THREAT_TYPE',
  timestamp: '2024-01-27T10:30:00.000Z'
}
```

## User Interface Components

### Popup Interface

**Files:**
- `popup.html` - UI structure
- `popup.css` - Styling (gradient design)
- `popup.js` - Interactivity

**Features:**
- Status display (threat detection, trackers, downloads)
- Quick action buttons (toggle features, open settings)
- Recent threats list (last 10)
- Clear log button
- Auto-refresh (every 2 seconds)

**Message Protocol:**
```javascript
// Get threat log
{ action: 'getThreatLog' }
→ { threatLog: [...] }

// Clear log
{ action: 'clearThreatLog' }
→ { success: true }

// Get settings
{ action: 'getSettings' }
→ { settings: {...} }

// Update settings
{ action: 'updateSettings', data: {...} }
→ { success: true }
```

### Options Page

**Files:**
- `options.html` - Settings form
- `options.css` - Settings styling
- `options.js` - Settings logic

**Sections:**
1. API Keys (Google, VirusTotal)
2. Alert Levels (Low, Medium, High)
3. Privacy Mode (Balanced, Strict)
4. Feature Toggles (Trackers, Downloads, Logging)
5. Information section

**Storage:**
All settings saved to `chrome.storage.sync`:
- `apiKeyGoogle` - Main API key
- `apiKeyVirusTotal` - Optional secondary API
- `alertLevel` - Alert severity level
- `enableTrackerDetection` - Boolean
- `enableDownloadScanning` - Boolean
- `privacyMode` - Privacy setting
- `enableLogging` - Logging enabled flag

## API Integration

### Google Safe Browsing API v4

**Endpoint:**
```
POST https://safebrowsing.googleapis.com/v4/threatMatches:find
```

**Request Payload:**
```javascript
{
  client: {
    clientId: 'cyber-defense-extension',
    clientVersion: '1.0.0'
  },
  threatInfo: {
    threatTypes: ['MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE', 'POTENTIALLY_HARMFUL_APPLICATION'],
    platformTypes: ['ALL_PLATFORMS'],
    threatEntryTypes: ['URL'],
    threatEntries: [{ url: 'https://example.com' }]
  }
}
```

**Response (Match Found):**
```javascript
{
  matches: [
    {
      threatType: 'SOCIAL_ENGINEERING',
      platformType: 'ALL_PLATFORMS',
      threatEntryType: 'URL',
      threat: { url: 'https://example.com' }
    }
  ]
}
```

**Rate Limiting:**
- 1 request per second (built-in delay)
- Prevents API quota exhaustion
- Falls back to heuristic check if limit hit

### VirusTotal API v3 (Optional)

**Endpoint:**
```
GET https://www.virustotal.com/api/v3/urls/{url_id}
```

**Rate Limiting:**
- Free tier: 4 requests per minute
- Extension respects this automatically

## Data Flow

### Threat Detection Flow

```
User visits website
         ↓
webRequest intercepted
         ↓
─────────────────────────
│ Is it a tracker?      │
├─────────────────────  │
│ Privacy mode = strict │ → BLOCK
└─────────────────────  │
         ↓
Rate limit check
         ↓
─────────────────────────
│ Call Safe Browsing?   │
├─────────────────────  │
│ Yes (≥1s since last)  │
└─────────────────────  │
         ↓
Query Safe Browsing API
         ↓
─────────────────────────
│ Threat found?         │
├─────────────────────  │
│ Yes → Log + Notify    │ → BLOCK (if high alert)
│ No  → Continue        │
└─────────────────────  │
         ↓
Heuristic fallback (if API fails)
         ↓
─────────────────────────
│ Suspicious patterns?  │
├─────────────────────  │
│ Yes → Log + Notify    │ → BLOCK (if high alert)
│ No  → Allow request   │
└─────────────────────  │
```

## Security Considerations

### Threat Model

**Assumes:**
- Chrome is patched and up-to-date
- User's system is not compromised
- Google Safe Browsing API is reliable

**Out of Scope:**
- Zero-day exploits
- Novel phishing techniques not in Google's database
- Network-level attacks (MitM, DNS hijacking)

### API Key Security

- Stored locally in `chrome.storage.sync`
- Never logged to console in production
- Never sent to third parties
- User obtains themselves (not distributed with extension)

### Privacy

- **No tracking:** User URLs not sent anywhere except Safe Browsing API
- **No storage:** Threat logs cleared on browser close
- **No accounts:** No user authentication or profiles
- **No cloud:** All processing happens locally

## Performance Optimization

### Rate Limiting Strategy

```javascript
const API_CALL_INTERVAL_MS = 1000; // 1 second minimum
if (Date.now() - lastApiCallTime < API_CALL_INTERVAL_MS) {
  // Use cached/heuristic result instead
  return performHeuristicCheck(url);
}
```

### Memory Management

```javascript
// Keep log bounded
const MAX_LOG_ENTRIES = 100;
if (THREAT_LOG.length > MAX_LOG_ENTRIES) {
  THREAT_LOG.shift(); // Remove oldest
}
```

### CPU/Network Impact

- **Minimal:** Only scans requests you make
- **Background:** Service worker doesn't block browsing
- **Efficient:** Reuses API responses when possible

## Error Handling

### API Failures

```
API Call Fails
    ↓
Log error to console
    ↓
Fall back to heuristic check
    ↓
Proceed (fail-open design)
```

**Rationale:** Better to allow a request than block everything if API is down

### Invalid URLs

```
Invalid URL parsed
    ↓
Catch error silently
    ↓
Skip scanning
    ↓
Allow request to proceed
```

## Testing Strategy

### Unit Testing Areas

1. **URL Parsing:** Valid/invalid URLs
2. **Threat Matching:** Signature matching
3. **Rate Limiting:** Request throttling
4. **Heuristic Rules:** Pattern detection
5. **Tracker Detection:** Domain matching

### Integration Testing

1. Safe Browsing API integration
2. Chrome storage sync
3. Notification system
4. Message passing

### Manual Testing

1. Load unpacked extension
2. Test with phishing sites
3. Monitor performance
4. Verify API key handling
5. Test all UI interactions

## Future Enhancements

### Post-MVP Features

1. **Machine Learning:** Advanced heuristics
2. **Enterprise Logging:** Cloud-based threat reporting
3. **Custom Rules:** User-defined threat patterns
4. **Multi-browser:** Firefox, Edge support
5. **Archive Scanning:** ZIP file analysis
6. **Browser Sync:** Settings across devices
7. **Threat Intelligence:** Community threat sharing
8. **Advanced Analytics:** Threat trends and reports

---

For implementation details, see the source code comments in each file.
