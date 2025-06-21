from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

from . import get_logger
from .exceptions import SpotifyAPIException, AuthenticationException, AssistantException
from ..models.responses import ErrorResponse

logger = get_logger(__name__)

async def spotify_exception_handler(request: Request, exc: SpotifyAPIException):
    logger.error(f"Spotify API error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="Spotify API Error", detail=exc.detail).model_dump()
    )

async def auth_exception_handler(request: Request, exc: AuthenticationException):
    logger.error(f"Authentication error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="Authentication Error", detail=exc.detail).model_dump()
    )

async def assistant_exception_handler(request: Request, exc: AssistantException):
    logger.error(f"Assistant error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="Assistant Error", detail=exc.detail).model_dump()
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(error="HTTP Error", detail=exc.detail).model_dump()
    )

async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(error="Internal Server Error", detail="An unexpected error occurred").model_dump()
    )

def register_exception_handlers(app: FastAPI):
    app.add_exception_handler(SpotifyAPIException, spotify_exception_handler)
    app.add_exception_handler(AuthenticationException, auth_exception_handler)
    app.add_exception_handler(AssistantException, assistant_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler) 