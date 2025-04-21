import streamlit as st
from agents import chat_agent
import os
from dotenv import load_dotenv
import time
import re

# Set page config (MUST be the first Streamlit command)
st.set_page_config(
    page_title="CrossBordersClub - Your AI Visa Agent",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load environment variables
load_dotenv()

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processing" not in st.session_state:
    st.session_state.processing = False

# Check for required environment variables
required_vars = [
    'REDDIT_CLIENT_ID',
    'REDDIT_CLIENT_SECRET',
    'REDDIT_USER_AGENT',
    'GOOGLE_API_KEY'
]

missing_vars = [var for var in required_vars if not os.getenv(var)]

def format_reddit_links(text):
    """Convert Reddit URLs and structured link data to formatted markdown"""
    def format_structured_link(summary, search_query, link_text="Search Reddit"):
        # Create a clean URL-friendly version of the search query
        url_query = search_query.replace(' ', '%20')
        return f"""
**{summary}**
- Search: `{search_query}`
- {link_text}: [Reddit Search](https://www.reddit.com/search/?q={url_query})
"""
    
    # First try to parse structured link data
    try:
        import json
        data = json.loads(text)
        if isinstance(data, dict) and "summary" in data and "search_query" in data:
            return format_structured_link(
                data["summary"],
                data["search_query"],
                data.get("link_text", "Search Reddit")
            )
    except (json.JSONDecodeError, TypeError):
        pass
    
    # If not structured data, handle regular Reddit URLs
    def clean_title(title):
        return title.replace('_', ' ').rstrip('/')
    
    # First, clean up any incorrectly nested markdown links
    # Remove any nested markdown patterns
    text = re.sub(r'\[(?:\[([^\]]+)\]\([^)]+\))\](?:\([^)]+\))', r'[\1]', text)
    
    # Handle full Reddit URLs - only if they're not already part of a markdown link
    text = re.sub(
        r'(?<!\]\()https?://(?:www\.)?reddit\.com/r/(\w+)/comments/([^/]+)/([^/\s]+)/?(?!\))',
        lambda m: f'[{clean_title(m.group(3))}](https://reddit.com/r/{m.group(1)}/comments/{m.group(2)}/{m.group(3)})',
        text
    )
    
    # Handle r/subreddit mentions - only if they're not already part of a markdown link
    text = re.sub(
        r'(?<!\]\()(?<!/)(?<!\w)r/(\w+)(?!\w)(?!\))',
        r'[r/\1](https://reddit.com/r/\1)',
        text
    )
    
    # Clean up any double-wrapped links that might have been created
    text = re.sub(r'\[(\[.*?\]\(.*?\))\]\(.*?\)', r'\1', text)
    
    return text

def handle_example_question(question: str):
    """Handle when an example question is clicked"""
    st.session_state.processing = True
    st.session_state.messages.append({"role": "user", "content": question})

# Sidebar content
with st.sidebar:
    st.markdown('''
        <div style="display: flex; align-items: center; gap: 0.75rem; padding: 1rem;">
            <span style="font-size: 24px;">🌐</span>
            <h1 style="margin: 0; font-size: 1.5rem;">CrossBordersClub</h1>
        </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="padding: 1.5rem; background: #f8f9fa; border-radius: 12px; margin: 1.5rem 0; border: 1px solid #e9ecef;">
        <h4 style="margin-top: 0;">Welcome! 👋</h4>
        <p>I'm <strong>Rooban</strong>. Holding a passport that requires extra planning hasn't stopped me from doing my fair share of traveling! I've learned a lot navigating the world of visas and paperwork.</p>
        <p>I'm building CrossBordersClub – a larger community and resource hub to make this easier for everyone.</p>
        <p>For now, think of this chat as your AI companion. It uses insights gathered from real traveler experiences on communities like Reddit to help answer your questions on visas, passports, and immigration. Enjoy the assist! 🌍</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.subheader("💡 Popular Questions")
    
    # Example Questions
    example_questions = [
        "What are the requirements for a US tourist visa?",
        "How to apply for Schengen visa?",
        "Digital nomad visa options",
        "Canada Express Entry points calculator",
        "Portugal D7 visa requirements",
        "UK skilled worker visa process",
        "Australian PR pathways",
        "Dubai golden visa eligibility",
        "Estonia e-Residency benefits",
        "Singapore work visa types"
    ]
    
    for question in example_questions:
        if st.button(question, key=f"btn_{question}", disabled=st.session_state.processing):
            handle_example_question(question)
            st.rerun()
    
    # Disclaimer
    st.markdown("""
    <div style="font-size: 0.9rem; color: #666; padding: 1.25rem; background-color: #fff8e1; border-radius: 12px; margin: 1.5rem 0; border-left: 4px solid #ffc107;">
        ⚠️ <strong>Important Note:</strong> Information provided is gathered from Reddit discussions and online sources. 
        While we strive for accuracy, always verify with official government sources or consult with immigration professionals.
    </div>
    """, unsafe_allow_html=True)

# Main content
st.markdown("""
    <div style="background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%); color: white; padding: 3rem 2rem; border-radius: 24px; margin: -2rem -1rem 2rem -1rem; position: relative; overflow: hidden; box-shadow: 0 10px 30px rgba(33,150,243,0.2);">
        <div style="position: absolute; top: 0; right: 0; width: 300px; height: 300px; background: linear-gradient(45deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%); border-radius: 50%; transform: translate(100px, -100px);"></div>
        <div style="position: relative; z-index: 1;">
            <h1 style="font-size: 3.5rem; font-weight: 800; margin-bottom: 1.5rem; line-height: 1.2; color: white; text-shadow: 0 2px 4px rgba(0,0,0,0.1); background: linear-gradient(120deg, #ffffff 0%, #e3f2fd 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Your AI Visa & Immigration Assistant</h1>
            <p style="font-size: 1.35rem; opacity: 0.95; max-width: 700px; line-height: 1.6; margin-bottom: 2rem; text-shadow: 0 1px 2px rgba(0,0,0,0.1);">Navigate the complexities of global mobility with AI-powered insights from real community experiences. Get accurate, up-to-date information about visas, immigration, and citizenship opportunities.</p>
            <div style="display: inline-block; padding: 0.75rem 1.5rem; background: rgba(255,255,255,0.1); border-radius: 12px; backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2);">
                <span style="font-size: 1.1rem; font-weight: 500;">🔍 Ask me anything about visas and immigration</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Chat container
chat_container = st.container()

# Add bottom padding to prevent overlap with input
st.markdown("<div style='height: 120px'></div>", unsafe_allow_html=True)

# Check for missing environment variables
if missing_vars:
    st.error("⚠️ Configuration error. Please contact the administrator.")
else:
    # Display chat messages
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                # Format Reddit links in the message
                formatted_content = format_reddit_links(message["content"])
                st.markdown(formatted_content)
        
        # Show loading message if processing
        if st.session_state.processing:
            with st.chat_message("assistant"):
                st.markdown('<div style="animation: pulse 1.5s infinite; padding: 1.5rem; border-radius: 16px; background: #f5f9ff; text-align: center; margin: 1rem 0; border: 1px solid #e3f2fd;">🔍 Searching and analyzing Reddit discussions...</div>', unsafe_allow_html=True)
                try:
                    # Generate response
                    response = chat_agent.generate_response(st.session_state.messages[-1]["content"])
                    # Format Reddit links in response
                    formatted_response = format_reddit_links(response)
                    # Add response to messages
                    st.session_state.messages.append({"role": "assistant", "content": formatted_response})
                    # Reset processing flag
                    st.session_state.processing = False
                    st.rerun()
                except Exception as e:
                    error_message = "An error occurred while processing your request. Please try again."
                    if os.getenv('DEBUG'):
                        error_message += f"\nError details: {str(e)}"
                    st.session_state.messages.append({"role": "assistant", "content": f"⚠️ {error_message}"})
                    st.session_state.processing = False
                    st.rerun()

    # Chat input
    if prompt := st.chat_input("Ask about visas, passports, or immigration...", disabled=st.session_state.processing):
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.processing = True
        st.rerun() 