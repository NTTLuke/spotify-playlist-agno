from fastapi import Header
from spoty_playlist_api.log import logger
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from spotify_playlist.spotify_assistant import MusicAssistant
from typing import Literal
from fastapi import APIRouter


music_lover_assistant_router = APIRouter()


music_assistant = MusicAssistant()
AssistantType = Literal["SPOTIFY_PLAYLIST"]


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


@music_lover_assistant_router.post("/chat")
async def chat(body: ChatRequest, x_spotify_access_token: str = Header(None)):
    """Sends a message to an Assistant and returns the response"""
    logger.debug(f"ChatRequest: {body}")

    return StreamingResponse(
        chat_response_streamer(
            spotify_access_token=x_spotify_access_token, chat_request=body
        ),
        media_type="text/event-stream",
    )
