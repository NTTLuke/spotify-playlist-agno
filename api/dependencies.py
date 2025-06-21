import os
import uuid

from fastapi import Depends, HTTPException, Request
from agno.team.team import Team
from spotify_playlist.spotify_assistant import SpotifyMusicAssistant

def get_spotify_token(request: Request) -> str:
    """
    A dependency to extract the Spotify access token from the request cookie.
    Raises a 401 Unauthorized error if the token is not found.
    """
    token = request.cookies.get("accessToken")
    if not token:
        raise HTTPException(status_code=401, detail="Spotify access token cookie not found")
    return token

def get_request_specific_team(token: str = Depends(get_spotify_token)) -> Team:
    """
    Dependency that creates a request-specific music assistant team,
    configured with the user's actual access token.
    """
    music_assistant = SpotifyMusicAssistant()
    # Now we use the real token from the user's request
    music_assistant_team = music_assistant.get_team(
        access_token=token,
        session_id=str(uuid.uuid4()), # This could also come from the request if needed
        user_id=str(uuid.uuid4())      # This could also come from the request if needed
    )
    return music_assistant_team 