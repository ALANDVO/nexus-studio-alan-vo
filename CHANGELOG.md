# Changelog

## 1.0.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

# Nexus Studio - Changelog

## [1.0.0] - 2024-10-21

### Added
- Initial project skeleton with FastAPI backend and React + TypeScript frontend
- Bedrock Model Resolver: region-aware inference profile ID resolution (us/eu/au/apac prefixes)
- IAM Policy Generator: region-aware IAM policies for Bedrock access
- Plugin Validator: validates and fixes hooks.json and .mcp.json configuration files
- Bootstrap Token Manager: MSAL acquireTokenSilent flow for bootstrap endpoints
- Dockerfiles for backend and frontend with non-root users
- docker-compose.yaml with Keycloak, persistent volumes, healthchecks
- Comprehensive test suite (15+ backend tests)
- CI/CD workflow (GitHub Actions)
- MIT License

### Security
- HttpOnly SameSite cookies with CSRF protection for authentication
- Non-root Docker users
- Secure defaults with environment-based configuration
- No hardcoded secrets or credentials

### Documentation
- README with install/run/test instructions
- Architecture diagram (Mermaid)
- API endpoint reference
- Provider configuration table
- SSO/SAML setup guide