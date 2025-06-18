from fastapi import APIRouter, Request, HTTPException, Response, Depends
from fastapi.responses import RedirectResponse
from ..core import get_settings, get_logger
from ..services.spotify import SpotifyService

logger = get_logger(__name__)
auth_router = APIRouter()


@auth_router.get("/login")
async def login(settings = Depends(get_settings)):
    """Initiate Spotify OAuth flow."""
    spotify_service = SpotifyService(settings)
    auth_url = spotify_service.get_auth_url()
    logger.info("Initiating Spotify OAuth flow")
    return RedirectResponse(url=auth_url)


@auth_router.get("/callback")
async def callback(
    code: str, 
    response: Response,
    settings = Depends(get_settings)
) -> RedirectResponse:
    """Handle OAuth callback and exchange code for tokens."""
    try:
        spotify_service = SpotifyService(settings)
        token_data = await spotify_service.exchange_code_for_tokens(code)
        
        response = RedirectResponse(url="/static/auth_success.html")
        
        # Set secure cookie with access token
        response.set_cookie(
            key="accessToken",
            value=token_data["access_token"],
            path="/",
            domain="localhost",
            httponly=False,  # Frontend needs access for now
            secure=False,    # Set to True in production with HTTPS
            samesite="lax",
            max_age=token_data.get("expires_in", 3600)
        )
        
        # Store refresh token securely (httponly)
        response.set_cookie(
            key="refreshToken",
            value=token_data["refresh_token"],
            path="/",
            domain="localhost", 
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=60 * 60 * 24 * 30  # 30 days
        )
        
        logger.info("OAuth callback successful")
        return response
        
    except Exception as e:
        logger.error(f"OAuth callback error: {str(e)}")
        raise HTTPException(status_code=400, detail="Authentication failed")


@auth_router.post("/refresh")
async def refresh_token(
    request: Request,
    settings = Depends(get_settings)
):
    """Refresh access token using refresh token."""
    refresh_token = request.cookies.get("refreshToken")
    if not refresh_token:
        raise HTTPException(status_code=401, detail="No refresh token found")
    
    try:
        spotify_service = SpotifyService(settings)
        token_data = await spotify_service.refresh_access_token(refresh_token)
        
        return {
            "access_token": token_data["access_token"],
            "expires_in": token_data.get("expires_in", 3600)
        }
    except Exception as e:
        logger.error(f"Token refresh error: {str(e)}")
        raise HTTPException(status_code=401, detail="Token refresh failed")


@auth_router.post("/logout")
async def logout(response: Response):
    """Logout user by clearing tokens."""
    response.delete_cookie(key="accessToken", path="/", domain="localhost")
    response.delete_cookie(key="refreshToken", path="/", domain="localhost")
    logger.info("User logged out")
    return {"message": "Logged out successfully"}


@auth_router.get("/status")
async def status(request: Request, settings = Depends(get_settings)):
    """Check authentication status and return user profile."""
    access_token = request.cookies.get("accessToken")
    if not access_token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        spotify_service = SpotifyService(settings)
        user_profile = await spotify_service.get_user_profile(access_token)
        return user_profile
    except Exception as e:
        logger.error(f"Error fetching user profile: {str(e)}")
        raise HTTPException(status_code=401, detail="Invalid or expired token")