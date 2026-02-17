import json
import os
from typing import Optional
import requests

AUTH_URL = "https://www.amazon.com/ap/oa"
TOKEN_URL = "https://api.amazon.com/auth/o2/token"


def get_authorize_url(client_id: str, redirect_uri: str, scope: str, state: Optional[str] = None) -> str:
    """Return the Amazon LWA authorization URL to redirect users to."""
    params = {
        "client_id": client_id,
        "scope": scope,
        "response_type": "code",
        "redirect_uri": redirect_uri,
    }
    if state:
        params["state"] = state
    # Build URL
    from urllib.parse import urlencode

    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(client_id: str, client_secret: str, code: str, redirect_uri: str) -> dict:
    """Exchange an authorization code for tokens (access + refresh)."""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
    }
    resp = requests.post(TOKEN_URL, data=data, timeout=10)
    resp.raise_for_status()
    return resp.json()


def refresh_access_token(client_id: str, client_secret: str, refresh_token: str) -> dict:
    """Obtain a fresh access token using a refresh token."""
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    resp = requests.post(TOKEN_URL, data=data, timeout=10)
    resp.raise_for_status()
    return resp.json()


# Simple on-disk token store (single-file). Not for production.
TOKENS_PATH = os.getenv("TOKENS_PATH", "tokens.json")


def _read_tokens() -> dict:
    try:
        with open(TOKENS_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _write_tokens(data: dict):
    with open(TOKENS_PATH, "w") as f:
        json.dump(data, f, indent=2)


def save_tokens(account_id: str, tokens: dict):
    data = _read_tokens()
    data[account_id] = tokens
    _write_tokens(data)


def load_tokens(account_id: str) -> Optional[dict]:
    data = _read_tokens()
    return data.get(account_id)
