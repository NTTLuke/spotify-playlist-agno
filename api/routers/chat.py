from fastapi import APIRouter, Header, HTTPException
from fastapi.responses import StreamingResponse
from ..core import get_logger
from ..models.requests import ChatRequest
from ..services.assistant import AssistantService

logger = get_logger(__name__)
chat_router = APIRouter()

assistant_service = AssistantService()

@chat_router.post("/")
async def chat(
    body: ChatRequest,
    x_spotify_access_token: str = Header(None, alias="X-SPOTIFY-ACCESS-TOKEN")
) -> StreamingResponse:
    """Send a message to the assistant and stream the response."""
    
    if not x_spotify_access_token:
        raise HTTPException(status_code=401, detail="Spotify access token required")
    
    logger.info(f"Chat request from user {body.user_id}: {body.message[:50]}...")
    
    try:
        response_stream = assistant_service.chat_stream(
            message=body.message,
            access_token=x_spotify_access_token,
            user_id=body.user_id,
            session_id=body.session_id
        )
        
        return StreamingResponse(
            response_stream,
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            }
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail="Chat service unavailable")