from typing import AsyncGenerator
from ..core import get_logger
from spotify_playlist.spotify_assistant import MusicAssistant

logger = get_logger(__name__)


class AssistantService:
    """Service for handling AI assistant operations."""
    
    def __init__(self):
        self._music_assistant = None
    
    @property
    def music_assistant(self) -> MusicAssistant:
        """Lazy initialization of music assistant."""
        if self._music_assistant is None:
            self._music_assistant = MusicAssistant()
        return self._music_assistant
    
    async def chat_stream(
        self,
        message: str,
        access_token: str,
        user_id: str,
        session_id: str
    ) -> AsyncGenerator[str, None]:
        """Stream chat responses from the music assistant."""
        try:
            music_assistant_team = self.music_assistant.get_team(
                access_token=access_token,
                session_id=session_id,
                user_id=user_id
            )
            
            run_response = music_assistant_team.run(message, stream=True)
            for chunk in run_response:
                # Log chunk details for debugging
                logger.debug(f"Chunk event: {getattr(chunk, 'event', 'no event')}, type: {type(chunk).__name__}")
                
                # Create a structured response based on event type
                chunk_data = {
                    "type": "unknown",
                    "content": ""
                }
                
                # Get the event type
                event = getattr(chunk, 'event', None)
                
                # Handle different event types
                if event == "RunStarted":
                    chunk_data["type"] = "run_started"
                    chunk_data["content"] = "Starting to process your request..."
                elif event == "RunResponse":
                    chunk_data["type"] = "message"
                    chunk_data["content"] = getattr(chunk, 'content', '')
                elif event == "RunCompleted":
                    chunk_data["type"] = "run_completed"
                    chunk_data["content"] = getattr(chunk, 'content', '')
                elif event == "RunError":
                    chunk_data["type"] = "error"
                    chunk_data["content"] = f"Error: {getattr(chunk, 'content', 'Unknown error')}"
                elif event == "ToolCallStarted":
                    chunk_data["type"] = "tool_call_started"
                    tool_name = chunk.tools[0].tool_name
                    chunk_data["content"] = f"Using {tool_name}..."
                elif event == "ToolCallCompleted":
                    chunk_data["type"] = "tool_call_completed"
                    chunk_data["content"] = "Tool call completed"
                else:
                    # Fallback - try to get content
                    if hasattr(chunk, 'content'):
                        chunk_data["type"] = "message"
                        chunk_data["content"] = chunk.content
                
                # Only yield if there's content
                if chunk_data["content"]:
                    import json
                    yield f"data: {json.dumps(chunk_data)}\n\n"
                
        except Exception as e:
            logger.error(f"Assistant stream error: {str(e)}")
            yield f"data: Error: {str(e)}\n\n"