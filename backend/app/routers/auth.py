# backend/app/routers/auth.py
import os
from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuth
from starlette.config import Config

router = APIRouter(prefix="/auth", tags=["Auth"])

# Read from env (Render → Environment)
GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET", "")
BACKEND_BASE_URL = os.getenv("BACKEND_BASE_URL", "https://workexperio.onrender.com")
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://<your-frontend>.onrender.com")

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

@router.get("/github/login")
async def github_login(request: Request):
    redirect_uri = f"{BACKEND_BASE_URL}/auth/github/callback"
    return await oauth.github.authorize_redirect(request, redirect_uri)

@router.get("/github/callback")
async def github_callback(request: Request):
    try:
        token = await oauth.github.authorize_access_token(request)
        user = await oauth.github.get("user", token=token)
        userinfo = user.json()

        # TODO: look up / create user in your DB here (userinfo["id"], userinfo["login"], userinfo["email"], ...)

        # Option A: issue your own JWT and pass it back to frontend
        # jwt_token = make_jwt_for(userinfo["id"])
        # return RedirectResponse(f"{FRONTEND_URL}/dashboard?token={jwt_token}")

        # Option B: set a cookie on backend domain then redirect to FE
        # response = RedirectResponse(f"{FRONTEND_URL}/dashboard")
        # response.set_cookie("session", session_value, httponly=True, secure=True, samesite="none")
        # return response

        # Temporary: just go to frontend dashboard with GitHub username
        gh = userinfo.get("login", "user")
        return RedirectResponse(f"{FRONTEND_URL}/dashboard?user={gh}")

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OAuth error: {e}")
