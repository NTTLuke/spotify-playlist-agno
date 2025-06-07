import httpx
from typing import Dict, Any
from ..core import get_logger
from ..core.config import Settings

logger = get_logger(__name__)


class SpotifyService:
    """Service for handling Spotify API operations."""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.token_url = "https://accounts.spotify.com/api/token"
        self.auth_base_url = "https://accounts.spotify.com/authorize"
    
    def get_auth_url(self) -> str:
        """Generate Spotify OAuth authorization URL."""
        params = {
            "response_type": "code",
            "client_id": self.settings.spotify_client_id,
            "scope": self.settings.spotify_scope,
            "redirect_uri": self.settings.spotify_redirect_uri
        }
        
        query_string = "&".join([f"{k}={v}" for k, v in params.items()])
        return f"{self.auth_base_url}?{query_string}"
    
    async def exchange_code_for_tokens(self, code: str) -> Dict[str, Any]:
        """Exchange authorization code for access and refresh tokens."""
        payload = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": self.settings.spotify_redirect_uri,
            "client_id": self.settings.spotify_client_id,
            "client_secret": self.settings.spotify_client_secret,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=payload)
            
        if response.status_code != 200:
            logger.error(f"Token exchange failed: {response.status_code} - {response.text}")
            raise Exception("Failed to exchange code for tokens")
        
        return response.json()
    
    async def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh access token using refresh token."""
        payload = {
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "client_id": self.settings.spotify_client_id,
            "client_secret": self.settings.spotify_client_secret,
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.token_url, data=payload)
            
        if response.status_code != 200:
            logger.error(f"Token refresh failed: {response.status_code} - {response.text}")
            raise Exception("Failed to refresh access token")
        
        return response.json()
    
    async def validate_token(self, access_token: str) -> bool:
        """Validate if access token is still valid."""
        headers = {"Authorization": f"Bearer {access_token}"}
        
        async with httpx.AsyncClient() as client:
            response = await client.get("https://api.spotify.com/v1/me", headers=headers)
            
        return response.status_code == 200