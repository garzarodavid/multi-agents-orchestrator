from typing import TypedDict


class TokenResponse(TypedDict):
    access_token: str
    expires_in: int
    provider: str
