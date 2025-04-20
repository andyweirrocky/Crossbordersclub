import streamlit as st
from agents.reddit_scout.agent import agent
import os
from dotenv import load_dotenv
import google.cloud.aiplatform as aiplatform
from vertexai.language_models import TextGenerationModel

# Load environment variables
load_dotenv()

# Initialize Google AI Platform
try:
    aiplatform.init(
        project=os.getenv("GOOGLE_CLOUD_PROJECT", "default-project"),
        location=os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )
except Exception as e:
    print(f"Error initializing AI Platform: {e}")

# Check for required environment variables
required_vars = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USER_AGENT',
    'GOOGLE_API_KEY'
]

missing_vars = [var for var in required_vars if not os.getenv(var)]

# Set page config
st.set_page_config(
    page_title="Reddit Scout Agent",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
    This agent helps you find information about visas, passports, and citizenship opportunities from Reddit.
    
    ### How to use:
    1. Ask questions about:
       - Specific countries
       - Visa types
       - Immigration processes
       - Citizenship options
    2. The agent will search relevant Reddit discussions
    3. Get real-time information from the community
    
    ### Example questions:
    - "What are the best visa options for digital nomads?"
    - "Tell me about golden visa programs in Europe"
    - "What's the process for getting a Schengen visa?"
    """)

# Main content
st.title("🔍 Reddit Scout Agent")
st.markdown("""
Ask questions about visas, passports, or immigration topics. The agent will search Reddit for relevant discussions and provide you with up-to-date information from the community.
""")

# Check for missing environment variables
if missing_vars:
    st.error(f"Missing required environment variables: {', '.join(missing_vars)}")
    st.markdown("""
    ### ⚠️ Configuration Required
    The application needs API keys to function. Please make sure all required environment variables are set in Streamlit Cloud:
    
    1. Go to your app settings
    2. Find the "Secrets" section
    3. Add the following variables:
       - `REDDIT_CLIENT_ID`
       - `REDDIT_CLIENT_SECRET`
       - `REDDIT_USER_AGENT`
       - `GOOGLE_API_KEY`
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
            with st.spinner("Searching Reddit for relevant information..."):
                try:
                    # Create the agent's input
                    agent_input = {
                        "messages": [
                            {"role": "user", "content": prompt}
                        ]
                    }
                    
                    # Get the response from the agent
                    response = agent.invoke(agent_input)
                    
                    # Extract the response content
                    if isinstance(response, dict) and "content" in response:
                        content = response["content"]
                    else:
                        content = str(response)
                    
                    st.markdown(content)
                    st.session_state.messages.append({"role": "assistant", "content": content})
                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_message} Please try again or contact support if the issue persists."}) 