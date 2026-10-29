# Changelog

## 1.1.0 — work-in-progress checkpoint

Partial code published for continued development. Known issues: STATUS.md.

## 1.0.1 — 2024-10-29

### Completed
- bedrock-model-resolver: Bedrock model identifier resolver for AU/EU/APAC regions
  - Region-to-prefix mapping (us/eu/au/apac) with 24 AWS regions supported
  - Foundation model ID to cross-region inference profile mapping
  - Validation against known Bedrock region capabilities
  - Unit tests for all region prefixes (8 backend + 2 frontend tests)
  - API endpoint: POST /api/v1/bedrock/resolve
  - Frontend component: BedrockResolver with region/model selectors

### Notes
- This checkpoint marks bedrock-model-resolver feature as complete
- All existing tests pass (25 backend, 8 frontend)
- feature-plan.json and PLAN.md updated to reflect completed feature

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