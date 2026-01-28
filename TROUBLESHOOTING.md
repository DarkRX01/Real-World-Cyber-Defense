# 🆘 Troubleshooting - Fix Common Problems

**Something not working? This guide will help you fix it in minutes!**

---

## ❌ Extension Won't Load

### Problem: Nothing happens when I click "Load unpacked"

**Solution:**
```
1. Make sure you selected the RIGHT folder
   - It should have a file called "manifest.json" inside
   - It should have a "src" folder
   - It should have an "icons" folder
   
2. Check "Developer mode" is turned ON
   - Go to chrome://extensions/
   - Look at top right for "Developer mode"
   - Make sure the toggle is BLUE (ON)
   
3. If still not working:
   - Try closing Chrome completely
   - Open Chrome again
   - Try steps 1-3 again
```

---

## ❌ Extension Loads But Shows Error

### Problem: I see an error in the extension list

**Solution:**
```
1. Look at the error message
   - If it says "missing manifest"
     → Wrong folder selected
     → Pick the cyber-defense-extension folder itself
   
2. Try reloading the extension:
   - Find the extension in list
   - Click the reload icon (circular arrow)
   - If it still shows error, unload and reload:
     → Click "X" button to remove it
     → Load unpacked again
     
3. Check file permissions:
   - Right-click cyber-defense-extension folder
   - Properties → Security
   - Make sure you have "Read" permission
```

---

## ❌ Extension Loaded But Not Showing

### Problem: I don't see the shield icon in toolbar

**Solution:**
```
1. It might be hidden:
   - Look for 3-dot menu (⋮) on top right of Chrome
   - Click it
   - Look for "Extensions" option
   - Find "Real-World Cyber Defense"
   - Click the pin icon next to it
   - Now it should show in toolbar
   
2. Or try clicking different spots:
   - Look very carefully at top right
   - Near the address bar
   - See small icons there? Click each one
   - One of them might be your extension
```

---

## ❌ Settings Not Saving

### Problem: I add API key but it disappears

**Solution:**
```
1. Make sure you're clicking "Save Settings"
   - After pasting API key, look for "Save" button
   - Click it
   - Wait 2 seconds
   
2. Check if settings page is broken:
   - Go to chrome://extensions/
   - Find "Real-World Cyber Defense"
   - Click "Options" or "Settings"
   - Try again
   - Wait 3 seconds before closing
   
3. Try this:
   - Close the settings page completely
   - Click extension icon again
   - Click gear icon again
   - Settings should still be there
```

---

## ❌ API Key Not Working

### Problem: Extension says "API key not found" or "Invalid key"

**Solution:**
```
1. Check if you copied the whole key:
   - Go back to Google Cloud Console
   - Find your API key
   - Copy it completely (should be LONG text)
   - No spaces before or after
   
2. Check if Safe Browsing API is enabled:
   - Go to console.cloud.google.com
   - Find your project
   - Go to "Enabled APIs & services"
   - Look for "Safe Browsing API"
   - If NOT there, click "Enable APIs and Services"
   - Search "Safe Browsing API"
   - Click it
   - Click "Enable"
   - Wait 1 minute
   
3. Try a new API key:
   - Maybe the old one is broken
   - Go to Google Cloud Console
   - Go to "Credentials"
   - Delete the old key
   - Click "Create Credentials"
   - Choose "API Key"
   - Copy the NEW key
   - Paste in extension settings
   - Click Save
```

---

## ❌ No Alerts Showing

### Problem: Extension never warns me about anything

**Solution:**
```
1. Check if notifications are on:
   - Click extension icon
   - Click gear ⚙️
   - Check "Enable Notifications" or similar
   - Make sure "Alert Level" is NOT set to "Off"
   
2. Check Chrome notifications:
   - Go to chrome://settings/content/notifications
   - Look for cyber-defense-extension
   - Make sure it says "Allowed"
   
3. Check if extension is actually on:
   - Click extension icon
   - You should see popup
   - If no popup, extension isn't working
   - Try reloading it
   
4. Visit a test page:
   - Go to: testsafebrowsing.appspot.com
   - Click on different options
   - This will trigger alerts if working
   - (It's a safe testing site)
```

---

## ❌ Extension Uses Too Much Memory

### Problem: My Chrome is slow since I installed it

**Solution:**
```
1. Extension should be tiny, but if slow:
   - This might be a different extension
   - Check if other extensions are the problem
   - Try disabling other extensions one by one
   
2. If it IS this extension:
   - Go to settings
   - Turn off "Download Scanning"
   - Save settings
   - See if Chrome speeds up
   
3. Try restarting Chrome:
   - Close ALL Chrome windows
   - Wait 10 seconds
   - Open Chrome again
   - Should be faster
```

---

## ❌ Can't Find Settings/Options

### Problem: Where do I change settings?

**Solution:**
```
1. Easy way:
   - Look for shield icon in toolbar
   - Click it ONCE
   - Popup appears
   - Look for gear icon ⚙️
   - Click it
   - Settings page opens!
   
2. If that doesn't work:
   - Go to chrome://extensions/
   - Find "Real-World Cyber Defense"
   - Look for "Details" button
   - Click it
   - Scroll down
   - Click "Options" or "Settings"
```

---

## ❌ Uninstalling Doesn't Work

### Problem: I want to remove the extension but can't

**Solution:**
```
1. Go to chrome://extensions/
   
2. Find "Real-World Cyber Defense" in the list
   
3. Look for small trash/delete icon
   
4. Click the trash icon
   
5. Chrome asks "Remove this extension?"
   
6. Click "Remove"
   
✅ Done! It's gone.
```

---

## ✅ Still Having Problems?

**Don't worry! Help is available:**

1. **Check docs:**
   - [README.md](README.md) - Full guide
   - [QUICK_REFERENCE.md](QUICK_REFERENCE.md) - Quick answers
   - [TESTING_GUIDE.md](TESTING_GUIDE.md) - How to test

2. **Ask for help:**
   - Go to [GitHub Issues](https://github.com/YOUR_USERNAME/cyber-defense-extension/issues)
   - Click "New issue"
   - Describe your problem
   - We'll help!

3. **Or ask a question:**
   - Go to [GitHub Discussions](https://github.com/YOUR_USERNAME/cyber-defense-extension/discussions)
   - Ask your question
   - Community will help

---

## 🛠️ Technical Help (If You Know Tech)

**For developers/advanced users:**

1. **Check browser console:**
   - Open DevTools (F12)
   - Click "Console" tab
   - Look for red error messages
   - Copy them when asking for help

2. **Check extension logs:**
   - Go to chrome://extensions/
   - Find the extension
   - Click "Details"
   - Click "Errors" (if it shows)
   - Read the error messages

3. **Check service worker:**
   - Go to chrome://extensions/
   - Find the extension
   - Look for "Service Worker" section
   - Click "Inspect" to see debugging

---

**Remember: All problems are solvable! Don't give up.** 💪

*Real-World Cyber Defense Support Team* 🛡️
