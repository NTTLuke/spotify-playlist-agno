# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Starting the Application
```bash
# Start PostgreSQL database
docker-compose up -d

# Install dependencies (preferred method)
uv sync

# Alternative dependency installation
pip install -r requirements.txt

# Start the FastAPI server
uvicorn api.main:app --reload

# Access the application
# Web interface: http://localhost:8000/static/index3.html
# API docs: http://localhost:8000/docs
```

### Environment Setup
The application requires a `.env` file with the following variables:
- `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT`, `AZURE_DEPLOYMENT_NAME` - Azure OpenAI configuration
- `SPOTIFY_CLIENT_ID`, `SPOTIFY_CLIENT_SECRET` - Spotify OAuth credentials
- `SERPER_API_KEY` - Web search functionality
- `POSTGRES_URL` - Database connection (defaults to `postgresql://ailuke:mypassword123456@localhost:5432/aimemory`)

## Architecture Overview

### Multi-Agent AI System
The core of the application is a multi-agent system built with the Agno framework:

- **SpotifyMusicAssistant** (`spotify_playlist/spotify_assistant.py`): Main orchestrator that creates specialized AI agents
- **Three Expert Agents**:
  - Expert Text Analyzer: Analyzes user input for mood and preferences
  - Expert Music Curator: Searches for songs based on analysis
  - Spotify API Expert: Handles playlist creation and Spotify operations

### Key Components

**FastAPI Application Structure**:
- `api/main.py`: Application entry point using Agno's FastAPIApp
- `api/routers/chat.py`: Streaming chat endpoint with Server-Sent Events
- `api/routers/auth.py`: Spotify OAuth2 authentication flow
- `api/core/config.py`: Centralized configuration management

**Spotify Integration**:
- `spotify_playlist/spotify_toolkit.py`: Custom Agno toolkit with Spotify API functions
- Functions include: `search_songs_uris`, `create_playlist_by_uris`, `get_user_top_genres`, etc.

**Data Persistence**:
- PostgreSQL database for conversation memory (managed by Agno framework)
- Agent storage table: `spotify_playlist_assistant`
- Database runs in Docker container with default dev credentials

### Request Flow
1. User authenticates via Spotify OAuth (`/auth/login`)
2. Frontend sends chat request to `/chat/` with session_id and user_id
3. Chat router creates new `SpotifyMusicAssistant` instance per request
4. Assistant creates a team of specialized agents with user's access token
5. Team processes request using multi-agent collaboration
6. Response streams back via Server-Sent Events

### Session Management
- Stateless request handling with PostgreSQL-backed session persistence
- Each request creates fresh assistant instance but retrieves conversation history via session_id
- Access tokens are managed per request, not persisted in application state

## Important Implementation Details

### Template Team Pattern
The main application creates a "template team" with dummy credentials for FastAPIApp initialization. This template is NOT used for actual request processing - each request creates its own properly authenticated team.

### Environment Variables in Config
The `Settings` class in `api/core/config.py` handles all environment variable loading with sensible defaults for development.

### Database Schema Auto-Upgrade
The PostgresAgentStorage is configured with `auto_upgrade_schema=True` to handle database migrations automatically.