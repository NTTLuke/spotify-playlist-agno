from phi.assistant import Assistant
import os
from dotenv import load_dotenv
from phi.llm.openai.chat import OpenAIChat

from spotify_playlist.tasks import SearchTools
from spotify_playlist.spotify_toolkit import SpotifyPlaylistTools
from phi.storage.assistant.postgres import PgAssistantStorage

load_dotenv()


class MusicAssistant:
    def __init__(self):

        if os.getenv("OPENAI_API_KEY") is None:
            raise ValueError("OpenAI API key is required to create the MusicAssistant.")

        self.llm = OpenAIChat(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

        if os.getenv("POSTGRES_URL") is None:
            raise ValueError(
                "Postgres URL is required to create the MusicAssistant with memory."
            )

        try:
            self.storage = PgAssistantStorage(
                table_name="assistant_runs", db_url=os.getenv("POSTGRES_URL")
            )
        except Exception as e:
            raise ValueError(f"Error creating the storage: {e}")

        self.access_token = None

    def _get_expert_analyzing_text(self, run_id: str, user_id: str) -> Assistant:
        return Assistant(
            run_id=run_id,
            user_id=user_id,
            name="Expert Text Analyzer",
            storage=self.storage,
            read_chat_history=True,
            role="Expert Text Analyzer for music selection",
            description=f"You are an expert in analyzing textual information to accurately select music."
            "With decades of experience, You are specialized in interpreting a wide range of textual data to identify that best match genre from the provided context."
            "You have decades of experience in understanding genre based text info.",
            instructions=[
                "Analyze the text to understand the user's mood and music preferences.",
                "Use this information to identify the genre of music that would best suit the user's mood.",
            ],
        )

    def _get_music_curator(self, run_id: str, user_id: str) -> Assistant:
        return Assistant(
            run_id=run_id,
            user_id=user_id,
            storage=self.storage,
            add_chat_history_to_prompt=True,
            num_history_messages=3,
            name="Expert Music Curator",
            role="Expert Music Curator for music selection",
            description="You are an expert in searching music online based on the user's mood and preferences identified by the expert text analyzer.",
            instructions=[
                "Search for 10 SONGS ONLY based on the user needs.Take care about music trends requested by the user.Provide a search query to find the songs on the internet specific for the user needs."
            ],
            tools=[SearchTools.search_internet],
        )

    def _get_spotify_api_expert(
        self, access_token: str, run_id: str, user_id: str
    ) -> Assistant:

        if not access_token:
            raise ValueError(
                "Access token is required to create the Spotify API Expert."
            )

        if self.access_token is None:
            self.access_token = access_token

        return Assistant(
            run_id=run_id,
            user_id=user_id,
            name="Spotify API Expert",
            storage=self.storage,
            add_chat_history_to_prompt=True,
            num_history_messages=3,
            role="You are an expert in using the Spotify API based on tools associated and the requests from the user.",
            description="You are an expert in using the Spotify API to perform different operations based on the user requests and the tools associated with the assistant."
            "Be very careful with the user requests and the tools associated with the assistant. Always response to the user with relevant information about the action performed.",
            instructions=[
                "Use the Spotify API to perform different operations based on the user requests and the tools associated with the assistant.",
                "if the user asks for play a playlist, remember the user to open the Spotify app before proceeding with the action.",
            ],
            tools=[SpotifyPlaylistTools(access_token=self.access_token)],
            show_tool_calls=True,
        )

    def get_team(self, access_token: str, run_id: str, user_id: str) -> Assistant:

        if not access_token:
            raise ValueError(
                "Access token is required to create the SpotifyPlaylistTeam."
            )

        if not run_id:
            raise ValueError("Run ID is required to create the SpotifyPlaylistTeam.")

        if not user_id:
            raise ValueError("User ID is required to create the SpotifyPlaylistTeam.")

        return Assistant(
            run_id=run_id,
            user_id=user_id,
            llm=self.llm,
            name="Phidata Music Assistant",
            storage=self.storage,
            add_chat_history_to_prompt=True,
            num_history_messages=3,
            description="""This team is the Music Assistant every user needs. You can do a lot of things with this team especially if you are a music lover.
            Always check your historical chat messages to get missing information before making any conclusions.""",
            output="The result of the action you have performed thanks to the specific assistant.",
            instructions=[
                "ALWAYS check your historical chat messages to get a hint before asking for help.",
                "If you think some information is missing or you need more context, ask the user for more information.",
            ],
            team=[
                self._get_expert_analyzing_text(run_id=run_id, user_id=user_id),
                self._get_music_curator(run_id=run_id, user_id=user_id),
                self._get_spotify_api_expert(
                    access_token=access_token, run_id=run_id, user_id=user_id
                ),
            ],
            debug_mode=True,
        )
