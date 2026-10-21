"""
Bootstrap Token Service - Handles MSAL token acquisition and refresh for bootstrap endpoint.

Implements acquireTokenSilent flow before calling bootstrap endpoint.
"""

import time
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class TokenSource(str, Enum):
    CACHE = "cache"
    SILENT_REFRESH = "silent_refresh"
    INTERACTIVE = "interactive"


@dataclass(frozen=True)
class TokenInfo:
    access_token: str
    expires_at: int  # Unix timestamp
    token_source: TokenSource
    expires_in: int  # Seconds until expiry


@dataclass(frozen=True)
class BootstrapConfig:
    bootstrap_url: str
    client_id: str
    tenant_id: str
    scopes: list[str]
    authority: str


class MockMSALClient:
    """
    Mock MSAL client for testing and development.

    In production, this would be replaced with the actual msal library.
    """

    def __init__(self, config: BootstrapConfig):
        self.config = config
        self._token_cache: dict[str, TokenInfo] = {}

    def acquire_token_silent(self, account: Optional[str] = None) -> Optional[TokenInfo]:
        """
        Attempt to acquire token silently from cache/refresh token.

        Returns TokenInfo if successful, None if silent auth fails.
        """
        # In real implementation, this would call msal.ConfidentialClientApplication.acquire_token_silent
        # For mock, return cached token if not expired
        cache_key = account or "default"
        if cache_key in self._token_cache:
            token = self._token_cache[cache_key]
            if token.expires_at > int(time.time()) + 60:  # 60s buffer
                return TokenInfo(
                    access_token=token.access_token,
                    expires_at=token.expires_at,
                    token_source=TokenSource.CACHE,
                    expires_in=token.expires_at - int(time.time()),
                )
        return None

    def acquire_token_interactive(self, account: Optional[str] = None) -> TokenInfo:
        """
        Acquire token interactively (user login).

        In real implementation, this would initiate auth code flow.
        """
        # Mock: generate a fake token
        expires_at = int(time.time()) + 3600  # 1 hour
        token = f"mock-token-{int(time.time())}"
        token_info = TokenInfo(
            access_token=token,
            expires_at=expires_at,
            token_source=TokenSource.INTERACTIVE,
            expires_in=3600,
        )
        cache_key = account or "default"
        self._token_cache[cache_key] = token_info
        return token_info

    def get_cached_token(self, account: Optional[str] = None) -> Optional[TokenInfo]:
        """Get cached token without checking expiry."""
        cache_key = account or "default"
        return self._token_cache.get(cache_key)


class BootstrapTokenManager:
    """
    Manages token acquisition for bootstrap endpoint calls.

    Implements the correct flow:
    1. Try acquireTokenSilent first
    2. If that fails, fall back to interactive login
    3. Use the fresh token for bootstrap call
    """

    def __init__(self, config: BootstrapConfig, msal_client: Optional[MockMSALClient] = None):
        self.config = config
        self.msal_client = msal_client or MockMSALClient(config)

    def get_valid_token(self, account: Optional[str] = None) -> TokenInfo:
        """
        Get a valid token for bootstrap call.

        Implements the correct flow: silent refresh first, then interactive.
        """
        # Step 1: Try silent refresh
        token = self.msal_client.acquire_token_silent(account)
        if token:
            return token

        # Step 2: Fall back to interactive
        return self.msal_client.acquire_token_interactive(account)

    def call_bootstrap(self, token: str) -> dict:
        """
        Call the bootstrap endpoint with a valid token.

        In real implementation, this would make an HTTP request.
        """
        # Mock implementation - in reality this would be:
        # import httpx
        # response = httpx.get(
        #     self.config.bootstrap_url,
        #     headers={"Authorization": f"Bearer {token}"},
        #     timeout=30.0,
        # )
        # response.raise_for_status()
        # return response.json()

        return {
            "gateway_token": token,
            "bootstrap_expires_at": int(time.time()) + 3600,
        }

    def bootstrap_flow(self, account: Optional[str] = None) -> dict:
        """
        Complete bootstrap flow: get valid token, call bootstrap endpoint.

        This is the main entry point for the add-in.
        """
        token_info = self.get_valid_token(account)
        result = self.call_bootstrap(token_info.access_token)
        return {
            **result,
            "token_source": token_info.token_source.value,
            "token_expires_in": token_info.expires_in,
        }


# Configuration helper
def create_bootstrap_config(
    bootstrap_url: str,
    client_id: str,
    tenant_id: str,
    scopes: Optional[list[str]] = None,
) -> BootstrapConfig:
    """Create bootstrap configuration."""
    return BootstrapConfig(
        bootstrap_url=bootstrap_url,
        client_id=client_id,
        tenant_id=tenant_id,
        scopes=scopes or ["https://cognitiveservices.azure.com/.default"],
        authority=f"https://login.microsoftonline.com/{tenant_id}",
    )