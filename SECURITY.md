# Security Policy

## 🔐 Security is Our Priority

We take the security of the Real-World Cyber Defense desktop application seriously. This policy outlines how we handle security issues.

---

## 🚨 Reporting a Security Vulnerability

### DO NOT Report Publicly

**If you discover a security vulnerability, please DO NOT:**
- Open a public GitHub issue
- Post in discussions
- Share in comments
- Discuss in public channels

**This could endanger all users.**

### DO Report Privately

**Instead, please:**

1. **GitHub Security Advisories**: Use [GitHub's private vulnerability reporting](https://github.com/DarkRX01/Real-World-Cyber-Defense/security/advisories/new)
2. **Include:**
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if you have one)
   - Your contact information (for follow-up)

### What to Expect

- **Acknowledgment** within 48 hours
- **Investigation** within 7 days
- **Update** on progress regularly
- **Fix and release** as soon as possible
- **Credit** in release notes (if you wish)

---

## 🛡️ Security Best Practices

### For Users

**To stay safe while using Cyber Defense:**

1. ✅ Keep the application updated to the latest version
2. ✅ Download only from official sources (GitHub releases)
3. ✅ Don't trust threat alerts alone - verify independently
4. ✅ Report suspicious behavior
5. ✅ Keep your operating system updated
6. ✅ Use strong, unique passwords
7. ✅ Enable Windows Firewall and Defender

### For Developers

**When contributing code:**

1. ✅ Never hardcode API keys or secrets
2. ✅ Validate all user inputs
3. ✅ Handle errors gracefully
4. ✅ No eval() or dynamic code execution
5. ✅ Test security implications
6. ✅ Follow OWASP guidelines
7. ✅ Report vulnerabilities privately

---

## 🔍 Security Review Process

### Code Review
- All changes are reviewed via pull requests
- Security implications considered
- No hardcoded secrets allowed
- Error handling validated
- Automated linting with security checks (ruff)

### Vulnerability Assessment
- Regular dependency updates
- Known vulnerabilities tracked via GitHub Dependabot
- Dependency checking with pip-audit
- Code quality analysis

### Testing
- Security test scenarios included
- Error handling validated
- Input validation tested
- Unit tests for all threat detection logic

---

## 🚪 Optional API Key Security

### How We Handle API Keys

The application works fully offline without any API keys. Optional API keys enhance detection:

✅ **Stored Locally** - Only on your computer in settings.json
✅ **Never Logged** - Not written to logs
✅ **Never Shared** - Not sent to third parties (except the API provider)
✅ **You Control It** - You provide your own key
✅ **Optional** - App works without it (local-only mode)

### How You Should Handle API Keys

1. ✅ Keep them secret
2. ✅ Don't share them
3. ✅ Don't commit them to version control
4. ✅ Don't paste them in public chats
5. ✅ Rotate them regularly
6. ✅ Revoke them if leaked

### If Your Key is Leaked

1. **Immediately revoke it:**
   - Go to the API provider's console
   - Delete the compromised key
   - Create a new key

2. **Update Cyber Defense:**
   - Open Settings
   - Enter the new API key
   - Save changes

3. **Monitor usage:**
   - Check API provider's dashboard
   - Review API usage logs
   - Watch for unusual activity

---

## 🔐 Data Privacy

### What We Collect

❌ We do NOT collect:
- Your browsing history
- Your personal data
- Your IP address
- Your location
- Your device information
- Analytics data
- Usage statistics
- Telemetry of any kind

### What Gets Shared

The application operates **100% locally** by default:
- **No external API calls** unless you enable optional APIs
- **Optional**: Google Safe Browsing API - Only the URL being scanned
- **Optional**: VirusTotal API - Only file hashes being checked
- **No other sharing** - All threat detection is processed locally

### What Is Stored

- **Settings**: `~/.cyber-defense/settings.json` - Your preferences
- **Threat Log**: `~/.cyber-defense/threat_log.json` - Detected threats (last 500)
- **Logs**: `~/.cyber-defense/logs/` - Application logs for debugging
- **No cloud sync** - Everything stays on your computer
- **You control deletion** - Delete the folder to remove all data

---

## 🛠️ Supported Versions

### Current Release
- **Version 2.0.0** - Full security support ✅

### Older Versions
- **Version 1.x** - No longer supported, please upgrade

### Support Policy
- Latest version: Always supported
- Previous major version: Supported for 6 months after new release
- Older versions: No support - please upgrade

---

## 📋 Known Issues

Currently no known security vulnerabilities.

If you find one, report it privately per instructions above.

---

## 🔄 Security Updates

### Release Timeline
- Security fixes: ASAP (within 48 hours)
- Updates: Via GitHub releases
- Notifications: Via GitHub releases and CHANGELOG.md

### Update Policy
- All security fixes released immediately
- No waiting for feature releases
- All users notified of security updates
- Details provided in release notes and SECURITY.md

### How to Update
1. Download latest release from GitHub
2. Run the installer (Windows) or install script (Linux)
3. Restart the application

---

## 📚 References

### Security Standards
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Python Security Best Practices](https://python.org/dev/security/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)

### Tools Used
- Ruff linter with security checks (flake8-bandit)
- Pytest for security test cases
- Manual code review
- GitHub Dependabot for dependency monitoring

---

## 💬 Questions?

For security-related questions:
- Email: security@cyberdefense.local
- Avoid public discussions
- Keep sensitive information private

---

## 📄 License

This security policy is part of the Real-World Cyber Defense project and is licensed under MIT License.

---

**Thank you for helping keep this project secure!** 🛡️
