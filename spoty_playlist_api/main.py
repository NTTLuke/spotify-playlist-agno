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
from .music_lover_assistant import music_lover_assistant_router
from .spoty_auth import spotify_oauth_router
from .spoty_auth_bot import spoty_auth_bot_router


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

app.include_router(music_lover_assistant_router)
app.include_router(spotify_oauth_router)
app.include_router(spoty_auth_bot_router, prefix="/bot-login")
