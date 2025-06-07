from fastapi import HTTPException
from typing import Optional


class SpotifyAPIException(HTTPException):
    """Exception for Spotify API related errors."""
    
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)


class AuthenticationException(HTTPException):
    """Exception for authentication related errors."""
    
    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(status_code=401, detail=detail)


class AssistantException(HTTPException):
    """Exception for assistant related errors."""
    
    def __init__(self, detail: str, status_code: int = 500):
        super().__init__(status_code=status_code, detail=detail)