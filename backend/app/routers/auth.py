# backend/app/routers/auth.py
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config
from sqlalchemy.orm import Session

# local imports
from app.database import SessionLocal
from app.models import User  # ensure User model has github_id, avatar_url, auth_provider, password nullable

# --- router must be defined before decorators are used ---
router = APIRouter(prefix="/auth", tags=["Auth"])

# ---------- Env / Defaults ----------
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://127.0.0.1:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://127.0.0.1:5173")  # change to your frontend prod URL

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
    Redirect user to GitHub OAuth authorize URL.
    Make sure the GitHub app callback URL is:
      {BACKEND_BASE_URL}/auth/github/callback
    """
    redirect_uri = f"{BACKEND_BASE_URL}/auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)


@router.get("/github/callback")
async def github_callback(request: Request):
    """
    GitHub redirects back here. We exchange the code for a token,
    fetch the user's profile, upsert a user record in Postgres, then redirect.
    """
    try:
        token = await oauth.github.authorize_access_token(request)
        # primary profile
        user_resp = await oauth.github.get("user", token=token)
        userinfo = user_resp.json()

        # GitHub may not always return email in /user; if not, fetch from /user/emails
        email = userinfo.get("email")
        if not email:
            emails_resp = await oauth.github.get("user/emails", token=token)
            try:
                # emails_resp.json() is a list; pick the primary verified email
                emails = emails_resp.json()
                primary = next((e["email"] for e in emails if e.get("primary") and e.get("verified")), None)
                email = primary or (emails[0]["email"] if emails else None)
            except Exception:
                email = None

        github_id = str(userinfo.get("id"))
        username = userinfo.get("login", f"github_{github_id}")
        avatar = userinfo.get("avatar_url")

        # Upsert into Postgres (SQLAlchemy)
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
                    password=None,
                )
                db.add(new_user)
                db.commit()
                db.refresh(new_user)
                existing = new_user
            else:
                # Optionally update avatar / email if changed
                updated = False
                if email and existing.email != email:
                    existing.email = email
                    updated = True
                if avatar and existing.avatar_url != avatar:
                    existing.avatar_url = avatar
                    updated = True
                if updated:
                    db.commit()
        finally:
            db.close()

        # Redirect to frontend with a minimal query token (replace with proper JWT/cookie in prod)
        return RedirectResponse(f"{FRONTEND_URL}/dashboard?user={existing.name}")

    except Exception as e:
        # For debugging; in production avoid returning internals
        raise HTTPException(status_code=400, detail=f"OAuth error: {e}")
