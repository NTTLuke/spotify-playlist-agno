from fastapi import FastAPI, Request, HTTPException, Response, Header
from fastapi.responses import RedirectResponse
import requests
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from spoty_playlist_api.log import logger
from phi.assistant import Assistant
from fastapi.responses import StreamingResponse
from typing import Literal
from pydantic import BaseModel
from spotify_playlist.spotify_assistant import MusicAssistant

AssistantType = Literal["SPOTIFY_PLAYLIST"]

load_dotenv()

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the static directory to serve static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Spotify API credentials
CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SCOPES = "playlist-modify-private playlist-modify-public user-modify-playback-state user-read-playback-state playlist-read-private"

# Spotify API auth URL
REDIRECT_URI = "http://localhost:8000/callback"
AUTH_URL = f"https://accounts.spotify.com/authorize?response_type=code&client_id={CLIENT_ID}&scope={SCOPES}&redirect_uri={REDIRECT_URI}"

# Spotify API token URL
TOKEN_URL = "https://accounts.spotify.com/api/token"

# Redirect URL after login
REDIRECT_RESPONSE_URL = "http://localhost:8000/static/index3.html?#showForm"


@app.get("/login")
def read_root():
    return RedirectResponse(url=AUTH_URL)


@app.get("/callback")
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


music_assistant = MusicAssistant()


class ChatRequest(BaseModel):
    message: str
    assistant: AssistantType = "SPOTIFY_PLAYLIST"
    user_id: str = "theluke"
    run_id: str = "1"


def chat_response_streamer(spotify_access_token: str, chat_request: ChatRequest):

    user_id = chat_request.user_id
    run_id = chat_request.run_id

    music_assistant_team = music_assistant.get_team(
        access_token=spotify_access_token, run_id=run_id, user_id=user_id
    )

    for chunk in music_assistant_team.run(chat_request.message):
        yield chunk


@app.post("/chat")
async def chat(body: ChatRequest, x_spotify_refresh_token: str = Header(None)):
    """Sends a message to an Assistant and returns the response"""
    logger.debug(f"ChatRequest: {body}")

    return StreamingResponse(
        chat_response_streamer(
            spotify_access_token=x_spotify_refresh_token, chat_request=body
        ),
        media_type="text/event-stream",
    )
