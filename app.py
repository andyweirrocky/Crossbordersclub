import streamlit as st
from agents import agent
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

# Check for required environment variables without displaying them
required_vars = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USER_AGENT',
    'GOOGLE_API_KEY'
]

missing_vars = [var for var in required_vars if not os.getenv(var)]

# Debug information (only showing status, not actual values)
st.sidebar.markdown("### System Status")
if missing_vars:
    st.sidebar.error("⚠️ Some required configurations are missing")
else:
    st.sidebar.success("✅ All systems operational")

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

# Sidebar content
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
    st.error("Configuration error. Please contact the administrator.")
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
                    response = agent.generate(prompt)
                    
                    # Add the response to chat history
                    st.markdown(response)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response
                    })
                except Exception as e:
                    error_message = "An error occurred while processing your request. Please try again."
                    if os.getenv('DEBUG'):  # Only show detailed error in debug mode
                        error_message += f"\nError details: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": f"⚠️ {error_message}"
                    }) 