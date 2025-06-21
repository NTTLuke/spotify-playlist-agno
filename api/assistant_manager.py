from typing import Dict
from spotify_playlist.spotify_assistant import SpotifyMusicAssistant

class AssistantManager:
    """
    Manages the lifecycle of SpotifyMusicAssistant instances.
    This class acts as an in-memory cache to ensure that the same assistant
    instance (with its storage and context) is used for a given session.
    """
    def __init__(self):
        self._assistants: Dict[str, SpotifyMusicAssistant] = {}
        print("AssistantManager initialized.")

    def get_or_create_assistant(self, session_id: str) -> SpotifyMusicAssistant:
        """
        Retrieves a cached assistant instance for the given session_id,
        or creates a new one if it doesn't exist.
        """
        if session_id not in self._assistants:
            print(f"Creating new assistant for session_id: {session_id}")
            self._assistants[session_id] = SpotifyMusicAssistant()
        else:
            print(f"Reusing existing assistant for session_id: {session_id}")
        return self._assistants[session_id]

# Create a single, global instance of the AssistantManager.
# This instance will be shared across all requests in the application.
assistant_manager = AssistantManager() 