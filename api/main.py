import os
import uuid
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from api.core import setup_logging, get_settings, get_logger
from api.core.middleware import LoggingMiddleware
from api.core.exception_handlers import register_exception_handlers
from api.models.responses import ErrorResponse
from api.routers.auth import auth_router
from api.routers.chat import get_chat_router
from agno.app.fastapi.app import FastAPIApp
from api.routers.auth import callback as auth_callback
from spotify_playlist.spotify_assistant import SpotifyMusicAssistant


# Load environment variables
load_dotenv()

# Get settings
settings = get_settings()

# Setup logging
setup_logging(settings.log_level)

# Get logger
logger = get_logger(__name__)

# Create a "template" team for platform registration.
# This team is initialized with a dummy token and is NOT used for request processing.
# Its purpose is to satisfy the FastAPIApp constructor requirement.
template_music_assistant = SpotifyMusicAssistant()
template_team = template_music_assistant.get_team(
    access_token="dummy-token-for-startup",
    session_id="template-session",
    user_id="template-user"
)

# Create FastAPIApp
fastapi_app = FastAPIApp(
    teams=[template_team],
    name="Spotify Music Assistant",
    app_id="spotify_music_assistant",
    description="A Spotify music assistant that can help user to create playlists based on user's requests.",
)

# Get the FastAPI app from the FastAPIApp
app = fastapi_app.get_app()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register exception handlers
app.add_middleware(LoggingMiddleware)

# Register exception handlers
register_exception_handlers(app)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Register routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])

# Register chat router
chat_router = get_chat_router()
app.include_router(chat_router, prefix="/chat", tags=["chat"])

# Add callback route at root level to match Spotify redirect URI
app.add_api_route("/callback", auth_callback, methods=["GET"])


@app.get("/")
async def root():
    """Serve the main page."""
    from fastapi.responses import FileResponse
    return FileResponse("static/index3.html")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.app_version}


if __name__ == "__main__":
    fastapi_app.serve(app="main:app", port=8000, reload=True)
