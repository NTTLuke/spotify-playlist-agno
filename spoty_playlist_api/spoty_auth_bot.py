from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
import requests
import uuid
from fastapi import APIRouter
import os


CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SCOPES = "playlist-modify-private playlist-modify-public user-modify-playback-state user-read-playback-state playlist-read-private user-follow-read user-top-read"
# Spotify API auth URL
REDIRECT_URL = "http://localhost:8000/bot-login/callback"
AUTH_URL = f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&scope={SCOPES}&redirect_uri={REDIRECT_URL}"
# Spotify API token URL
TOKEN_URL = "https://accounts.spotify.com/api/token"
# Redirect URL after login
REDIRECT_RESPONSE_URL = "http://localhost:8000/static/index3.html?#showForm"


spoty_auth_bot_router = APIRouter()


user_states = {}


@spoty_auth_bot_router.get("/login")
def login(chat_id: str):
    state = str(uuid.uuid4())
    user_states[state] = chat_id
    url = f"{AUTH_URL}&state={state}"
    return RedirectResponse(url=url)


@spoty_auth_bot_router.get("/callback")
def callback(code: str, state: str, request: Request, response: Response):
    if state not in user_states:
        raise HTTPException(status_code=400, detail="Invalid state")

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": REDIRECT_URL,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }

    token_response = requests.post(TOKEN_URL, data=payload)
    if token_response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error retrieving access token")

    token_data = token_response.json()
    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    # Store the tokens using the chat_id
    chat_id = user_states[state]
    store_tokens(chat_id, access_token, refresh_token)

    # Clean up the state
    del user_states[state]

    return RedirectResponse(url="http://localhost:8000/static/auth_success.html")


def store_tokens(chat_id: str, access_token: str, refresh_token: str):
    # Store the tokens securely in your database
    pass
