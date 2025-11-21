"""Blueprint for authentication routes using OAuth2 authorization code flow."""

import os
import json
import msal
from flask import Blueprint, redirect, url_for, session, request
import src.app_logging as al

# pylint: disable=W1203

auth_bp = Blueprint("auth", __name__)

CLIENT_ID = os.environ.get("MSAL_CLIENT_ID")
AUTHORITY = os.environ.get("AUTHORITY")  # Use '/common' for multi-tenant
SCOPE = [os.environ.get("SCOPE")]  # Adjust scope as needed
REDIRECT_URI = os.environ.get("REDIRECT_URI")  # Adjust for your app


# Function to get MSAL app instance with token cache
def get_msal_app():
    """Create and return a MSAL ConfidentialClientApplication instance."""
    cache = msal.SerializableTokenCache()
    if "token_cache" in session:
        cache.deserialize(json.loads(session["token_cache"]))
    return msal.ConfidentialClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        client_credential=os.environ.get("MSAL_CLIENT_SECRET"),
        token_cache=cache,
    )


# TODO: add cleanup function
def save_token_cache(msal_app):
    """Save the token cache to session."""
    if msal_app.token_cache:
        serialized = json.dumps(msal_app.token_cache.serialize())
        session["token_cache"] = serialized
        # persist to a secure file whose directory is set by env var
        try:
            import os, tempfile

            cache_dir = os.environ.get("MSAL_CACHE_DIR")
            try:
                os.makedirs(cache_dir, exist_ok=True)
            except Exception:
                pass
            # determine user id from id token claims
            user = session.get("user") or {}
            user_id = user.get("sub") or user.get("oid")
            if user_id:
                filename = f"msalcache_{user_id}.json"
                path = os.path.join(cache_dir, filename)
                al.logger.debug(f"Saving token cache to {path}")
                with open(path, "w") as f:
                    f.write(serialized)
                try:
                    os.chmod(path, 0o600)
                    al.logger.info(
                        f"Token cache saved to {path} with restricted permissions"
                    )
                except Exception as e:
                    al.logger.warning(
                        f"Failed to set restricted permissions on token cache file {path}: {e}"
                    )
        except Exception:
            # fall back to session-only cache
            pass


@auth_bp.route("/login")
def login():
    """Redirect user to Azure AD sign-in page."""
    msal_app = get_msal_app()
    auth_url = msal_app.get_authorization_request_url(
        SCOPE, redirect_uri=REDIRECT_URI
    )
    return redirect(auth_url)


@auth_bp.route("/")
def root_login():
    """Root path serves as login entrypoint."""
    return redirect(url_for("auth.login"))


@auth_bp.route("/getAToken")
def authorized():
    """Handle the redirect from Azure AD and acquire token."""
    msal_app = get_msal_app()
    result = msal_app.acquire_token_by_authorization_code(
        request.args["code"], scopes=SCOPE, redirect_uri=REDIRECT_URI
    )
    if "access_token" in result:
        session["user"] = result.get("id_token_claims")
        session["authenticated"] = True
        save_token_cache(msal_app)
        return redirect(url_for("workspace.form_no_creds"))
    else:
        return redirect(url_for("workspace.collect_workspace_info"))


@auth_bp.route("/logout")
def logout():
    """Logout user."""
    # remove any token cache file we created
    try:
        import os

        user = session.get("user") or {}
        user_id = user.get("sub") or user.get("oid")
        if user_id:
            cache_dir = os.environ.get("MSAL_CACHE_DIR")
            if not cache_dir:
                import tempfile

                cache_dir = tempfile.gettempdir()
            path = os.path.join(cache_dir, f"msalcache_{user_id}.json")
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
    except Exception:
        pass
    session.clear()
    return redirect(url_for("auth.login"))
