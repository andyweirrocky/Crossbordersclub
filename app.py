import streamlit as st
from agents.reddit_scout.agent import get_passport_visa_info
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
    page_title="Your AI Visa Agent",
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
st.title("Your AI Visa Agent")
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
                    # Call the function directly
                    response = get_passport_visa_info(query=prompt)
                    
                    # Format the response
                    formatted_response = "Here's what I found:\n\n"
                    for subreddit, posts in response.items():
                        if subreddit != "error":
                            formatted_response += f"### From r/{subreddit}\n\n"
                            for post in posts:
                                formatted_response += f"**{post['title']}**\n"
                                formatted_response += f"- Score: {post['score']} | Comments: {post['num_comments']} | Date: {post['created_utc']}\n"
                                if post['flair']:
                                    formatted_response += f"- Flair: {post['flair']}\n"
                                if post['selftext']:
                                    formatted_response += f"- Summary: {post['selftext'][:200]}...\n"
                                formatted_response += f"- [Read more]({post['url']})\n\n"
                    
                    st.markdown(formatted_response)
                    st.session_state.messages.append({"role": "assistant", "content": formatted_response})
                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_message} Please try again or contact support if the issue persists."}) 