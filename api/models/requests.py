from pydantic import BaseModel, Field
from typing import Literal


AssistantType = Literal["SPOTIFY_PLAYLIST"]


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., description="User message to send to assistant")
    assistant: AssistantType = Field(default="SPOTIFY_PLAYLIST", description="Type of assistant to use")
    user_id: str = Field(default="user", description="Unique user identifier")
    session_id: str = Field(default="1", description="Conversation session identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Create a playlist with upbeat songs for working out",
                "assistant": "SPOTIFY_PLAYLIST",
                "user_id": "user123",
                "session_id": "conversation1"
            }
        }