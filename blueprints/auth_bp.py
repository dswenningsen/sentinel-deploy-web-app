"""Blueprint for authentication routes using OAuth2 authorization code flow."""

import os
import json
import msal
from flask import Blueprint, redirect, url_for, session, request

auth_bp = Blueprint("auth", __name__)

# Configuration - replace with your values
CLIENT_ID = os.environ.get("MSAL_CLIENT_ID", "YOUR_CLIENT_ID")
AUTHORITY = (
    "https://login.microsoftonline.com/common"  # Use '/common' for multi-tenant
)
SCOPE = ["https://management.azure.com/.default"]  # Adjust scope as needed
REDIRECT_URI = "http://localhost:5000/getAToken"  # Adjust for your app


# Function to get MSAL app instance with token cache
def get_msal_app():
    cache = msal.SerializableTokenCache()
    if "token_cache" in session:
        cache.deserialize(json.loads(session["token_cache"]))
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=os.environ.get(
            "MSAL_CLIENT_SECRET", "YOUR_CLIENT_SECRET"
        ),
        token_cache=cache,
    )


def save_token_cache(msal_app):
    """Save the token cache to session."""
    if msal_app.token_cache:
        session["token_cache"] = json.dumps(msal_app.token_cache.serialize())


@auth_bp.route("/login")
def login():
    """Redirect user to Azure AD sign-in page."""
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        SCOPE, redirect_uri=REDIRECT_URI
    )
    return redirect(auth_url)


@auth_bp.route("/getAToken")
def authorized():
    """Handle the redirect from Azure AD and acquire token."""
    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        request.args["code"], scopes=SCOPE, redirect_uri=REDIRECT_URI
    )
    if "access_token" in result:
        session["user"] = result.get("id_token_claims")
        session["access_token"] = result["access_token"]
        session["authenticated"] = True
        save_token_cache(msal_app)
        return redirect(url_for("workspace.collect_workspace_info"))
    else:
        return f"Token acquisition failed: {result.get('error_description')}"


@auth_bp.route("/logout")
def logout():
    """Logout user."""
    session.clear()
    return redirect(url_for("auth.login"))
