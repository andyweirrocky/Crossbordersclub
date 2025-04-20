import streamlit as st
from agents.reddit_scout.agent import agent
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
                response = agent.chat(prompt)
                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error("Sorry, there was an error processing your request. Please try again.")
                st.session_state.messages.append({"role": "assistant", "content": "Error: Please try again."}) 