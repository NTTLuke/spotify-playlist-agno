from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

from api.core import setup_logging, get_settings, get_logger
from api.core.middleware import LoggingMiddleware
from api.core.exceptions import SpotifyAPIException, AuthenticationException, AssistantException
from api.models.responses import ErrorResponse
from api.routers.auth import auth_router
from api.routers.chat import get_chat_router
from agno.app.fastapi.app import FastAPIApp
from spotify_playlist.spotify_assistant import SpotifyMusicAssistant

import os
import uuid


load_dotenv()
settings = get_settings()
setup_logging(settings.log_level)
logger = get_logger(__name__)


music_assistant = SpotifyMusicAssistant()
music_assistant_team = music_assistant.get_team(
    access_token=os.getenv("SPOTIFY_ACCESS_TOKEN"),
    session_id=str(uuid.uuid4()),
    user_id=str(uuid.uuid4())
)

fastapi_app = FastAPIApp(
    teams=[music_assistant_team],
    name="Spotify Music Assistant",
    app_id="spotify_music_assistant",
    description="A Spotify music assistant that can answer questions and help with tasks.",
)

app = fastapi_app.get_app()

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(LoggingMiddleware)

# Exception handlers
@app.exception_handler(SpotifyAPIException)
async def spotify_exception_handler(request: Request, exc: SpotifyAPIException):
    logger.error(f"Spotify API error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="Spotify API Error", detail=exc.detail).model_dump()
    )


@app.exception_handler(AuthenticationException)
async def auth_exception_handler(request: Request, exc: AuthenticationException):
    logger.error(f"Authentication error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="Authentication Error", detail=exc.detail).model_dump()
    )


@app.exception_handler(AssistantException)
async def assistant_exception_handler(request: Request, exc: AssistantException):
    logger.error(f"Assistant error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="Assistant Error", detail=exc.detail).model_dump()
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="HTTP Error", detail=exc.detail).model_dump()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(error="Internal Server Error", detail="An unexpected error occurred").model_dump()
    )

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(auth_router, prefix="/auth", tags=["authentication"])

chat_router = get_chat_router(team=music_assistant_team)
app.include_router(chat_router, prefix="/chat", tags=["chat"])

# Add callback route at root level to match Spotify redirect URI
from api.routers.auth import callback as auth_callback
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
