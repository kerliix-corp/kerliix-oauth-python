import time
from typing import Optional
from .types import TokenResponse


class TokenCache:
    def __init__(self):
        self.token: Optional[TokenResponse] = None

    def set(self, token: TokenResponse):
        token.created_at = int(time.time())
        self.token = token

    def get(self) -> Optional[TokenResponse]:
        if not self.token:
            return None

        now = int(time.time())
        expiry = (self.token.created_at or 0) + self.token.expires_in
        if now >= expiry - 30:
            return None
        return self.token

    def clear(self):
        self.token = None
