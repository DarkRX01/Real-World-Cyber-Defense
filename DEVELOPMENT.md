# Development Setup & Contribution Guide

## Local Development Setup

### Prerequisites

- Node.js v14+ (optional, for development tools)
- Chrome v88+
- Git (for version control)
- Text editor or IDE (VS Code recommended)

### Environment Setup

1. **Clone/Extract Repository:**
   ```bash
   cd ~/documents/Blue\ teaming/
   ```

2. **Project Structure:**
   ```
   cyber-defense-extension/
   ├── manifest.json
   ├── README.md
   ├── GETTING_STARTED.md
   ├── ARCHITECTURE.md
   ├── TESTING_GUIDE.md
   ├── DEVELOPMENT.md (this file)
   ├── icons/
   │   ├── shield-16.png
   │   ├── shield-32.png
   │   ├── shield-48.png
   │   └── shield-128.png
   └── src/
       ├── background/
       │   └── background.js
       ├── popup/
       │   ├── popup.html
       │   ├── popup.css
       │   └── popup.js
       ├── options/
       │   ├── options.html
       │   ├── options.css
       │   └── options.js
       └── utils/
           ├── constants.js
           └── helpers.js
   ```

3. **Load Extension in Chrome:**
   - Open `chrome://extensions/`
   - Enable "Developer mode" (top right)
   - Click "Load unpacked"
   - Select the `cyber-defense-extension` folder

### Development Workflow

1. **Make Changes:**
   Edit files in `src/` directory as needed

2. **Reload Extension:**
   - Go to `chrome://extensions/`
   - Click the refresh icon on your extension
   - Or press Ctrl+Shift+R (Windows/Linux) or Cmd+Shift+R (Mac)

3. **Test Changes:**
   - Test in Chrome immediately
   - Use popup to verify behavior
   - Check DevTools for errors

4. **Debug:**
   - Right-click extension icon → "Inspect popup"
   - Or go to `chrome://extensions/` → "Service worker" link
   - Use breakpoints and console logs

---

## File Structure & Responsibilities

### Core Files

#### `manifest.json`
- Defines extension metadata
- Lists permissions required
- Registers background script and UI pages
- Maps icons at different sizes

**When to Edit:**
- Adding new permissions
- Changing API endpoints
- Updating version number
- Adding new manifest V3 features

#### `background.js`
- Main service worker
- Handles all threat detection logic
- Manages API calls
- Stores settings and logs

**When to Edit:**
- Adding new threat detection logic
- Integrating new APIs
- Changing rate limiting
- Modifying tracker blocklist

#### Popup Files (`popup.*`)
- User-facing interface when clicking extension icon
- Shows recent threats
- Quick action buttons
- Auto-refreshes threat log

**When to Edit:**
- Changing popup layout
- Adding new buttons/features
- Modifying styling
- Updating threat display format

#### Options Files (`options.*`)
- Settings/configuration page
- API key input
- Feature toggles
- Alert level selection

**When to Edit:**
- Adding new settings
- Changing configuration options
- Adding form validation
- Updating styling/layout

#### Utility Files (`utils/*`)
- `constants.js` - Global constants and configuration
- `helpers.js` - Reusable utility functions

**When to Edit:**
- Adding new constants
- Creating utility functions
- Updating configuration values

---

## Common Development Tasks

### Adding a New Threat Type

1. **Add to constants:**
   ```javascript
   // In constants.js
   export const THREAT_TYPES = {
     NEW_THREAT: 'new_threat'
   };
   ```

2. **Add detection logic:**
   ```javascript
   // In background.js
   function detectNewThreat(url) {
     // Detection logic here
     return { isThreat: true, threatType: 'new_threat' };
   }
   ```

3. **Update UI:**
   ```javascript
   // In popup.js
   .threat-type { /* styling */ }
   // Maps automatically via threat.type
   ```

### Adding New Settings

1. **Update manifest:**
   - No changes needed (uses generic storage)

2. **Add to options.html:**
   ```html
   <div class="setting-group">
     <label>New Setting</label>
     <input type="checkbox" id="newSetting">
   </div>
   ```

3. **Handle in options.js:**
   ```javascript
   document.getElementById('newSetting').checked = 
     items.newSetting !== false;
   ```

4. **Use in background.js:**
   ```javascript
   if (SETTINGS.newSetting) {
     // Do something
   }
   ```

### Adding API Integration

1. **Create API client function:**
   ```javascript
   async function queryNewApi(data) {
     // API logic
     const response = await fetch(apiUrl, { /* ... */ });
     return response.json();
   }
   ```

2. **Integrate into scanning:**
   ```javascript
   const result = await queryNewApi(url);
   ```

3. **Handle errors:**
   ```javascript
   try {
     // API call
   } catch (error) {
     console.error('API error:', error);
     // Fallback logic
   }
   ```

### Adding Tracker Domains

1. **Update TRACKER_BLOCKLIST in background.js:**
   ```javascript
   const TRACKER_BLOCKLIST = [
     'existing-tracker.com',
     'new-tracker.com'
   ];
   ```

2. **Test detection:**
   - Visit site that uses new tracker
   - Verify popup shows tracker alert

---

## Debugging Guide

### Using DevTools

#### Popup Debugging
1. Right-click extension icon
2. Select "Inspect popup"
3. Console shows popup.js logs
4. Can interact with DOM in real-time

#### Background Script Debugging
1. Go to `chrome://extensions/`
2. Find your extension
3. Click "Service worker" link
4. Opens DevTools for background.js
5. Add breakpoints and step through code

#### Network Debugging
1. Open DevTools Network tab
2. Filter for API calls
3. Check request/response payloads
4. Verify headers and authentication

### Common Issues & Solutions

**Issue: API key not working**
```javascript
// Debug: Check if API key is loaded
chrome.runtime.sendMessage(
  { action: 'getSettings' },
  response => console.log(response.settings)
);
```

**Issue: Settings not persisting**
```javascript
// Verify storage is working
chrome.storage.sync.get(null, items => 
  console.log('Stored settings:', items)
);
```

**Issue: Threat not being detected**
1. Check DevTools console for errors
2. Verify API key is valid
3. Test with Google's test site
4. Check rate limiting isn't blocking request

**Issue: High memory usage**
1. Check threat log size
2. Verify cleanup is working
3. Look for memory leaks in message handlers
4. Profile with DevTools Memory tool

---

## Code Style Guidelines

### JavaScript Style

```javascript
// Use consistent naming
function scanUrlForThreats(url) {
  // Implementation
}

// Use const by default
const CONSTANT = 'value';

// Use arrow functions in callbacks
.then(response => response.json())

// Add descriptive comments
// Check for known phishing patterns
if (HEURISTIC_PATTERNS.PHISHING_KEYWORDS.includes(word)) {
  // ...
}

// Use JSDoc for functions
/**
 * Scan URL against threat database
 * @param {string} url - URL to scan
 * @returns {Object} Threat result with isThreat and threatType
 */
function scanUrl(url) {
  // ...
}
```

### HTML/CSS Style

```html
<!-- Use semantic HTML -->
<section class="settings-section">
  <h2>Settings Title</h2>
</section>

<!-- CSS: Use BEM-like naming -->
<div class="threat-item threat-item--critical">
  <!-- -->
</div>

/* Use CSS variables for consistency */
:root {
  --color-primary: #667eea;
  --color-success: #22543d;
}
```

---

## Testing During Development

### Quick Test Cycle

1. Make code changes
2. Reload extension (click refresh)
3. Test in browser
4. Check DevTools for errors
5. Iterate

### Running Specific Tests

```javascript
// In background script console:

// Test API scanning
scanUrlForThreats('http://testsafebrowsing.appspot.com/apiv4/').then(r => console.log(r));

// Test tracker detection
checkForTracker('https://google-analytics.com/page');

// Test heuristic check
performHeuristicCheck('http://phishing-login.fake.com');

// Check settings
chrome.runtime.sendMessage({action: 'getSettings'}, r => console.log(r));
```

---

## Performance Optimization Tips

### Memory
- Keep threat log bounded (MAX_LOG_ENTRIES = 100)
- Clean up old event listeners
- Use ephemeral storage (no persistence)

### CPU
- Rate limit API calls (1 per second)
- Use efficient string matching
- Avoid blocking operations

### Network
- Batch API calls when possible
- Cache results temporarily
- Use efficient data structures

---

## Adding New Features

### Feature Checklist

When adding a new feature:
- [ ] Define feature in constants.js
- [ ] Implement core logic in background.js
- [ ] Add UI components (popup/options)
- [ ] Add settings/configuration
- [ ] Add to threat logging if applicable
- [ ] Update documentation
- [ ] Test thoroughly
- [ ] Update version number

---

## Version Management

### Version Numbers

Use semantic versioning: `MAJOR.MINOR.PATCH`

- **MAJOR:** Breaking changes
- **MINOR:** New features
- **PATCH:** Bug fixes

Update in:
1. `manifest.json` - version field
2. `ARCHITECTURE.md` - EXTENSION_META version
3. Include in commit message

### Example:
```javascript
// manifest.json
"version": "1.0.1"

// constants.js
EXTENSION_META: {
  VERSION: '1.0.1'
}
```

---

## Building for Distribution

### Pre-Release Checklist

- [ ] All tests passing
- [ ] No console errors
- [ ] Version number updated
- [ ] Documentation updated
- [ ] Icons present (all sizes)
- [ ] API key is not hardcoded
- [ ] No personal data in code
- [ ] Code style consistent

### Preparing for Chrome Web Store

1. Remove "Developer mode" requirement
2. Ensure icons are optimized
3. Create store listing assets
4. Write compelling description
5. Set privacy policy
6. Submit for review

---

## Troubleshooting Development

### Extension Won't Load
- Check manifest.json syntax (use JSON validator)
- Verify all referenced files exist
- Check file paths are correct
- Look for permission errors

### Changes Not Applying
- Reload extension after code changes
- Check for syntax errors in console
- Verify files are saved
- Try hard refresh (Ctrl+Shift+R)

### Service Worker Crashes
- Check DevTools for errors
- Look for unhandled promise rejections
- Verify all async operations complete
- Check for infinite loops

---

## Resources

- **Chrome API Documentation:** https://developer.chrome.com/docs/extensions/
- **Manifest V3 Migration:** https://developer.chrome.com/docs/extensions/mv3/
- **Safe Browsing API:** https://developers.google.com/safe-browsing/
- **Chrome DevTools Guide:** https://developer.chrome.com/docs/devtools/

---

## Contributing

When contributing improvements:

1. Create a branch: `git checkout -b feature/your-feature`
2. Make changes following style guide
3. Test thoroughly
4. Commit with clear messages: `git commit -m "Add feature: description"`
5. Submit pull request with description

---

## Support

For development questions:
- Check existing documentation
- Review similar features in codebase
- Check Chrome API documentation
- Test with safe APIs first

---

**Happy developing! 🚀**
