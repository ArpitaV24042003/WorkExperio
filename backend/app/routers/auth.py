# backend/app/routers/auth.py
import os
import logging
from typing import Optional

from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlalchemy.orm import Session

# local imports
from app.database import SessionLocal
from app.models import User  # ensure User model includes github_id, avatar_url, auth_provider

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------- Env / Defaults ----------
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "https://workexperio.onrender.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://workexperio-4.onrender.com")  # change to your frontend prod URL

# Basic safety check: make sure client id/secret exist
if not (GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET):
    logger.warning("GITHUB_CLIENT_ID or GITHUB_CLIENT_SECRET not set. OAuth will fail until provided.")

# Starlette Config for Authlib (we pass env via the Config's environ dict)
config = Config(environ={
    "GITHUB_CLIENT_ID": GITHUB_CLIENT_ID,
    "GITHUB_CLIENT_SECRET": GITHUB_CLIENT_SECRET,
})
oauth = OAuth(config)

oauth.register(
    name="github",
    client_id=GITHUB_CLIENT_ID,
    client_secret=GITHUB_CLIENT_SECRET,
    access_token_url="https://github.com/login/oauth/access_token",
    authorize_url="https://github.com/login/oauth/authorize",
    api_base_url="https://api.github.com/",
    client_kwargs={"scope": "read:user user:email"},
)


@router.get("/github/login")
async def github_login(request: Request):
    """
    Start OAuth login: redirect to GitHub authorize page.
    Ensure your GitHub app's Authorization callback URL is:
      {BACKEND_BASE_URL}/auth/github/callback
    """
    if not (GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET):
        raise HTTPException(status_code=500, detail="GitHub OAuth client ID/secret not configured on server.")
    redirect_uri = f"{BACKEND_BASE_URL}/auth/github/callback"
    # authlib will use request.session (SessionMiddleware must be enabled)
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_callback(request: Request):
    """
    GitHub will redirect here after user authorizes. We exchange code -> token,
    fetch user profile, upsert to Postgres, then redirect to frontend.
    """
    try:
        # exchange code for token (this will use saved session data)
        token = await oauth.github.authorize_access_token(request)

        # primary profile
        user_resp = await oauth.github.get("user", token=token)
        userinfo = user_resp.json()

        # Email fallback: GitHub may hide email in /user; fetch /user/emails if missing
        email: Optional[str] = userinfo.get("email")
        if not email:
            try:
                emails_resp = await oauth.github.get("user/emails", token=token)
                emails = emails_resp.json() or []
                # pick primary + verified, or first verified, or first
                primary = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
                if not primary:
                    primary = next((e["email"] for e in emails if e.get("verified")), None)
                email = primary or (emails[0]["email"] if emails else None)
            except Exception:
                email = None

        github_id = str(userinfo.get("id"))
        username = userinfo.get("login", f"github_{github_id}")
        avatar = userinfo.get("avatar_url")

        # Upsert into Postgres
        db: Session = SessionLocal()
        try:
            existing = db.query(User).filter(User.github_id == github_id).first()
            if not existing:
                new_user = User(
                    name=username,
                    email=email or f"{username}@github.local",
                    github_id=github_id,
                    avatar_url=avatar,
                    auth_provider="github",
                    password=None,  # allow nullable password for OAuth users
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                existing = new_user
                logger.info("Created new user from GitHub: %s (id=%s)", username, existing.id)
            else:
                # optionally update avatar/email if changed
                updated = False
                if email and existing.email != email:
                    existing.email = email
                    updated = True
                if avatar and existing.avatar_url != avatar:
                    existing.avatar_url = avatar
                    updated = True
                if updated:
                    db.commit()
                    logger.info("Updated user %s with new GitHub info", existing.id)
        finally:
            db.close()

        # TEMP: redirect to frontend with user query param.
        # In prod replace this with a JWT or set secure httpOnly cookie from backend.
        return RedirectResponse(f"{FRONTEND_URL}/dashboard?user={existing.name}")

    except Exception as e:
        logger.exception("GitHub OAuth callback error")
        # Return 400 with short message (avoid leaking internals in production)
        raise HTTPException(status_code=400, detail=f"OAuth error: {e}")
