# Product development plan

Each round completes one feature or repair. Future items are planned, not implemented claims.

## Current round

project-skeleton

## Roadmap

### project-skeleton — Project skeleton with FastAPI backend and React frontend

Status: done

Acceptance:
- FastAPI app runs with health endpoint
- React + TypeScript + Vite frontend builds
- Dockerfiles for backend and frontend
- docker-compose.yaml with Keycloak
- README with install/run/test steps
- portfolio.json at root

Implementation: `backend/app/main.py`, `backend/app/core/config.py`, `backend/app/core/database.py`, `backend/app/core/logging.py`, `backend/app/models/__init__.py`, `backend/app/services/bedrock_resolver.py`, `backend/app/services/iam_policy_generator.py`, `backend/app/services/plugin_validator.py`, `backend/app/services/bootstrap_token.py`, `backend/app/api/core.py`, `backend/app/tests/test_core.py`, `frontend/src/main.tsx`, `frontend/src/App.tsx`, `frontend/src/api/client.ts`, `frontend/src/hooks/useApi.ts`, `frontend/src/types/index.ts`, `frontend/src/components/Layout.tsx`, `frontend/src/components/BedrockResolver.tsx`, `frontend/src/components/IAMPolicyGenerator.tsx`, `frontend/src/components/PluginValidator.tsx`, `frontend/src/components/BootstrapToken.tsx`, `frontend/src/components/SystemStatus.tsx`, `frontend/src/components/styles.css`, `frontend/src/pages/DashboardPage.tsx`, `frontend/src/pages/BedrockPage.tsx`, `frontend/src/pages/IAMPage.tsx`, `frontend/src/pages/PluginsPage.tsx`, `frontend/src/pages/BootstrapPage.tsx`, `frontend/src/test/setup.ts`, `frontend/src/components/Components.test.tsx`, `backend/Dockerfile`, `frontend/Dockerfile`, `frontend/nginx.conf`, `docker-compose.yaml`, `README.md`, `portfolio.json`, `LICENSE`, `CHANGELOG.md`, `pyproject.toml`, `.github/workflows/ci.yml`, `.gitignore`, `.env.example`, `keycloak/realm-export.json`

Tests: `backend/app/tests/test_core.py (25 tests)`, `frontend/src/components/Components.test.tsx (8 tests)`

### bedrock-model-resolver — Bedrock model identifier resolver for AU/EU/APAC regions

Status: planned

Acceptance:
- Resolves correct inference profile prefix (us/eu/au/apac) from region
- Maps foundation model IDs to cross-region inference profiles
- Validates against known Bedrock region capabilities
- Unit tests covering region-to-prefix mapping

### iam-policy-generator — IAM policy template generator with region-aware prefixes

Status: planned

Acceptance:
- Generates IAM policy with correct geographic prefix
- Supports us/eu/au/apac prefixes based on region
- Template renders valid JSON policy
- Tests for each region prefix

### bootstrap-token-refresh — Bootstrap endpoint with MSAL token refresh logic

Status: planned

Acceptance:
- Acquires fresh token via acquireTokenSilent before bootstrap call
- Handles token expiry with bootstrap_expires_at
- Falls back to interactive login on silent auth failure
- Integration test with mock MSAL

### hooks-json-validator — Plugin hooks.json schema validator

Status: planned

Acceptance:
- Validates hooks.json against expected schema
- Detects bare array vs object format
- CLI command to check all plugins
- Fixes invalid hooks.json files

### mcp-json-validator — MCP JSON syntax validator for plugin connectors

Status: planned

Acceptance:
- Parses and validates .mcp.json files
- Detects missing commas and unclosed braces
- Reports line/column of syntax errors
- CI check for all .mcp.json files

### wealth-management-restoration — Wealth management plugin restoration with financial planning workflow

Status: planned

Acceptance:
- Restores /financial-plan command
- Implements portfolio rebalancing workflow
- Includes tax-loss harvesting (/tlh) workflow
- Marked as community-maintained

### oidc-auth-complete — Complete OIDC authentication with Keycloak

Status: planned

Acceptance:
- Authorization code flow with PKCE
- State + nonce validation
- Role-based access control (viewer/analyst/admin)
- HttpOnly cookies with CSRF protection
- Login/logout flows working

