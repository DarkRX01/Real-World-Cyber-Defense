# Testing Guide - Real-World Cyber Defense Extension

## Testing Overview

This guide provides comprehensive testing procedures to validate the extension's functionality.

## Pre-Testing Checklist

- [ ] Extension is loaded in Developer Mode
- [ ] Google Safe Browsing API key is configured
- [ ] Chrome is up-to-date (v88+)
- [ ] No other security extensions interfering
- [ ] Clear browser cache and cookies (optional)

---

## Unit Testing Scenarios

### Test 1: API Key Configuration

**Objective:** Verify API keys are stored and loaded correctly

**Steps:**
1. Click extension icon → Settings
2. Enter test API key in "Google Safe Browsing API Key"
3. Click "Save Settings"
4. Close and reopen Settings
5. Verify API key is still there

**Expected Result:** ✅ API key persists across sessions

**Failure Indicators:**
- API key is blank when reopening
- Error message when saving
- Settings not visible

---

### Test 2: Threat Log Display

**Objective:** Verify threat logging and display works

**Steps:**
1. Open popup (click extension icon)
2. Check "Recent Threats Detected" section
3. Click "Clear Log"
4. Confirm: "Clear all threat logs?"
5. Verify list shows "No threats detected yet."

**Expected Result:** ✅ Log clears and resets properly

---

### Test 3: Feature Toggle

**Objective:** Verify tracker detection toggle works

**Steps:**
1. Open popup
2. Click "Toggle Trackers" button
3. Check status changes from "Enabled" → "Disabled"
4. Click Settings and verify "Enable Tracker Detection" is unchecked
5. Go back to popup, click "Toggle Trackers" again
6. Verify status returns to "Enabled"

**Expected Result:** ✅ Toggles change both popup and settings

---

## Integration Testing Scenarios

### Test 4: Safe Browsing API Integration

**Objective:** Verify Google Safe Browsing API works correctly

**Steps:**
1. Ensure API key is configured in Settings
2. Visit: http://testsafebrowsing.appspot.com/apiv4/
3. Click on a test link (marked as "Phishing" or "Malware")
4. Observe Chrome behavior

**Expected Result:**
- 🟢 GOOD: Extension shows notification warning about threat
- 🟡 NEUTRAL: Page loads but extension shows warning
- 🔴 BAD: No warning shown, request completes silently

**Debugging if Test 4 Fails:**
1. Open DevTools (F12) → Application → Service Workers
2. Click on background worker
3. Open Console
4. Reload page and check for error messages
5. Verify API key is valid in Google Cloud Console

---

### Test 5: Popup Real-Time Updates

**Objective:** Verify popup refreshes threat list automatically

**Steps:**
1. Open popup (leave it open)
2. In a new tab, visit Google's test site
3. Click on a threat link
4. Watch popup from step 1

**Expected Result:** ✅ Popup shows new threat within 2 seconds

---

### Test 6: Download Detection

**Objective:** Verify download scanner warns about suspicious files

**Steps:**
1. Ensure "Enable Download Scanning" is enabled in Settings
2. Visit a website with safe downloads (e.g., GitHub releases)
3. Download a file (preferably not .exe)
4. Check popup - should not show suspicious download alert

**Expected Result:** ✅ No alert for safe downloads

**Test 6b: Dangerous Downloads**
1. (Simulated) If you had a way to download .exe from unknown source
2. Popup should show suspicious download alert
3. Alert should recommend not proceeding

---

### Test 7: Tracker Detection

**Objective:** Verify tracker blocking works

**Steps:**
1. Ensure "Enable Tracker Detection" is enabled
2. Ensure "Privacy Mode" is set to "Balanced" (not Strict)
3. Visit google.com
4. Open DevTools Network tab
5. Look for `google-analytics.com` requests
6. Check popup for tracker alerts

**Expected Result:** ✅ Popup shows tracker alerts for Analytics domains

**Test 7b: Strict Mode**
1. Go to Settings
2. Change "Privacy Mode" to "Strict"
3. Reload google.com
4. Check Network tab - should NOT see `google-analytics.com` requests

**Expected Result:** ✅ Analytics requests are blocked in Strict mode

---

### Test 8: Alert Levels

**Objective:** Verify alert level settings control behavior

**Steps:**
1. Go to Settings
2. Set Alert Level to "Low"
3. Visit Google's test site and trigger a threat
4. Verify: Only notification appears, request completes

**Expected Result:** ✅ Request not blocked in Low mode

**Test 8b: Medium Mode**
1. Set Alert Level to "Medium"
2. Test with a "high-severity" threat

**Expected Result:** ✅ High-severity threats blocked

**Test 8c: High Mode**
1. Set Alert Level to "High"
2. Test with any threat

**Expected Result:** ✅ All threats are blocked

---

## End-to-End Testing Scenarios

### Test 9: Complete User Workflow

**Objective:** Test the full extension lifecycle

**Steps:**
1. **Setup Phase:**
   - [ ] Get Google API key
   - [ ] Load extension
   - [ ] Configure API key
   - [ ] Verify all settings save

2. **Detection Phase:**
   - [ ] Visit normal site (google.com)
   - [ ] Visit test threat site
   - [ ] Verify threat detected and logged

3. **Management Phase:**
   - [ ] Open popup
   - [ ] View threats
   - [ ] Clear logs
   - [ ] Verify cleared

4. **Cleanup Phase:**
   - [ ] Close Chrome
   - [ ] Reopen Chrome
   - [ ] Verify logs are cleared (ephemeral)

**Expected Result:** ✅ All phases complete successfully

---

### Test 10: Error Recovery

**Objective:** Verify extension handles API failures gracefully

**Steps:**
1. Go to Settings
2. Enter invalid API key (e.g., "invalid_key_12345")
3. Visit Google's test site
4. Extension should:
   - [ ] Show error or notification
   - [ ] Fall back to heuristic check
   - [ ] Not crash or hang

**Expected Result:** ✅ Extension continues working with fallback

---

### Test 11: Cross-Tab Consistency

**Objective:** Verify extension works consistently across tabs

**Steps:**
1. Open 3 tabs
2. In each tab, open popup
3. Visit threat site in Tab 1
4. Check popups in Tabs 2 and 3

**Expected Result:** ✅ All popups show same threat log

---

## Performance Testing

### Test 12: Memory Usage

**Objective:** Verify extension doesn't consume excessive memory

**Steps:**
1. Open DevTools → Memory tab
2. Take heap snapshot before extension
3. Use extension normally for 10 minutes
4. Browse various websites
5. Take another heap snapshot

**Expected Result:** 
- 🟢 GOOD: <10 MB additional memory
- 🟡 NEUTRAL: 10-20 MB additional memory
- 🔴 BAD: >20 MB additional memory

---

### Test 13: CPU Impact

**Objective:** Verify extension has minimal CPU impact

**Steps:**
1. Open DevTools → Performance tab
2. Record 30 seconds of normal browsing
3. Review CPU usage

**Expected Result:** ✅ <1% additional CPU usage

---

### Test 14: Network Impact

**Objective:** Verify extension doesn't cause excessive network requests

**Steps:**
1. Open DevTools → Network tab
2. Filter for Safe Browsing API domain
3. Browse normally for 5 minutes
4. Count requests to Safe Browsing API

**Expected Result:** ✅ Requests limited to actual URLs visited

---

## Browser Compatibility Testing

### Test 15: Chrome Versions

**Test on:**
- [ ] Chrome 88 (minimum supported)
- [ ] Chrome 100+
- [ ] Chrome Latest

**Objective:** Extension works on supported versions

**Expected Result:** ✅ All versions work identically

---

## Security Testing

### Test 16: API Key Security

**Objective:** Verify API key is not exposed

**Steps:**
1. Open DevTools
2. Check Application → Session Storage
3. Check Network tab for API key exposure
4. Check Console for logged API keys

**Expected Result:**
- ✅ API key not in Network requests (only in POST body)
- ✅ API key not in Console logs
- ✅ API key only in chrome.storage.sync

---

### Test 17: Data Privacy

**Objective:** Verify no user data is collected

**Steps:**
1. Check DevTools Network tab
2. Monitor all outgoing requests during normal browsing
3. Verify no tracking requests to unknown services

**Expected Result:**
- ✅ Only requests to Safe Browsing API (your scan)
- ✅ No requests to extension developer's servers
- ✅ No analytics services contacted

---

## Regression Testing Checklist

### After Any Code Changes

- [ ] API key still works
- [ ] Threat detection still triggers
- [ ] Tracker detection still works
- [ ] Download scanning still works
- [ ] Settings save/load correctly
- [ ] Popup displays correctly
- [ ] No console errors
- [ ] No memory leaks

---

## Known Test Sites

### Safe Browsing Test URLs

**Google's Official Test Site:**
- URL: http://testsafebrowsing.appspot.com/apiv4/
- Contains: Safe test cases for each threat type

**PhishTank Database:**
- URL: https://www.phishtank.com/
- Contains: Real phishing URLs (view only, don't visit)

**Malware Test Sites (Proceed with Caution):**
- These are blocked by Google Safe Browsing
- Test with: http://testsafebrowsing.appspot.com/apiv4/

---

## Troubleshooting Failed Tests

### If Test 4 (Safe Browsing API) Fails:

**Checklist:**
1. [ ] API key is valid (check Google Cloud Console)
2. [ ] API key has Safe Browsing enabled
3. [ ] API key is correctly pasted (no extra spaces)
4. [ ] Extension is reloaded after changing API key
5. [ ] Network connection is working
6. [ ] Google API isn't rate-limiting your IP

**Debug:**
```javascript
// In DevTools Console for background worker:
chrome.runtime.sendMessage({action: 'getSettings'}, response => {
  console.log('Settings:', response.settings);
  console.log('API Key present:', response.settings.apiKeyGoogle ? 'Yes' : 'No');
});
```

---

### If Test 7 (Tracker Detection) Fails:

**Checklist:**
1. [ ] Tracker detection is enabled in popup status
2. [ ] Privacy mode is "Balanced" (not disabled)
3. [ ] Website actually loads tracker scripts
4. [ ] Network requests are not blocked by other tools

---

### If Test 9 (Complete Workflow) Fails:

**Checklist:**
1. [ ] Extension is loaded in Developer Mode
2. [ ] No errors in DevTools Console
3. [ ] All permissions are granted
4. [ ] Browser notifications are enabled
5. [ ] Chrome isn't in incognito mode (extensions disabled)

---

## Test Report Template

Use this template to document test results:

```
Test Date: _______________
Chrome Version: __________
Extension Version: ________
API Keys Configured: Yes / No

Test Results:
[ ] Test 1: API Key Configuration ✅/❌
[ ] Test 2: Threat Log Display ✅/❌
[ ] Test 3: Feature Toggle ✅/❌
[ ] Test 4: Safe Browsing API ✅/❌
[ ] Test 5: Popup Real-Time ✅/❌
[ ] Test 6: Download Detection ✅/❌
[ ] Test 7: Tracker Detection ✅/❌
[ ] Test 8: Alert Levels ✅/❌
[ ] Test 9: Complete Workflow ✅/❌
[ ] Test 10: Error Recovery ✅/❌

Issues Found:
1. ____________________________
2. ____________________________

Overall Result: PASS / FAIL
```

---

**Happy Testing! 🛡️**
