# from phi.assistant import Assistant
# import os
# from dotenv import load_dotenv
# from phi.llm.openai.chat import OpenAIChat

# from spotify_playlist.tasks import SearchTools
# from spotify_playlist.spotify_toolkit import SpotifyPlaylistTools
# from phi.storage.assistant.postgres import PgAssistantStorage

# load_dotenv()


# class MusicAssistant:
#     def __init__(self, access_token: str):
#         if not access_token:
#             raise ValueError(
#                 "Access token is required to create the SpotifyPlaylistTeam."
#             )
#         self.access_token = access_token

#         if os.getenv("OPENAI_API_KEY") is None:
#             raise ValueError(
#                 "OpenAI API key is required to create the SpotifyPlaylistTeam."
#             )

#         self.llm = OpenAIChat(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

#         if os.getenv("POSTGRES_URL") is None:
#             raise ValueError(
#                 "Postgres URL is required to create the SpotifyPlaylistTeam with memory."
#             )

#         try:
#             self.storage = PgAssistantStorage(
#                 table_name="assistant_runs", db_url=os.getenv("POSTGRES_URL")
#             )
#         except Exception as e:
#             raise ValueError(f"Error creating the storage: {e}")

#     def _get_expert_analyzing_text(self, run_id: str, user_id: str) -> Assistant:
#         return Assistant(
#             run_id=run_id,
#             user_id=user_id,
#             name="Expert Text Analyzer",
#             storage=self.storage,
#             read_chat_history=True,
#             role="Expert Text Analyzer for music selection",
#             description=f"You are an expert in analyzing textual information to accurately select music."
#             "With decades of experience, You are specialized in interpreting a wide range of textual data to identify that best match genre from the provided context."
#             "You have decades of experience in understanding genre based text info.",
#             instructions=[
#                 "Analyze the text to understand the user's mood and music preferences.",
#                 "Use this information to identify the genre of music that would best suit the user's mood.",
#             ],
#         )

#     def _get_music_curator(self, run_id: str, user_id: str) -> Assistant:
#         return Assistant(
#             run_id=run_id,
#             user_id=user_id,
#             storage=self.storage,
#             read_chat_history=True,
#             name="Expert Music Curator",
#             role="Expert Music Curator for music selection",
#             description="You are an expert in searching music online based on the user's mood and preferences identified by the expert text analyzer.",
#             instructions=[
#                 "Search for 10 SONGS ONLY based on the user needs.Take care about music trends requested by the user.Provide a search query to find the songs on the internet specific for the user needs."
#             ],
#             tools=[SearchTools.search_internet],
#         )

#     def _get_spotify_api_expert(self, run_id: str, user_id: str) -> Assistant:
#         return Assistant(
#             run_id=run_id,
#             user_id=user_id,
#             name="Spotify API Expert",
#             storage=self.storage,
#             read_chat_history=True,
#             role="You are an expert in using the Spotify API based on tools associated and the requests from the user.",
#             description=f"""You are an expert in using the Spotify API to perform different operations based on the user requests and the tools associated with the assistant.
#             Be very careful with the user requests and the tools associated with the assistant.""",
#             # instructions=[
#             #     "You have to search for the user songs and get their Spotify Uris.",
#             #     "Using the uris, you have to create a playlist without asking to user the confirmation."
#             #     "If the user specifies the playlist name, use it, otherwise create a playlist with a default name."
#             #     "If the user specify to play the playlist, you have to start the playback.",
#             # ],
#             tools=[SpotifyPlaylistTools(access_token=self.access_token)],
#             show_tool_calls=True,
#         )

#     # def _get_spotify_api_expert(self) -> Assistant:
#     #     return Assistant(
#     #         name="Spotify API Expert",
#     #         role="Search URI songs using Spotify API and create a playlist",
#     #         description=f"You are an expert in using the Spotify API to search for URI songs from spotify and create a playlist.",
#     #         instructions=[
#     #             "You have to search for the user songs and get their Spotify Uris.",
#     #             "Using the uris, you have to create a playlist without asking to user the confirmation."
#     #             "If the user specifies the playlist name, use it, otherwise create a playlist with a default name."
#     #             "If the user specify to play the playlist, you have to start the playback.",
#     #         ],
#     #         tools=[SpotifyPlaylistTools(access_token=self.access_token)],
#     #         show_tool_calls=True,
#     #     )

#     def get_team(self) -> Assistant:
#         run_id = "spotify_playlist_team_1"
#         user_id = "luke"

#         return Assistant(
#             run_id=run_id,
#             user_id=user_id,
#             llm=self.llm,
#             name="Phidata Music Assistant",
#             description="""This team is the Music Assistant every user needs. You can do a lot of things with this team especially if you are a music lover.""",
#             output="The result of the action you have performed thanks to the specific assistant.",
#             storage=self.storage,
#             read_chat_history=True,
#             team=[
#                 self._get_expert_analyzing_text(run_id=run_id, user_id=user_id),
#                 self._get_music_curator(run_id=run_id, user_id=user_id),
#                 self._get_spotify_api_expert(run_id=run_id, user_id=user_id),
#             ],
#             debug_mode=True,
#         )

#     # # TODO: Maybe moving the team as generic spotify assistant instead of playlist
#     # def get_team(self) -> Assistant:
#     #     return Assistant(
#     #         llm=self.llm,
#     #         name="Phidata Spotify Team",
#     #         description="This team is responsible for creating a playlist based on the user's mood and preferences. Return the playlist link to the user with the songs that you have included into the playlist.",
#     #         team=[
#     #             self._get_expert_analyzing_text(),
#     #             self._get_music_curator(),
#     #             self._get_spotify_api_expert(),
#     #         ],
#     #         debug_mode=True,
#     #     )


# # spotify_team.print_response(
# #     f"I want to dance. I love 80s pop music, and I'm feeling a bit down today. So, I need a playlist that can cheer me up.",
# #     markdown=True,
# # )
