# Spotify Playlist Assistant with Agno

An AI-powered Spotify playlist assistant that uses the Agno framework to orchestrate multiple AI agents. The system creates personalized playlists based on natural language descriptions of mood and preferences.

## 🎵 Features

- **Natural Language Playlist Creation**: Describe your mood, genre preferences, or situation to create custom playlists
- **Multi-Agent AI System**: Uses specialized AI agents for text analysis, music curation, and Spotify operations
- **Web Interface**: Clean, Material Design-inspired UI with real-time streaming responses
- **Conversation Memory**: PostgreSQL-backed memory for context-aware conversations
- **OAuth Integration**: Secure Spotify authentication flow

## 🏗️ Architecture

### Core Components

1. **Multi-Agent System** (`spotify_playlist/spotify_assistant.py`):
   - **Expert Text Analyzer**: Analyzes user input for mood/preferences
   - **Expert Music Curator**: Searches for songs based on analysis
   - **Spotify API Expert**: Handles all Spotify operations
   - Uses Azure OpenAI GPT-4 with Agno framework

2. **Spotify Toolkit** (`spotify_playlist/spotify_toolkit.py`):
   - Custom tools for Spotify API operations
   - Functions: search_song, create_playlist, add_song_to_playlist, play_song, get_user_top_genres

3. **Web API** (`api/`):
   - FastAPI application with streaming chat endpoint
   - OAuth2 authentication flow for Spotify
   - Server-Sent Events for real-time AI responses

4. **Frontend** (`static/index3.html`):
   - Material Design-inspired UI
   - Real-time streaming responses with markdown rendering
   - Quick suggestion buttons for common requests

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose (required for both deployment methods)
- Spotify Developer Account
- Azure OpenAI Account
- Serper API Key (for web search)
- Python 3.12+ (only for local development)

### 1. Clone the Repository

```bash
git clone https://github.com/NTTLuke/spotify-playlist-agno.git
cd spotify-playlist-agno
```

### 2. Environment Setup

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API keys and configuration:
   ```bash
   nano .env  # or your preferred editor
   ```

   **Required Environment Variables:**
   ```env
   # Azure OpenAI (Required)
   AZURE_OPENAI_API_KEY=your_azure_openai_api_key
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_DEPLOYMENT_NAME=your_deployment

   # Spotify OAuth (Required)
   SPOTIFY_CLIENT_ID=your_spotify_client_id
   SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
   SPOTIFY_REDIRECT_URI=http://localhost:8000/callback

   # Serper API for web search (Required)
   SERPER_API_KEY=your_serper_api_key
   ```

### 3. Choose Your Deployment Method

## 🐳 Docker Deployment (Recommended)

The easiest way to run the application is using Docker Compose, which handles both the database and the FastAPI application.

### Start the Application

```bash
# Start both database and FastAPI application
docker-compose up -d
```

This command will:
- Build the FastAPI application container
- Start the PostgreSQL database
- Configure networking between services
- Set up all environment variables automatically

### Managing the Application

```bash
# View application logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f app
docker-compose logs -f db

# Rebuild application after code changes
docker-compose up --build -d app

# Stop all services
docker-compose down

# Stop and remove all data (including database)
docker-compose down -v
```

### Access the Application
- **Web Interface**: http://localhost:8000/
- **API Documentation**: http://localhost:8000/docs

---

## 🔧 Local Development (Alternative)

If you prefer to run the FastAPI application locally while using Docker only for the database:

### Install Dependencies

Using `uv` (recommended):
```bash
pip install uv
uv sync
```

Or using `pip`:
```bash
pip install -r requirements.txt
```

### Start the Database Only

```bash
docker-compose up -d db
```

### Run the Application Locally

```bash
uvicorn api.main:app --reload
```

### Access the Application
- **Web Interface**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 🔧 Configuration

### Spotify Developer Setup

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Create a new app
3. Add redirect URI: `http://localhost:8000/callback`
4. Copy the Client ID and Client Secret to your `.env` file


### Azure OpenAI Setup (default)

1. Create an Azure OpenAI resource
2. Deploy an OpenAI model
3. Copy the API key, endpoint, and deployment name to your `.env` file

### OpenAI Setup

1. Go to [OpenAI Platform](https://platform.openai.com)
2. Create an API key
3. Copy the API key to your `.env` file


### Serper API Setup

1. Go to [Serper.dev](https://serper.dev)
2. Sign up and get your API key
3. Add it to your `.env` file

## 🔒 Security

- The `.env` file is in `.gitignore` and should never be committed
- All sensitive configuration uses environment variables
- Default database credentials are for development only - change them in production
- The secret key should be changed in production environments

## 📝 Usage

### Web Interface

1. Open http://localhost:8000
2. Click "Login with Spotify" to authenticate
3. Start chatting with the AI assistant
4. Use natural language to describe the playlist you want:
   - "Create a playlist for a rainy Sunday morning"
   - "I need energetic workout music"
   - "Make me a chill playlist for studying"
5. Alternatively, you can use the suggested buttons on top
   
### API Endpoints

- `GET /` - Web interface
- `GET /login` - Spotify OAuth login
- `GET /callback` - OAuth callback
- `POST /chat/` - Chat with the assistant (requires authentication)
- `GET /auth/status` - Check authentication status

## 🛠️ Development

### Project Structure

```
├── api/                    # FastAPI application
│   ├── core/              # Core configuration and logging
│   ├── routers/           # API route handlers
│   └── models/            # Request/response models
├── spotify_playlist/       # AI assistant and Spotify toolkit
├── static/                # Frontend assets
└── docker-compose.yaml    # PostgreSQL database setup
```

### Key Files

- `spotify_playlist/spotify_assistant.py` - Main AI assistant with multi-agent system
- `spotify_playlist/spotify_toolkit.py` - Spotify API operations
- `api/routers/chat.py` - Chat endpoint with streaming responses
- `api/core/config.py` - Application configuration
- `static/index3.html` - Web interface

### Running Tests

Currently, there are no automated tests configured. This would be a good area for contribution.

### Linting and Formatting

No linting configuration is currently set up. Consider adding tools like `ruff` or `black` for code formatting.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Ensure no sensitive information is committed
5. Submit a pull request

## 📄 License

[Add your license information here]

## 🆘 Troubleshooting

### Common Issues

1. **Database Connection Error**:
   - Ensure Docker is running: `docker-compose up -d`
   - Check database credentials in `.env`

2. **Spotify Authentication Failed**:
   - Verify your Spotify Client ID and Secret
   - Ensure redirect URI matches exactly: `http://localhost:8000/callback`

3. **Azure OpenAI API Error**:
   - Check your API key and endpoint
   - Verify your deployment name
   - Ensure you have sufficient quota

4. **Import Errors**:
   - Make sure all dependencies are installed: `uv sync`
   - Check Python version (requires 3.12+)

### Logs

The application logs to the console. Set `LOG_LEVEL=DEBUG` in your `.env` file for detailed logging.

## 🔗 Links

- [Agno Framework Documentation](https://docs.agno.ai)
- [Spotify Web API Documentation](https://developer.spotify.com/documentation/web-api)
- [Azure OpenAI Documentation](https://docs.microsoft.com/en-us/azure/cognitive-services/openai/)
- [FastAPI Documentation](https://fastapi.tiangolo.com)