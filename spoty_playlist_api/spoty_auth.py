from fastapi import Request, HTTPException, Response
from fastapi.responses import RedirectResponse
import requests
import os
from fastapi import APIRouter

# Spotify API credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SCOPES = "playlist-modify-private playlist-modify-public user-modify-playback-state user-read-playback-state playlist-read-private user-follow-read user-top-read"
# Spotify API auth URL
REDIRECT_URI = "http://localhost:8000/callback"
AUTH_URL = f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&scope={SCOPES}&redirect_uri={REDIRECT_URI}"
# Spotify API token URL
TOKEN_URL = "https://accounts.spotify.com/api/token"
# Redirect URL after login
REDIRECT_RESPONSE_URL = "http://localhost:8000/static/index3.html?#showForm"


spotify_oauth_router = APIRouter()


@spotify_oauth_router.get("/login")
def read_root():
    return RedirectResponse(url=AUTH_URL)


@spotify_oauth_router.get("/callback")
def callback(code: str, request: Request, response: Response) -> RedirectResponse:
    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URI,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    token_response = requests.post(TOKEN_URL, data=payload)
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error retrieving access token")

    token_data = token_response.json()
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    # set the response to redirect to the frontend
    response = RedirectResponse(url=REDIRECT_RESPONSE_URL)

    # JUST FOR TESTING PORPUSES
    # not super secure
    response.set_cookie(
        path="/",
        domain="localhost",
        key="accessToken",
        value=access_token,
        httponly=False,
        secure=False,  # Set to True in production with HTTPS
        samesite="Lax",
    )

    return response
