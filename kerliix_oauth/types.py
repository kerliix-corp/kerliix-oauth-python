from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class TokenResponse:
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "Bearer"
    expires_in: int = 3600
    scope: Optional[str] = None
    created_at: Optional[int] = None


@dataclass
class UserInfo:
    id: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None
    extra: Optional[Dict[str, Any]] = None


class OAuthError(Exception):
    """Custom OAuth error for consistent developer experience."""
    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message
