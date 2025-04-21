# ADK Made Simple - Agent Examples

This project demonstrates agents built using the Google Agent Development Kit (ADK).
Currently, it contains two agents: "Reddit Scout" and "Reddit Scout MCP".

## Agents

- **Reddit Scout**: Simulates fetching recent discussion titles from game development subreddits.
- **Reddit Scout MCP**: Enhanced version with Model Content Protocol (MCP) for better content management and caching.

## General Setup

1.  **Clone the repository:**

    ```bash
    git clone <your-repo-url>
    cd adk-made-simple
    ```

2.  **Create and activate a virtual environment (Recommended):**

    ```bash
    python -m venv .venv
    # On Windows
    .\.venv\Scripts\activate
    # On macOS/Linux
    source .venv/bin/activate
    ```

3.  **Install general dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Agent-Specific Setup:** Navigate to the specific agent's directory within `agents/` and follow the instructions in its `README.md` (or follow the steps below for the default agent).

## Reddit Scout - Setup & Running

1.  **Navigate to Agent Directory:**

    ```bash
    cd agents/reddit_scout
    ```

2.  **Set up API Key:**

    - Copy the example environment file:
      ```bash
      cp ../.env.example .env
      ```
    - Edit the `.env` file and add your Google AI API Key. You can obtain one from [Google AI Studio](https://aistudio.google.com/app/apikey).
      ```dotenv
      GOOGLE_API_KEY=YOUR_API_KEY_HERE
      ```
    - _Note:_ You might need to load this into your environment depending on your OS and shell (`source .env` or similar) if `python-dotenv` doesn't automatically pick it up when running `adk`.

3.  **Run the Agent:**

    - Make sure your virtual environment (from the root directory) is activated.
    - From the `agents/reddit_scout` directory, run the agent using the ADK CLI, specifying the core code package:
      ```bash
      adk run reddit_scout
      ```
    - Alternatively, from the project root (`adk-made-simple`), you might be able to run:
      ```bash
      adk run agents.reddit_scout
      ```
      _(Check ADK documentation for preferred discovery method)_

## Reddit Scout MCP - Setup & Running

1.  **Navigate to Agent Directory:**

    ```bash
    cd agents/reddit_scout_mcp
    ```

2.  **Set up API Key and Cache Configuration:**

    - Copy the example environment file:
      ```bash
      cp ../.env.example .env
      ```
    - Edit the `.env` file and add your Google AI API Key and MCP configuration:
      ```dotenv
      GOOGLE_API_KEY=YOUR_API_KEY_HERE
      MCP_CACHE_DIR=.mcp_cache
      MCP_TTL=3600
      MCP_MAX_SIZE_MB=100
      MCP_COMPRESSION=true
      ```
      
      Configuration options:
      - `MCP_CACHE_DIR`: Directory to store cache files (default: `.mcp_cache`)
      - `MCP_TTL`: Time-to-live for cache entries in seconds (default: 3600)
      - `MCP_MAX_SIZE_MB`: Maximum cache size in megabytes (default: 100)
      - `MCP_COMPRESSION`: Enable/disable cache compression (default: true)

3.  **Run the Agent:**

    - Make sure your virtual environment (from the root directory) is activated.
    - From the `agents/reddit_scout_mcp` directory, run the agent using the ADK CLI:
      ```bash
      adk run reddit_scout_mcp
      ```
    - Alternatively, from the project root:
      ```bash
      adk run agents.reddit_scout_mcp
      ```

## MCP Features

The MCP (Model Content Protocol) version includes several enhancements:

1. **Configurable Caching**:
   - Customizable cache directory
   - Adjustable cache expiration time
   - Configurable maximum cache size
   - Optional compression for cache files

2. **Cache Management**:
   - Automatic cleanup of expired cache entries
   - Size-based cache eviction (removes oldest entries when limit is reached)
   - Cache statistics tracking (hits, misses, errors)

3. **Performance Monitoring**:
   - Detailed logging of cache operations
   - Cache hit/miss statistics
   - Cache size tracking
   - Error tracking and reporting

4. **Error Handling**:
   - Robust error handling for cache operations
   - Graceful fallback when cache operations fail
   - Detailed error logging

## Testing Both Agents

To compare the performance of both agents:

```bash
python test_agents.py
```

This will:
1. Run the original agent
2. Run the MCP agent (first run)
3. Run the MCP agent (cached run)
4. Compare performance and results

## Project Structure Overview

```
adk-made-simple/
├── agents/
│   ├── reddit_scout/        # Original Reddit Scout Agent
│   │   ├── __init__.py
│   │   └── agent.py
│   └── reddit_scout_mcp/    # MCP-enhanced Reddit Scout Agent
│       ├── __init__.py
│       └── agent.py
├── .venv/                   # Virtual environment directory
├── .env.example             # Environment variables example
├── .gitignore               # Root gitignore file
├── requirements.txt         # Project dependencies
├── README.md                # This file (Overall Project README)
├── test_agents.py           # Agent comparison test script
└── PLAN.md                  # Development plan notes
```

# AI Visa Agent

An AI-powered assistant that helps users find information about visas, passports, and immigration by analyzing Reddit discussions and providing up-to-date insights from the community.

## Features

- Real-time Reddit post analysis
- Smart conversation handling
- Comprehensive immigration information
- User-friendly chat interface
- Automatic source citation

## Setup

1. Clone the repository:
```bash
git clone <your-repo-url>
cd adk-made-simple
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with the following:
```env
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_client_secret
REDDIT_USER_AGENT=your_reddit_user_agent
GOOGLE_API_KEY=your_google_api_key
```

4. Run the app:
```bash
streamlit run app.py
```

## Deployment on Streamlit Cloud

1. Fork this repository to your GitHub account
2. Visit [share.streamlit.io](https://share.streamlit.io)
3. Sign in with GitHub
4. Deploy your app by selecting the repository
5. Add your environment variables in the Streamlit Cloud settings

## Environment Variables

- `REDDIT_CLIENT_ID`: Your Reddit API client ID
- `REDDIT_CLIENT_SECRET`: Your Reddit API client secret
- `REDDIT_USER_AGENT`: Your Reddit API user agent
- `GOOGLE_API_KEY`: Your Google API key for Gemini

## Getting API Keys

### Reddit API
1. Visit [Reddit's App Preferences](https://www.reddit.com/prefs/apps)
2. Click "Create App" or "Create Another App"
3. Fill in the details:
   - Name: AI Visa Agent
   - App type: Script
   - Description: AI assistant for visa information
   - Redirect URI: http://localhost:8501
4. Get your client ID and secret

### Google API
1. Visit [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project
3. Enable the Gemini API
4. Create API credentials
5. Copy your API key

## Usage

After deployment, users can:
1. Visit your Streamlit app URL
2. Start chatting with the AI agent
3. Ask questions about visas, passports, and immigration
4. Get real-time information from Reddit discussions

## Security Notes

- Never commit your `.env` file
- Keep your API keys secure
- Use environment variables in Streamlit Cloud
- Enable all security features in config.toml

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to use and modify for your own projects!
