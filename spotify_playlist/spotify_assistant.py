from agno.agent import Agent
import os
from dotenv import load_dotenv
from agno.models.azure.openai_chat import AzureOpenAI
from agno.team.team import Team
from spotify_playlist.spotify_toolkit import SpotifyPlaylistTools
from agno.storage.agent.postgres import PostgresAgentStorage
from agno.tools.serperapi import SerperApiTools

load_dotenv()


class MusicAssistant:
    def __init__(self):

        self.llm = AzureOpenAI(
            id="gpt-4o", 
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"), 
            azure_deployment=os.getenv("AZURE_DEPLOYMENT_NAME"),
            temperature=0.3
        )

        if os.getenv("POSTGRES_URL") is None:
            raise ValueError(
                "Postgres URL is required to create the MusicAssistant with memory."
            )

        try:
            self.storage = PostgresAgentStorage(
                table_name="spotify_playlist_assistant",
                db_url=os.getenv("POSTGRES_URL"),
                auto_upgrade_schema=True,
                mode="team",
            )
        except Exception as e:
            raise ValueError(f"Error creating the storage: {e}")

        self.access_token = None

    def _get_expert_analyzing_text(self, session_id: str, user_id: str) -> Agent:
        return Agent(
            model=self.llm,
            session_id=session_id,
            user_id=user_id,
            name="Expert Text Analyzer",
            role="Expert Text Analyzer for music selection",
            add_history_to_messages=True,
            num_history_responses=3,
            description="""
            You are an expert in analyzing user input text to understand their emotional tone, intentions, or musical preferences.
            Your job is to infer mood and genre indications based on how the user describes what they want to listen to, how they feel, or what they're doing.
            """,
           instructions=[
                "Carefully read the user’s text and analyze emotional or situational context (e.g., 'feeling sad', 'need focus music').",
                "Return a short summary of the inferred mood and the music genre(s) that match it.",
                "Use decades of music experience to map nuanced emotions or scenarios to appropriate genres."
            ]
        )

    def _get_music_curator(self, session_id: str, user_id: str) -> Agent:
        return Agent(
            model=self.llm,
            session_id=session_id,
            user_id=user_id,
            add_history_to_messages=True,
            num_history_responses=3,
            name="Expert Music Curator",
            role="Expert Music Curator for music selection",
            description="""
            You are a music curator with deep knowledge of music trends and user tastes.
            Using the output from the Expert Text Analyzer or direct user instructions, your job is to identify and suggest 10 specific songs that best match the requested style or mood.
            """,
            instructions=[
                "Search for 10 SONGS ONLY based on the user's needs or the mood/genre provided by the text analyzer.",
                "Tailor your search queries using user mood, preferences, or trends they mention (e.g., 'summer 2020 pop').",
                "Find songs that fit, and ensure they are relevant and varied."
            ],
            tools=[SerperApiTools(api_key=os.getenv("SERPER_API_KEY"))],
        )

    def _get_spotify_api_expert(
        self, access_token: str, session_id: str, user_id: str
    ) -> Agent:

        if not access_token:
            raise ValueError(
                "Access token is required to create the Spotify API Expert."
            )

        if self.access_token is None:
            self.access_token = access_token

        return Agent(
            model=self.llm,
            session_id=session_id,
            user_id=user_id,
            name="Spotify API Expert Team",
            role="Spotify API Expert Team",
            add_history_to_messages=True,
            num_history_responses=3,
            description="""
            You are a specialist team responsible for executing actions on Spotify, such as searching songs, creating playlists, retrieving listening history, or playing music.
            """,
            instructions=[
            "Analyze the user's request and perform the appropriate action",
            "If the user asks to play music, remind them to open the Spotify app on an active device before starting playback."
            ],
            success_criteria="Spotify playlist has been created and the link with the songs has been sent to the user.",
            tools=[SpotifyPlaylistTools(access_token=self.access_token)],
            show_tool_calls=True,
        )

    def get_team(self, access_token: str, session_id: str, user_id: str) -> Team:

        if not access_token:
            raise ValueError(
                "Access token is required to create the SpotifyPlaylistTeam."
            )
        
        if not session_id:
            raise ValueError("Session ID is required to create the SpotifyPlaylistTeam.")

        if not user_id:
            raise ValueError("User ID is required to create the SpotifyPlaylistTeam.")

        return Team(
            model=self.llm,
            session_id=session_id,
            user_id=user_id,
            mode="collaborate",
            name="Spotify Music Assistant",
            storage=self.storage,
            description="""You are a team leader assistant responsible for helping users create personalized Spotify playlists based on Spotify user's preferences.
            To do this, use specialized agents of the team who analyze user text, curate songs, and perform Spotify API operations.
            Share found songs before creating the playlist.
            Follow the instruction and do not ask too much questions to the user.
            """,  
            instructions=[
                "Analyze the user request",
                "Search into latest Spotify user's preferences based on the genre",
                "Find online the songs that match the user's preferences based on the genre or mood requested by the user.",
                "Make sure each agent's output is correct before taking the next step.",
                "Inform the user about the playlist creation with the link to the playlist.",
                "If the user asks to play music, remind them to open the Spotify app on an active device before starting playback.",
            ],
            success_criteria="A playlist has been created and the user has been informed about it.",
            show_members_responses=True,
            members=[
                self._get_expert_analyzing_text(session_id=session_id, user_id=user_id),
                self._get_music_curator(session_id=session_id, user_id=user_id),
                self._get_spotify_api_expert(
                    access_token=access_token, session_id=session_id, user_id=user_id
                ),
            ],
            enable_agentic_context=True,
            enable_team_history=True,
            num_history_runs=3,
            show_tool_calls=True,
            debug_mode=True,
            add_datetime_to_instructions=True,
        )


if __name__ == "__main__":
    import uuid
    assistant = MusicAssistant()
    team = assistant.get_team(
        access_token=os.getenv("SPOTIFY_ACCESS_TOKEN"),
        session_id=str(uuid.uuid4()),
        user_id=str(uuid.uuid4()),
    )
    team.cli_app("Hello", stream=True)