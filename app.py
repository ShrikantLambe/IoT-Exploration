import os
import time
from typing import Optional

import requests
from flask import Flask, request, jsonify, redirect, url_for

from alexa_oauth import (
    get_authorize_url,
    exchange_code_for_token,
    refresh_access_token,
    save_tokens,
    load_tokens,
)

app = Flask(__name__)

# Load client config from env for security
CLIENT_ID = os.getenv("ALEXA_CLIENT_ID")
CLIENT_SECRET = os.getenv("ALEXA_CLIENT_SECRET")
REDIRECT_URI = os.getenv("ALEXA_REDIRECT_URI", "http://localhost:5000/oauth/callback")
SCOPE = "alexa::proactive_events"

# Simple in-memory map for demo accounts (not secure)
DEMO_ACCOUNT = "demo_user"


@app.route("/oauth/start")
def oauth_start():
    if not CLIENT_ID:
        return jsonify({"error": "ALEXA_CLIENT_ID not set"}), 500
    auth_url = get_authorize_url(CLIENT_ID, REDIRECT_URI, SCOPE, state=DEMO_ACCOUNT)
    return redirect(auth_url)


@app.route("/oauth/callback")
def oauth_callback():
    code = request.args.get("code")
    state = request.args.get("state") or DEMO_ACCOUNT
    if not code:
        return jsonify({"error": "missing code"}), 400
    tokens = exchange_code_for_token(CLIENT_ID, CLIENT_SECRET, code, REDIRECT_URI)
    save_tokens(state, tokens)
    return jsonify({"status": "saved", "account": state})


def get_valid_access_token(account: str) -> Optional[str]:
    tokens = load_tokens(account)
    if not tokens:
        return None
    access_token = tokens.get("access_token")
    expires_in = tokens.get("expires_in")
    obtained_at = tokens.get("obtained_at")
    refresh_token = tokens.get("refresh_token")
    if not obtained_at:
        # save obtained time
        tokens["obtained_at"] = int(time.time())
        save_tokens(account, tokens)
        return access_token
    if int(time.time()) > int(obtained_at) + int(expires_in) - 60:
        # refresh
        new = refresh_access_token(CLIENT_ID, CLIENT_SECRET, refresh_token)
        new["obtained_at"] = int(time.time())
        save_tokens(account, new)
        return new.get("access_token")
    return access_token


# Notifications API example: POST to Alexa Notifications endpoint
ALEXA_NOTIFICATIONS_URL = "https://api.amazonalexa.com/v1/notifications"


def send_notification(access_token: str, title: str, body: str) -> dict:
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "content": {
            "title": title,
            "body": body,
        }
    }
    resp = requests.post(ALEXA_NOTIFICATIONS_URL, json=payload, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()


@app.route("/send", methods=["POST"])
def send():
    data = request.get_json(silent=True) or {}
    message = data.get("message")
    account = data.get("account") or DEMO_ACCOUNT
    if not message:
        return jsonify({"error": "missing 'message'"}), 400
    token = get_valid_access_token(account)
    if not token:
        return jsonify({"error": "no token for account", "authorize": url_for("oauth_start", _external=True)}), 401
    try:
        resp = send_notification(token, "IoT-Exploration", message)
        return jsonify({"status": "sent", "response": resp})
    except requests.HTTPError as e:
        return jsonify({"error": str(e), "details": e.response.text}), 502
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
