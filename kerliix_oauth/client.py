import base64
import hashlib
import os
import time
import requests
from urllib.parse import urlencode
from typing import List, Optional, Dict, Any
from .cache import TokenCache
from .types import TokenResponse, UserInfo, OAuthError


def base64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode().rstrip("=")


def generate_code_verifier() -> str:
    return base64url_encode(os.urandom(32))


def generate_code_challenge(verifier: str) -> str:
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64url_encode(digest)


class KerliixOAuth:
    def __init__(self, client_id: str, redirect_uri: str, base_url: str, client_secret: Optional[str] = None):
        if not client_id or not redirect_uri:
            raise ValueError("client_id and redirect_uri are required")

        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.base_url = base_url.rstrip("/") if base_url else "https://api.kerliix.com"
        self.cache = TokenCache()

    # --- Generate Authorization URL ---
    def get_auth_url(self, scopes: Optional[List[str]] = None, state: str = "", use_pkce: bool = False) -> Dict[str, Any]:
        scopes = scopes or ["openid", "profile", "email"]

        params = {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "response_type": "code",
            "scope": " ".join(scopes),
            "state": state,
        }

        code_verifier = None
        if use_pkce:
            code_verifier = generate_code_verifier()
            params["code_challenge"] = generate_code_challenge(code_verifier)
            params["code_challenge_method"] = "S256"

        url = f"{self.base_url}/oauth/authorize?{urlencode(params)}"
        return {"url": url, "code_verifier": code_verifier}

    # --- Exchange code for token ---
    def exchange_code_for_token(self, code: str, code_verifier: Optional[str] = None) -> TokenResponse:
        if not code:
            raise OAuthError("invalid_request", "Authorization code is required")

        url = f"{self.base_url}/oauth/token"
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        if self.client_secret:
            auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
            headers["Authorization"] = f"Basic {auth_header}"

        data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.redirect_uri,
        }
        if code_verifier:
            data["code_verifier"] = code_verifier

        resp = requests.post(url, data=data, headers=headers)
        data = self._handle_response(resp, "token_exchange_failed")

        token = TokenResponse(**data)
        self.cache.set(token)
        return token

    # --- Refresh token if expired ---
    def refresh_token_if_needed(self) -> Optional[TokenResponse]:
        cached = self.cache.get()
        if cached:
            return cached

        last = self.cache.token
        if not last or not last.refresh_token or not self.client_secret:
            return None

        url = f"{self.base_url}/oauth/token"
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}",
        }
        data = {
            "grant_type": "refresh_token",
            "refresh_token": last.refresh_token,
        }

        resp = requests.post(url, data=data, headers=headers)
        data = self._handle_response(resp, "refresh_failed")

        token = TokenResponse(**data)
        self.cache.set(token)
        return token

    # --- Get user info ---
    def get_user_info(self, access_token: Optional[str] = None) -> UserInfo:
        token = access_token or (self.refresh_token_if_needed().access_token if self.refresh_token_if_needed() else None)
        if not token:
            raise OAuthError("missing_token", "No access token available")

        url = f"{self.base_url}/oauth/userinfo"
        resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
        data = self._handle_response(resp, "userinfo_fetch_failed")
        return UserInfo(**data)

    # --- Revoke token ---
    def revoke_token(self, token: str) -> bool:
        if not token:
            raise OAuthError("invalid_request", "Token is required")
        if not self.client_secret:
            raise OAuthError("unauthorized_client", "Client secret required")

        url = f"{self.base_url}/oauth/revoke"
        auth_header = base64.b64encode(f"{self.client_id}:{self.client_secret}".encode()).decode()
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}",
        }
        resp = requests.post(url, data={"token": token}, headers=headers)
        self._handle_response(resp, "revoke_failed")
        self.cache.clear()
        return True

    # --- Centralized error handler ---
    def _handle_response(self, resp: requests.Response, default_error: str) -> Dict[str, Any]:
        try:
            data = resp.json()
        except Exception:
            data = {"error": default_error, "error_description": resp.text}

        if not resp.ok or "error" in data:
            raise OAuthError(data.get("error", default_error), data.get("error_description", "Unknown error"))

        return data
