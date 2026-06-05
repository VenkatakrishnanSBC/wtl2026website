"""Service-account authentication for the GA4 Data API and GSC Search Console API.

Uses google-auth Application Default Credentials (ADC) by default — set
GOOGLE_APPLICATION_CREDENTIALS to your service-account JSON key — or an explicit
``--credentials path.json`` override. The same service account must be granted
read access in BOTH GA4 (Property Access Management) and GSC (Users and permissions).
"""

from __future__ import annotations

from typing import Optional

# Read-only scopes. GA4 Data API needs analytics.readonly; GSC needs webmasters.readonly.
GA4_SCOPES = ("https://www.googleapis.com/auth/analytics.readonly",)
GSC_SCOPES = ("https://www.googleapis.com/auth/webmasters.readonly",)
ALL_SCOPES = tuple(set(GA4_SCOPES) | set(GSC_SCOPES))


class AuthError(Exception):
    """Raised when credentials cannot be loaded."""


def credentials_for(config, scopes: tuple[str, ...]):
    """Resolve credentials from a Config: OAuth access token wins, else SA/ADC.

    Token-based auth (OAuth Playground model): when ``config.oauth_access_token``
    is set, build plain OAuth2 credentials from the bearer token. The token must
    have been authorized with the needed scopes (analytics.readonly,
    webmasters.readonly) — e.g. via https://developers.google.com/oauthplayground.
    Access tokens expire after ~1 hour; regenerate and update OAUTH_ACCESS_TOKEN
    when they do.
    """
    token = getattr(config, "oauth_access_token", None)
    quota_project = getattr(config, "quota_project", None)
    if token:
        try:
            from google.oauth2.credentials import Credentials as UserCredentials
        except ImportError as exc:  # pragma: no cover - dependency guard
            raise AuthError(
                "google-auth is not installed. Run: pip install -r requirements.txt"
            ) from exc
        creds = UserCredentials(token=token)
        if quota_project:
            creds = creds.with_quota_project(quota_project)
        return creds

    creds = load_credentials(config.credentials_path, scopes)
    if quota_project and hasattr(creds, "with_quota_project"):
        creds = creds.with_quota_project(quota_project)
    return creds


def load_credentials(credentials_path: Optional[str], scopes: tuple[str, ...]):
    """Load service-account credentials with the given scopes.

    Args:
        credentials_path: Explicit path to a service-account JSON key, or None to
            use ADC (GOOGLE_APPLICATION_CREDENTIALS / gcloud default).
        scopes: OAuth scopes to request.

    Returns:
        A ``google.auth.credentials.Credentials`` object.

    Raises:
        AuthError: When no credentials can be located, with setup guidance.
    """
    try:
        from google.oauth2 import service_account  # local import keeps CLI --help fast
    except ImportError as exc:  # pragma: no cover - dependency guard
        raise AuthError(
            "google-auth is not installed. Run: pip install -r requirements.txt"
        ) from exc

    if credentials_path:
        try:
            return service_account.Credentials.from_service_account_file(
                credentials_path, scopes=list(scopes)
            )
        except Exception as exc:  # noqa: BLE001
            raise AuthError(
                f"Failed to load service-account key from {credentials_path}: {exc}"
            ) from exc

    # Fall back to ADC.
    try:
        import google.auth

        creds, _project = google.auth.default(scopes=list(scopes))
        return creds
    except Exception as exc:  # noqa: BLE001
        raise AuthError(
            "No credentials found. Set GOOGLE_APPLICATION_CREDENTIALS to a "
            "service-account JSON key, or pass --credentials path.json.\n"
            "See README.md 'Authentication setup'."
        ) from exc


def service_account_email(credentials_path: Optional[str]) -> Optional[str]:
    """Return the service-account email from the key file, if available.

    Used by error messages and ``verify`` so the user knows exactly which email to
    grant access to in GA4/GSC.
    """
    if not credentials_path:
        return None
    try:
        import json

        with open(credentials_path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data.get("client_email")
    except Exception:  # noqa: BLE001 - non-fatal, only for nicer messages
        return None
