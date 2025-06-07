# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered Spotify playlist assistant that uses the Agno framework to orchestrate multiple AI agents. The system creates personalized playlists based on natural language descriptions of mood and preferences.

## Common Development Commands

### Starting the Application

```bash
# 1. Start PostgreSQL database (required for agent memory)
docker-compose up -d

# 2. Run the FastAPI web application
uvicorn spoty_playlist_api.main:app --reload

# 3. (Optional) Run the Telegram bot interface
python telegram-bot/music_lover_bot.py
```

### Environment Setup

Create a `.env` file with:
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint
- `AZURE_OPENAI_DEPLOYMENT_NAME` - GPT-4 deployment name
- `SERPER_API_KEY` - For web search functionality
- `SPOTIFY_CLIENT_ID` - Spotify OAuth client ID
- `SPOTIFY_CLIENT_SECRET` - Spotify OAuth client secret
- `SPOTIFY_REDIRECT_URI` - OAuth redirect URI (typically http://localhost:8000/callback)
- `TELEGRAM_BOT_TOKEN` - For Telegram bot (optional)
- `DB_URL` - PostgreSQL connection URL (default: postgresql://ailuke:mypassword123456@localhost:5432/aimemory)

## High-Level Architecture

### Core Components

1. **Multi-Agent System** (`spotify_playlist/spotify_assistant.py`):
   - Expert Text Analyzer: Analyzes user input for mood/preferences
   - Expert Music Curator: Searches for songs based on analysis
   - Spotify API Expert: Handles all Spotify operations
   - Uses Azure OpenAI GPT-4 with Agno framework

2. **Spotify Toolkit** (`spotify_playlist/spotify_toolkit.py`):
   - Custom tools for Spotify API operations
   - Requires `SPOTIFY_ACCESS_TOKEN` in session
   - Functions: search_song, create_playlist, add_song_to_playlist, play_song, get_user_top_genres, etc.

3. **Web API** (`spoty_playlist_api/`):
   - FastAPI application with streaming chat endpoint
   - OAuth2 authentication flow for Spotify
   - Separate auth flows for web and Telegram bot users
   - Stores conversation history in PostgreSQL

4. **Frontend** (`static/index3.html`):
   - Material Design-inspired UI
   - Real-time streaming responses with markdown rendering
   - Quick suggestion buttons for common requests

### Key Architectural Decisions

- **Agent Memory**: PostgreSQL stores conversation history, enabling context-aware responses
- **Streaming Responses**: Uses Server-Sent Events for real-time AI responses
- **Multi-Interface**: Same backend serves both web and Telegram interfaces
- **OAuth Flow**: Separate endpoints for web (`/login`) and bot (`/bot-login`) authentication

## Development Notes

- The project uses `uv` as the package manager (see `uv.lock`)
- No test suite or linting configuration currently exists
- Modified files in git suggest active migration from "phidata" to "agno" framework
- The `tasks.py` file contains commented-out legacy code that might be useful for reference