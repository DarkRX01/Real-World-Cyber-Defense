# Contributing to Real-World Cyber Defense

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

## 📋 Code of Conduct

We are committed to providing a welcoming and inspiring community for all. Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md).

**Be respectful, inclusive, and constructive.**

---

## 🤝 How to Contribute

### Reporting Issues

1. **Check existing issues** first - your issue may already be reported
2. **Use the bug report template** when creating an issue
3. **Include:**
   - Chrome version
   - Extension version
   - Steps to reproduce
   - Expected behavior
   - Actual behavior
   - Screenshots (if applicable)

### Suggesting Enhancements

1. **Check existing discussions** - your idea may already be discussed
2. **Use the feature request template**
3. **Describe:**
   - What problem it solves
   - How it should work
   - Why it's useful
   - Example use case

### Submitting Code Changes

#### Step 1: Fork and Clone
```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/cyber-defense-extension.git
cd cyber-defense-extension
```

#### Step 2: Create a Branch
```bash
# Create a feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b bugfix/issue-description
```

#### Step 3: Make Changes
- Follow the code style (see below)
- Add comments for complex logic
- Update documentation if needed
- Don't commit API keys or secrets

#### Step 4: Test Your Changes
```bash
# Load unpacked in Chrome
chrome://extensions/ → Load unpacked

# Run tests
See TESTING_GUIDE.md for procedures

# Check for errors
Open DevTools → Console
```

#### Step 5: Commit
```bash
# Use clear, descriptive commit messages
git commit -m "Add feature: description of what changed"

# Examples:
git commit -m "Add tracker detection for TikTok"
git commit -m "Fix: API key not persisting"
git commit -m "Docs: Update installation guide"
```

#### Step 6: Push and Create PR
```bash
# Push to your fork
git push origin feature/your-feature-name

# Go to GitHub and create a Pull Request
# Use the PR template and describe your changes
```

---

## 🎨 Code Style Guide

### JavaScript
```javascript
// Use const by default, let if needed
const CONSTANT = 'value';
let variable = 'value';

// Use arrow functions in callbacks
array.map(item => item.value)

// Use descriptive names
function scanUrlForThreats(url) {
  // Implementation
}

// Add comments for complex logic
// Check if URL contains known phishing patterns
if (url.includes('phishing')) {
  // Handle phishing
}

// Use JSDoc for functions
/**
 * Scan URL against threat database
 * @param {string} url - URL to scan
 * @returns {Object} Threat result
 */
function scanUrl(url) {
  // Implementation
}
```

### HTML
```html
<!-- Use semantic HTML -->
<section class="settings-section">
  <h2>Settings Title</h2>
</section>

<!-- Use meaningful class names -->
<button class="threat-item threat-item--critical">
```

### CSS
```css
/* Use meaningful selectors */
.threat-item {
  /* Styles */
}

/* Use CSS variables -->
:root {
  --color-primary: #667eea;
}

/* Use BEM-like naming -->
.threat-item--critical {
  /* Specific variant */
}
```

---

## 📦 Development Setup

### Prerequisites
- Node.js v14+ (optional, for tooling)
- Chrome v88+
- Git

### Local Setup
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/cyber-defense-extension.git
cd cyber-defense-extension

# Load in Chrome
1. Open chrome://extensions/
2. Enable "Developer mode"
3. Click "Load unpacked"
4. Select this folder
```

### Making Changes
```bash
# Edit files as needed
# Reload extension in Chrome (refresh icon)
# Test in DevTools (F12)
```

---

## 🧪 Testing

### Before Submitting PR
- [ ] Code works without errors
- [ ] No console warnings/errors
- [ ] Settings persist correctly
- [ ] API integration works (if changed)
- [ ] All features still work
- [ ] No security issues

### Run Tests
See [TESTING_GUIDE.md](TESTING_GUIDE.md) for detailed procedures:
```bash
# Test URL scanning
# Test tracker detection
# Test download scanning
# Test settings management
# Test popup display
# Test error handling
```

---

## 📚 Documentation

If your change affects functionality:
- [ ] Update relevant documentation
- [ ] Add code comments
- [ ] Update CHANGELOG.md
- [ ] Update examples if applicable

### Documentation Files
- `README.md` - Main documentation
- `GETTING_STARTED.md` - Setup guide
- `ARCHITECTURE.md` - Technical design
- `DEVELOPMENT.md` - Development guide

---

## 🔐 Security

### API Keys
- **NEVER** hardcode API keys
- **NEVER** commit `.env` files with keys
- Store in `chrome.storage.sync` only

### Sensitive Code
- No eval() or dynamic code execution
- Validate all inputs
- Handle errors gracefully
- No information disclosure in errors

### Reporting Security Issues
**DO NOT open a public issue for security vulnerabilities.**

See [SECURITY.md](SECURITY.md) for reporting procedures.

---

## 🐛 Types of Contributions

### Bug Fixes
```
Title: Fix: [Brief description]
Description: What was broken, what was done to fix it
Testing: How to verify the fix works
```

### New Features
```
Title: Feature: [Brief description]
Description: What it does, why it's useful
Design: How it works, what changes
Testing: How to test it
```

### Documentation
```
Title: Docs: [What was updated]
Description: Why the documentation was needed
Changes: What was added/updated
```

### Performance
```
Title: Perf: [Brief description]
Description: What was slow, what the improvement is
Metrics: Benchmark before/after if applicable
```

---

## 📋 PR Checklist

Before submitting your PR:

- [ ] Code follows style guide
- [ ] Comments added for complex logic
- [ ] Documentation updated
- [ ] No hardcoded secrets
- [ ] Tests pass
- [ ] No console errors
- [ ] CHANGELOG updated
- [ ] PR description is clear

---

## 🎯 Areas for Contribution

### High Priority
- Bug fixes for reported issues
- Security vulnerability fixes
- Documentation improvements
- Test coverage expansion

### Medium Priority
- Performance optimizations
- Enhanced error handling
- Improved user experience
- Better error messages

### Low Priority
- Code style improvements
- Comment improvements
- Minor refactoring
- Configuration options

---

## 💡 Project Ideas

### Want to Work On?
- Enhanced heuristics for threat detection
- VirusTotal API integration
- Archive file scanning
- Multi-browser support (Firefox, Edge)
- Threat intelligence sharing
- Enterprise logging features

Check [Issues](https://github.com/DarkRX01/Real-World-Cyber-Defense/issues) and [Discussions](https://github.com/DarkRX01/Real-World-Cyber-Defense/discussions) for ideas.

---

## 🎓 Learning Resources

### Getting Started with Chrome Extensions
- [Chrome Extension Docs](https://developer.chrome.com/docs/extensions/)
- [Manifest V3 Guide](https://developer.chrome.com/docs/extensions/mv3/)

### Understanding the Project
- [ARCHITECTURE.md](ARCHITECTURE.md) - System design
- [DEVELOPMENT.md](DEVELOPMENT.md) - Dev setup
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - Testing procedures

### Threat Detection
- [Google Safe Browsing API](https://developers.google.com/safe-browsing)
- [VirusTotal API](https://www.virustotal.com/gui/home/upload)

---

## ❓ Questions?

- 📖 Check documentation first
- 💬 Open a GitHub Discussion
- 🐛 Check existing Issues
- 📧 See SECURITY.md for sensitive topics

---

## 🎉 Thanks for Contributing!

Your contributions make this project better for everyone. Whether it's code, documentation, bug reports, or ideas - we appreciate it all!

---

## 📄 License

By contributing, you agree that your contributions will be licensed under the project's MIT License.

---

**Happy Contributing! 🚀**
