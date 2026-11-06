## Security Policy

### Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x     | ✅ Yes     |

### Reporting a Vulnerability

**Please do NOT open a public GitHub issue for security vulnerabilities.**

Instead, report them privately via GitHub's [Security Advisory](https://github.com/pameeesd/vectorizador-svg/security/advisories/new) feature, or email the maintainer directly.

Include:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if any)

We aim to respond within **48 hours** and will credit reporters in the release notes.

### Security Design

- File uploads are validated by **magic bytes** (not just Content-Type)
- No files are persisted to disk permanently; temp files are cleaned up after each request
- API rate-limited to 20 req/min per IP
- CORS restricted to configured origins
- Non-root Docker user
- Dependencies audited weekly via GitHub Actions (`pip-audit`, `npm audit`, Trivy)
