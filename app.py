import streamlit as st
from agents.reddit_scout.agent import agent  # Import the agent instead of the function
import os
from dotenv import load_dotenv

# Set page config (MUST be the first Streamlit command)
st.set_page_config(
    page_title="Your AI Visa Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Debug information
st.sidebar.markdown("### Debug Information")
st.sidebar.write("Environment Variables Status:")
for var in ['REDDIT_CLIENT_ID', 'REDDIT_CLIENT_SECRET', 'REDDIT_USER_AGENT', 'GOOGLE_API_KEY']:
    exists = var in os.environ
    st.sidebar.write(f"- {var}: {'✅ Set' if exists else '❌ Missing'}")

# Check for required environment variables
required_vars = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USER_AGENT',
    'GOOGLE_API_KEY'
]

missing_vars = [var for var in required_vars if not os.getenv(var)]

# Custom CSS for better styling
st.markdown("""
    <style>
    .main {
        padding: 2rem;
    }
    .stChatInput {
        position: fixed;
        bottom: 0;
        width: 100%;
        background-color: white;
        padding: 1rem;
        z-index: 100;
    }
    .stChatMessage {
        margin-bottom: 1rem;
    }
    .error-box {
        padding: 1rem;
        background-color: #ffebee;
        border-radius: 4px;
        margin: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.title("About")
    st.markdown("""
    This AI agent helps you find information about visas, passports, and citizenship opportunities from Reddit.
    Powered by Google's Gemini and ADK (Agent Development Kit).
    
    ### How to use:
    1. Ask questions about:
       - Specific countries
       - Visa types
       - Immigration processes
       - Citizenship options
    2. The AI agent will search relevant Reddit discussions
    3. Get real-time information and insights from the community
    
    ### Example questions:
    - "What are the best visa options for digital nomads?"
    - "Tell me about golden visa programs in Europe"
    - "What's the process for getting a Schengen visa?"
    """)

# Main content
st.title("Your AI Visa Agent")
st.markdown("""
Ask questions about visas, passports, or immigration topics. The AI agent will search Reddit for relevant discussions and provide you with up-to-date information and insights from the community.
""")

# Check for missing environment variables
if missing_vars:
    st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    st.markdown("""
    ### ⚠️ Configuration Required
    The application needs API keys to function. Please make sure all required environment variables are set:
    
    1. Go to your app settings
    2. Find the "Secrets" section
    3. Add the following variables:
       - `REDDIT_CLIENT_ID` (from Reddit API)
       - `REDDIT_CLIENT_SECRET` (from Reddit API)
       - `REDDIT_USER_AGENT` (from Reddit API)
       - `GOOGLE_API_KEY` (from Google AI Studio)
    """)
else:
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Chat input
    if prompt := st.chat_input("Ask about visas, passports, or immigration..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Get agent response
        with st.chat_message("assistant"):
            with st.spinner("AI agent searching and analyzing Reddit discussions..."):
                try:
                    # Use the ADK agent to get a response
                    response = agent.chat(prompt)
                    
                    # Add the response to chat history
                    st.markdown(response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                except Exception as e:
                    error_message = f"An error occurred: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"⚠️ {error_message}"
                    }) 