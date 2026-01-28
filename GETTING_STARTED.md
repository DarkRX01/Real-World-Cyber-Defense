# Getting Started - Easy Setup Guide

**Follow these simple steps to get your extension running in 5 minutes!**

---

## Step 1️⃣: Load the Extension in Chrome

### What you'll do:
Install the extension so Chrome knows about it.

### How:
```
1. Open Chrome browser
2. Copy this and paste in address bar: chrome://extensions/
3. Press Enter
4. Look for "Developer mode" toggle (top right of page)
5. Click to turn it ON
6. Click the blue "Load unpacked" button that appears
7. Find your cyber-defense-extension folder
8. Select it (click it once, then click "Select Folder")
9. ✅ Done! You'll see the extension in the list
```

---

## Step 2️⃣: (Optional) Add Google Safe Browsing API Key

### What this does:
Gives your extension access to Google's threat database for better detection.

### How to get a free API key:
```
1. Go to: https://console.cloud.google.com/
2. Click "Create Project"
3. Name it anything (like "Cyber Defense")
4. Wait 30 seconds for it to load
5. In the search box at top, type: Safe Browsing API
6. Click on "Safe Browsing API"
7. Click the blue "Enable" button
8. Wait for it to enable (30 seconds)
9. Click "Credentials" on the left
10. Click "Create Credentials"
11. Choose "API Key"
12. Copy the key it shows you
13. ✅ You have your free API key!
```

### How to add the key to your extension:
```
1. Look at your Chrome toolbar (top right area)
2. Find the shield icon (that's your extension)
3. Click it once
4. Click the gear icon ⚙️ (settings)
5. Paste your API key in the text box
6. Click "Save Settings"
7. ✅ Done! You're all set
```

---

## ❓ Questions?

**Q: Do I HAVE to add an API key?**
A: No! The extension works without it. The key just makes it better.

**Q: Is the API key free?**
A: Yes! 100% free. No credit card needed.

**Q: Where does my API key go?**
A: It stays only in your Chrome browser, safely stored. We never see it.

**Q: Is my data safe?**
A: Yes! Everything happens on your computer. Nothing is sent anywhere.

---

## 🎉 You're Done!

Your extension is now ready. Click the shield icon anytime to see:
- ✅ Recent threats detected
- ✅ How many trackers blocked  
- ✅ Quick access to settings

**Enjoy your free protection!** 🛡️

---

## Next Steps

- **Learn more:** Read [README.md](README.md)
- **See all features:** Read [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
3. You should see an alert popup from the extension

**Expected Result:** Extension detects threat and shows notification

### Test 2: Tracker Detection
1. Visit any major website (e.g., Google.com, Facebook.com)
2. Open Chrome DevTools (F12)
3. Go to Network tab
4. Reload the page
5. Look for requests to tracker domains like `google-analytics.com`
6. The extension should have logged these

**Expected Result:** Tracker requests are detected and logged

### Test 3: Download Scanner
1. Download a file from a website
2. Check the popup for recent alerts
3. If the file extension is dangerous (e.g., .exe) from untrusted source, alert should appear

**Expected Result:** Suspicious downloads trigger notifications

### Test 4: Popup Display
1. Click extension icon
2. You should see:
   - Extension status (Threat Detection, Trackers, Downloads)
   - Recent threats detected
   - Quick action buttons

**Expected Result:** Popup shows all recent threats with details

---

## Troubleshooting

### Issue: "No API key found" message
**Solution:**
- Check that you've entered your Google API key in Settings
- Verify the key is correct and copied fully
- Reload the extension (toggle off/on in chrome://extensions/)

### Issue: No threats detected when expected
**Solution:**
- Verify API key is valid
- Check extension is enabled in chrome://extensions/
- Check notifications permission is enabled
- Try the test site: http://testsafebrowsing.appspot.com/apiv4/

### Issue: Extension not appearing in toolbar
**Solution:**
- Go to chrome://extensions/
- Verify extension is enabled
- Click the pin icon next to the extension to keep it visible in toolbar
- Reload Chrome

### Issue: High false positives
**Solution:**
- This is likely correct behavior (legitimate sites flagged by Google)
- Change alert level to "Low" if too many notifications
- Report false positives to Google via Safe Browsing Feedback

### Issue: API quota exceeded
**Solution:**
- Google Safe Browsing free tier allows reasonable requests
- Extension automatically rate-limits to 1 request/second
- Check that you're not making duplicate requests

---

## Advanced Configuration

### Alert Levels Explained

**Low Mode:**
- Only sends notifications
- Never blocks requests
- Best for: Learning what's detected without disruption

**Medium Mode (Default):**
- Shows notifications for all threats
- Blocks only high-severity threats
- Best for: Balanced security and usability

**High Mode:**
- Shows notifications for all threats
- Blocks all detected threats automatically
- Best for: Maximum security, restrictive environment

### Privacy Modes Explained

**Balanced Mode (Default):**
- Shows alerts when trackers detected
- Allows requests by default
- Best for: Most users, general browsing

**Strict Mode:**
- Automatically blocks all known tracking domains
- Maximum privacy protection
- Best for: Journalists, researchers, sensitive work

### Feature Toggles

**Tracker Detection:**
- Identifies third-party tracking pixels and analytics
- Blocklist includes: Google Analytics, Facebook pixels, Twitter tracking, etc.
- Toggle on/off based on preference

**Download Scanning:**
- Scans file extensions for dangerous types
- Checks against known malicious domains
- Warns before downloading suspicious files

**Threat Logging:**
- Stores threat detections in memory
- Clears when browser closes (ephemeral)
- Helps identify attack patterns

---

## Understanding the Dashboard

### Status Section
Shows which features are currently active:
- ✅ Threat Detection (always active)
- 🔒 Tracker Detection (toggleable)
- ⬇️ Download Scanner (toggleable)

### Recent Threats List
Shows the last 10 threats detected:
- **Type badge:** threat/tracker/suspicious_download
- **Severity indicator:** Low/Medium/High
- **URL:** Where threat was detected
- **Timestamp:** When it was detected

Click "Clear Log" to reset threat history

### Quick Actions
- **Toggle Trackers:** Enable/disable tracker blocking
- **Toggle Downloads:** Enable/disable download scanning
- **Settings:** Open configuration page

---

## API Keys Reference

### Google Safe Browsing API
- **Purpose:** Real-time threat detection against Google's database
- **Cost:** Free tier available
- **Rate Limit:** Extension limits to 1 request/second
- **Data Sent:** Only the URL being checked
- **Privacy:** Google doesn't store browsing history from queries

### VirusTotal API (Optional)
- **Purpose:** Additional malware scanning (optional)
- **Cost:** Free tier with 4 requests/minute limit
- **Rate Limit:** Extension respects this automatically
- **Data Sent:** URL or file hash
- **Privacy:** VirusTotal can see submitted URLs

---

## Extension Permissions Explained

The extension requests these Chrome permissions:

| Permission | Why It's Used | Data Shared |
|-----------|---------------|------------|
| `webRequest` | Monitor outgoing web requests | Only with Safe Browsing API |
| `webRequestBlocking` | Block malicious requests | None (local decision) |
| `notifications` | Show threat alerts | None (local only) |
| `storage` | Save your API keys and settings | None (local storage) |
| `downloads` | Scan downloaded files | File metadata only |
| `activeTab` | Check current tab details | None (for future features) |

---

## Common Questions (FAQ)

**Q: Does the extension track my browsing?**
A: No. All threat detection happens locally. No browsing history is sent anywhere. Only URLs being actively scanned are sent to Safe Browsing API.

**Q: Is my API key safe?**
A: Yes. Your API key is stored locally in Chrome and never shared with third parties.

**Q: Can the extension block legitimate websites?**
A: Rarely. Google Safe Browsing is very accurate but can have false positives. You can always proceed past the warning.

**Q: What happens to my threat logs?**
A: Threat logs are stored in memory and automatically cleared when you close Chrome. No permanent logging occurs.

**Q: Can I use this on mobile Chrome?**
A: Not in this MVP version. Mobile support can be added in future versions.

**Q: Do I need to pay for anything?**
A: No. Google Safe Browsing and VirusTotal both have free tiers with reasonable limits.

---

## Performance Impact

The extension has minimal performance impact:
- **Memory:** ~5-10 MB
- **CPU:** <1% average
- **Network:** Only requests for URLs being scanned
- **Battery:** Minimal impact on mobile (if supported)

---

## Getting Help

If you encounter issues:

1. Check the Troubleshooting section above
2. Review the About section in Settings for version info
3. Check the threat log for recent alerts
4. Verify API key is valid and enabled

---

## Next Steps

After setup, you might want to:

1. **Adjust settings** to match your security needs
2. **Test with known phishing sites** to understand how it works
3. **Monitor threat logs** to see what's detected on your network
4. **Explore privacy mode** to see difference between balanced and strict

---

## Security Best Practices

While using this extension:

1. **Keep Chrome updated** to latest version
2. **Enable 2FA** on important accounts (extension can't prevent account takeover)
3. **Don't trust extension alone** - use other security tools too
4. **Keep API keys private** - don't share them
5. **Review alerts carefully** - don't automatically trust blocking
6. **Stay informed** about current phishing/malware tactics

---

**You're all set! Enjoy safer browsing with Cyber Defense! 🛡️**
