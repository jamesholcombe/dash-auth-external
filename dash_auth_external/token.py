from dataclasses import dataclass
import time


@dataclass
class OAuth2Token:
    access_token: str
    token_type: str = None
    expires_in: int = None
    refresh_token: str = None
    expires_at: float = None
    scope: str = None
    id_token: str = None

    def __post_init__(self):
        if self.expires_at is None and self.expires_in is not None:
            self.expires_at = time.time() + float(self.expires_in)

    def is_expired(self):
        return time.time() > self.expires_at if self.expires_at else False
