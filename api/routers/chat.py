from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json

from ..core import get_logger
from ..models.requests import ChatRequest
from ..dependencies import get_spotify_token
from spotify_playlist.spotify_assistant import SpotifyMusicAssistant

from agno.run.team import TeamRunEvent

logger = get_logger(__name__)


def get_chat_router() -> APIRouter:
    chat_router = APIRouter()

    @chat_router.post("/")
    async def chat(
        body: ChatRequest, 
        access_token: str = Depends(get_spotify_token)
    ) -> StreamingResponse:
        """
        Send a message to the assistant and stream the response.
        Session state is managed by PostgreSQL via session_id.
        """
        logger.info(f"Chat request for session {body.session_id}: {body.message[:50]}...")

        try:
            # 1. Create a new assistant instance per request (stateless)
            assistant = SpotifyMusicAssistant()

            # 2. Get a team configured with the user's current token and session details
            # The session state is managed by PostgreSQL via the session_id
            team = assistant.get_team(
                access_token=access_token,
                session_id=body.session_id,
                user_id=body.user_id
            )

            # 3. Run the chat logic with the team
            async def event_stream():
                async for chunk in await team.arun(body.message, stream=True):
                    if chunk.event == TeamRunEvent.run_started.value:
                        yield f"data: {json.dumps({'message': 'Preparing playlist for you...'})}\n\n"
                    if chunk.event == TeamRunEvent.run_response_content.value:
                        yield f"data: {json.dumps({'message': chunk.content})}\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")

        except Exception as e:
            logger.error(f"Chat error for session {body.session_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Chat service unavailable")

    return chat_router