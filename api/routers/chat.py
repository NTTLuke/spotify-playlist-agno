from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json

from ..core import get_logger
from ..models.requests import ChatRequest
from ..dependencies import get_spotify_token
from ..assistant_manager import assistant_manager

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
        This endpoint now manages state by using the AssistantManager.
        """
        logger.info(f"Chat request for session {body.session_id}: {body.message[:50]}...")

        try:
            # 1. Get the stateful assistant instance for this session
            assistant = assistant_manager.get_or_create_assistant(body.session_id)

            # 2. Get a team configured with the user's current token and session details
            team = assistant.get_team(
                access_token=access_token,
                session_id=body.session_id,
                user_id=body.user_id
            )

            # 3. Run the chat logic with the stateful and correctly configured team
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