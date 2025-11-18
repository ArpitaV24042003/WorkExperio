from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os
import logging
from typing import Optional

from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

from ..db import get_db, SessionLocal
from ..models import User, UserStats
from ..schemas import UserCreate, UserLogin, TokenResponse
from ..security import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)
router = APIRouter()

# ---------- GitHub OAuth Configuration ----------
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

# Basic safety check: make sure client id/secret exist
if not (GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET):
    logger.warning("GITHUB_CLIENT_ID or GITHUB_CLIENT_SECRET not set. OAuth will fail until provided.")

# Starlette Config for Authlib
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


@router.post("/signup", response_model=TokenResponse)
def signup(payload: UserCreate, db: Session = Depends(get_db)):
	try:
		# Check if email already exists - if so, return existing user's token (retain history)
		existing_user = db.query(User).filter(User.email == payload.email).first()
		if existing_user:
			# User exists - update name if provided and return existing token
			if payload.name and existing_user.name != payload.name:
				existing_user.name = payload.name
				db.commit()
				db.refresh(existing_user)
			# Generate new token for existing user (they're logging back in)
			token = create_access_token(existing_user.id)
			return TokenResponse(access_token=token)

		# Hash password
		password_hash = hash_password(payload.password)
		
		# Create user
		user = User(
			name=payload.name,
			email=payload.email,
			password_hash=password_hash,
		)
		db.add(user)
		db.flush()  # Get user.id without committing

		# Create UserStats for the new user
		try:
			stats = UserStats(user_id=user.id)
			db.add(stats)
		except Exception as stats_error:
			logger.error(f"Error creating UserStats for user {user.id}: {stats_error}")
			db.rollback()
			raise HTTPException(
				status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
				detail="Failed to create user profile"
			)

		# Commit both user and stats
		db.commit()
		db.refresh(user)

		# Generate token
		token = create_access_token(user.id)
		return TokenResponse(access_token=token)
	except HTTPException:
		raise
	except Exception as e:
		logger.exception("Signup error")
		db.rollback()
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Registration failed: {str(e)}"
		)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
	try:
		# Query user by email
		user = db.query(User).filter(User.email == payload.email).first()
		if not user:
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
		
		# OAuth users don't have password_hash
		if user.password_hash is None:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="This account uses OAuth authentication. Please sign in with GitHub."
			)
		
		# Verify password
		if not verify_password(payload.password, user.password_hash):
			raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

		# Generate token
		token = create_access_token(user.id)
		return TokenResponse(access_token=token)
	except HTTPException:
		raise
	except Exception as e:
		logger.exception("Login error")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail=f"Login failed: {str(e)}"
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
                    password_hash=None,  # Nullable for OAuth users
                    github_id=github_id,
                    avatar_url=avatar,
                    auth_provider="github",
                )
                db.add(new_user)
                db.flush()  # Flush to get user.id
                
                # Create UserStats for new OAuth user (same as signup)
                stats = UserStats(user_id=new_user.id)
                db.add(stats)
                
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
