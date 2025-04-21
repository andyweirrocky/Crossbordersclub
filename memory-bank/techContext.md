# Technical Context

## Technologies Used
1. **Core Framework**:
   - Google Agent Development Kit (ADK) >= 0.2.0
   - Python 3.x

2. **Web Interface**:
   - Streamlit 1.31.1
   - streamlit-chat 0.1.1

3. **API Integration**:
   - PRAW 7.7.1 (Python Reddit API Wrapper)

4. **Configuration**:
   - python-dotenv 1.0.0

## Development Setup
1. **Environment**:
   - Virtual environment (.venv)
   - Environment variables via .env
   - Git version control

2. **Dependencies**:
   ```python
   google-adk>=0.2.0
   praw==7.7.1
   python-dotenv==1.0.0
   streamlit==1.31.1
   streamlit-chat==0.1.1
   ```

3. **Required API Keys**:
   - Google AI API Key
   - Reddit API credentials (Client ID, Client Secret)

## Technical Constraints
1. **API Limitations**:
   - Reddit API rate limits
   - Google AI API quotas
   - Cache size limitations

2. **Performance Considerations**:
   - Response time optimization
   - Cache efficiency
   - Memory usage

3. **Security Requirements**:
   - API key protection
   - Environment variable management
   - Secure deployment practices

## Development Workflow
1. **Local Development**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # or .\.venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Testing**:
   - Run test_agents.py for comparison
   - Individual agent testing
   - Performance monitoring

3. **Deployment**:
   - Streamlit Cloud deployment
   - Environment variable configuration
   - Continuous integration setup

## Directory Structure
```
adk-made-simple/
├── agents/
│   ├── reddit_scout/
│   └── reddit_scout_mcp/
├── .venv/
├── .env.example
├── requirements.txt
├── app.py
└── test_agents.py
```

## Known Technical Challenges
1. API rate limiting
2. Cache invalidation
3. Performance optimization
4. Cross-platform compatibility
5. Deployment configuration 