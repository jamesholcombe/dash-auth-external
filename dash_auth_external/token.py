from dataclasses import dataclass
import time


@dataclass
class OAuth2Token:
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

    def __post_init__(self):
        self.expires_at = time.time() + self.expires_in

    def is_expired(self):
        return time.time() > self.expires_at if self.expires_at else False
