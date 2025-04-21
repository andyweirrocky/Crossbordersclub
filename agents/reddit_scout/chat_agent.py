from typing import Dict, List
from .agent import get_reddit_posts
import google.generativeai as genai
import os
import re

class ChatAgent:
    def __init__(self):
        # Initialize Gemini
        genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
        
        # Initialize the model with the correct version
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Define greeting patterns
        self.greeting_patterns = [
            r'^hi$', r'^hello$', r'^hey$', r'^hi there$', r'^hello there$',
            r'^greetings$', r'^good morning$', r'^good afternoon$', r'^good evening$'
        ]
        
        # Store the instruction for reference
        self.instruction = """You are an AI agent that helps users find relevant information about visas, passports, and immigration from Reddit discussions. Your goal is to provide helpful, accurate information while being clear about the community-sourced nature of the data.

When analyzing Reddit posts:

1. UNDERSTAND THE QUERY
- Identify specific topics (visa types, countries, requirements)
- Note any time-sensitive aspects
- Look for specific vs. general information needs

2. ANALYZE AND SUMMARIZE
- Focus on recent, highly-upvoted posts
- Identify common patterns and advice
- Note official processes mentioned
- Highlight relevant experiences

3. STRUCTURE YOUR RESPONSE
- Start with a clear summary
- Group information by topic/country
- Include relevant post links
- Add appropriate disclaimers

4. BE RESPONSIBLE
- Clearly state that information is community-sourced
- Recommend verifying through official channels
- Note when information might be outdated
- Ask for clarification when needed

Remember:
- Maintain a professional, helpful tone
- Focus on factual information
- Provide balanced perspectives
- Always encourage official verification
"""

    def is_greeting(self, message: str) -> bool:
        """Check if the message is a simple greeting."""
        message = message.lower().strip()
        return any(re.match(pattern, message) for pattern in self.greeting_patterns)

    def get_greeting_response(self) -> str:
        """Return a friendly greeting response with instructions."""
        return """Hello! 👋 I'm your AI Visa Agent, here to help you find information about visas, passports, and immigration topics.

You can ask me questions like:
• "What are the requirements for a digital nomad visa in Portugal?"
• "How to apply for a Schengen visa?"
• "Tell me about golden visa programs in Europe"
• "What's the process for getting a student visa in Canada?"

What would you like to know about?"""
    
    def generate_response(self, message: str) -> str:
        try:
            # Check if it's a simple greeting
            if self.is_greeting(message):
                return self.get_greeting_response()
            
            # For actual queries, get relevant Reddit posts
            posts = get_reddit_posts(query=message)
            
            # Format the posts for the agent
            formatted_posts = []
            for subreddit, post_list in posts.items():
                for post in post_list:
                    formatted_posts.append(
                        f"[r/{post['subreddit']}] {post['title']}\n"
                        f"Score: {post['score']} | Comments: {post['num_comments']} | Date: {post['created_utc']}\n"
                        f"URL: {post['url']}\n"
                        f"Content: {post['selftext']}\n"
                    )
            
            # Create context for the agent
            context = f"""Instructions: {self.instruction}

Based on the user's question: "{message}", here are relevant Reddit posts:

{chr(10).join(formatted_posts)}

Please analyze these posts and provide a helpful response following the instructions."""
            
            # Generate response using the model
            response = self.model.generate_content(context)
            
            if response.text:
                return response.text
            else:
                return "I apologize, but I couldn't generate a response. Please try rephrasing your question."
        
        except Exception as e:
            return f"I encountered an error while processing your request: {str(e)}"

# Create a singleton instance
chat_agent = ChatAgent() 