from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from agno.team.team import Team
import json

from ..core import get_logger
from ..models.requests import ChatRequest

logger = get_logger(__name__)


def get_chat_router(team: Team) -> APIRouter:
    chat_router = APIRouter()

    @chat_router.post("/")
    async def chat(body: ChatRequest) -> StreamingResponse:
        """Send a message to the assistant and stream the response."""
        logger.info(f"Chat request from user {body.user_id}: {body.message[:50]}...")

        try:
            # Use the team object passed into the factory function
            # Assuming team.run() is an async generator that yields the response
            async def event_stream():
                async for chunk in await team.arun(body.message, stream=True):
                    # Assuming the chunk is a string or bytes, wrap it for SSE
                    yield f"data: {json.dumps({'message': chunk.content})}\n\n"

            return StreamingResponse(event_stream(), media_type="text/event-stream")

        except Exception as e:
            logger.error(f"Chat error: {str(e)}")
            raise HTTPException(status_code=500, detail="Chat service unavailable")

    return chat_router