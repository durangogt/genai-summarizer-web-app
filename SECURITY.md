# Security Policy

## Overview

This repository contains a self-hosted Python application for document summarization. Security is a top priority, especially for this public repository.

## 🔒 Security Best Practices

### For Repository Users

1. **Never Commit Secrets**
   - Do NOT commit API keys, tokens, or passwords to version control
   - Use the `.env` file for sensitive configuration (already in `.gitignore`)
   - Keep your Azure OpenAI credentials secure and private

2. **Environment Variables**
   - Always use environment variables for configuration
   - Review `.env.template` for required variables
   - Never share your actual `.env` file

3. **Dependencies**
   - Regularly update Python packages: `pip install --upgrade -r requirements.txt`
   - Review security advisories for installed packages
   - Use virtual environments to isolate dependencies

4. **Access Control**
   - Use strong, unique passwords for JWT secret keys
   - Implement rate limiting in production deployments
   - Enable HTTPS for production environments

5. **File Uploads**
   - The application enforces a 10MB file size limit
   - Only accepted file types: PDF, DOCX, TXT
   - Validate all uploaded content before processing

### For Contributors

1. **Code Review**
   - All changes require review before merging
   - Never include credentials in code or tests
   - Follow secure coding practices

2. **Testing**
   - Test security-sensitive features thoroughly
   - Use mock credentials in tests (never real ones)
   - Verify input validation and error handling

3. **Documentation**
   - Document security requirements clearly
   - Update security guides when making changes
   - Include security considerations in PRs

## 🌐 GitHub Pages Security

The GitHub Pages deployment is secure by design:

### What's Deployed
- ✅ **Static HTML/CSS documentation** - Safe, read-only content
- ✅ **Public API reference** - No secrets, just endpoint descriptions
- ✅ **Setup guides** - General instructions without credentials

### What's NOT Deployed
- ❌ **No backend code** - Python application stays in repository only
- ❌ **No secrets or API keys** - All credentials remain local
- ❌ **No database connections** - Documentation is static
- ❌ **No user data** - No sensitive information exposed

### Workflow Security
- **Minimal permissions**: `contents: read`, `pages: write`, `id-token: write`
- **Shallow clones**: Uses `fetch-depth: 1` to minimize data exposure
- **Latest actions**: Uses maintained, secure GitHub Actions
- **Concurrency control**: Prevents race conditions
- **Environment protection**: Leverages GitHub's security features

## 🐛 Reporting Vulnerabilities

If you discover a security vulnerability in this project:

### Please DO:
1. **Report privately** via GitHub Security Advisories
   - Go to the "Security" tab → "Advisories" → "New draft security advisory"
2. **Include details**:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fix (if available)
3. **Allow time for a fix** before public disclosure

### Please DON'T:
- Don't open public issues for security vulnerabilities
- Don't share exploit details publicly before a fix is available
- Don't test vulnerabilities on production systems you don't own

## 🔐 Security Features

### Application Security

1. **Authentication**
   - JWT token-based authentication
   - Configurable token expiration
   - Secure password hashing

2. **Input Validation**
   - File type validation (PDF, DOCX, TXT only)
   - File size limits (10MB maximum)
   - URL validation for web scraping
   - Text length validation

3. **Error Handling**
   - User-friendly error messages (no stack traces to users)
   - Comprehensive logging for debugging
   - Secure error responses (no sensitive data leakage)

4. **Dependencies**
   - Minimal dependency footprint
   - Well-maintained, security-reviewed packages
   - Regular updates and vulnerability scanning

### Deployment Security

1. **Self-Hosted Model**
   - Full control over data and infrastructure
   - No third-party data sharing
   - Private deployment options available

2. **Environment Isolation**
   - Virtual environment for Python packages
   - Isolated configuration via `.env` files
   - No hardcoded credentials

3. **Network Security**
   - Default localhost binding (127.0.0.1) for development
   - Configurable for production (0.0.0.0 behind reverse proxy)
   - HTTPS recommended for production deployments

## 🛡️ Security Checklist

Before deploying to production:

- [ ] All secrets are in environment variables, not code
- [ ] `.env` file is NOT committed to version control
- [ ] Strong, unique `SECRET_KEY` is configured
- [ ] API keys are rotated regularly
- [ ] HTTPS is enabled (via reverse proxy)
- [ ] Rate limiting is implemented
- [ ] File upload validation is active
- [ ] Dependencies are up to date
- [ ] Logs are monitored for suspicious activity
- [ ] Backups and disaster recovery plans are in place

## 📚 Additional Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)
- [Azure OpenAI Security](https://learn.microsoft.com/en-us/azure/ai-services/openai/how-to/managed-identity)

## 📞 Contact

For security concerns that don't rise to the level of a vulnerability:
- Open a discussion in the repository
- Tag with the `security` label
- Contact the repository maintainers

## 📜 Version History

- **v1.0** (2026-02-13): Initial security policy
  - GitHub Pages deployment security guidelines
  - Application security best practices
  - Vulnerability reporting process

---

**Remember**: Security is everyone's responsibility. When in doubt, ask!
