import os
from typing import Dict, List, TypedDict
from datetime import datetime

from google.adk.generative import Agent
import praw
from praw.exceptions import PRAWException

class RedditPost(TypedDict):
    title: str
    url: str
    score: int
    num_comments: int
    created_utc: float
    flair: str
    selftext: str
    subreddit: str

# List of relevant subreddits for immigration, visas, and citizenship
RELEVANT_SUBREDDITS = [
    "immigration",          # General immigration discussions
    "USCIS",               # US immigration
    "visas",               # General visa discussions
    "IWantOut",            # Immigration and relocation
    "PassportPorn",        # Passport discussions
    "expats",              # Expat community
    "Schengen",            # Schengen visa discussions
    "ukvisa",              # UK visa discussions
    "GermanCitizenship",   # German citizenship
    "dualcitizenship",     # Dual citizenship discussions
    "goldenvisa",          # Investment/Golden visa programs
    "digitalnomad",        # Digital nomad visas
    "eupersonalfinance",   # EU immigration/financial aspects
    "iwantoutjobs"         # Jobs for immigration
]

def get_reddit_posts(query: str = "", subreddit: str = "all", limit: int = 15) -> Dict[str, List[RedditPost]]:
    """
    Fetches visa, passport, and citizenship-related posts from relevant subreddits.
    This is a tool function that will be used by the ADK agent.
    """
    try:
        client_id = os.environ.get("REDDIT_CLIENT_ID")
        client_secret = os.environ.get("REDDIT_CLIENT_SECRET")
        user_agent = os.environ.get("REDDIT_USER_AGENT")

        if not all([client_id, client_secret, user_agent]):
            missing_creds = []
            if not client_id:
                missing_creds.append("REDDIT_CLIENT_ID")
            if not client_secret:
                missing_creds.append("REDDIT_CLIENT_SECRET")
            if not user_agent:
                missing_creds.append("REDDIT_USER_AGENT")
            raise ValueError(f"Missing Reddit API credentials: {', '.join(missing_creds)}")

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        # Test the Reddit connection
        try:
            reddit.user.me()
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Reddit API: {str(e)}")

        # Remove 'r/' prefix if present in the subreddit name
        subreddit = subreddit.replace('r/', '')

        results = {}
        subreddits_to_search = [subreddit] if subreddit != "all" and subreddit in RELEVANT_SUBREDDITS else RELEVANT_SUBREDDITS

        for sub_name in subreddits_to_search:
            try:
                sub = reddit.subreddit(sub_name)
                posts = list(sub.search(query, limit=limit)) if query else list(sub.hot(limit=limit))
                
                if posts:
                    post_info = []
                    for post in posts:
                        post_date = datetime.fromtimestamp(post.created_utc).strftime('%Y-%m-%d')
                        post_info.append({
                            "title": post.title,
                            "url": f"https://reddit.com{post.permalink}",
                            "score": post.score,
                            "num_comments": post.num_comments,
                            "created_utc": post_date,
                            "flair": post.link_flair_text or "",
                            "selftext": post.selftext[:500] + "..." if len(post.selftext) > 500 else post.selftext,
                            "subreddit": sub_name
                        })
                    if post_info:  # Only add subreddits that have matching posts
                        results[sub_name] = post_info
            except Exception as e:
                print(f"Warning: Error fetching from r/{sub_name}: {e}")
                continue

        return results if results else {"info": [{"title": "No relevant posts found", "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": ""}]}

    except Exception as e:
        raise Exception(f"Error fetching Reddit posts: {str(e)}")

# Define the Agent with proper ADK setup
agent = Agent(
    name="visa_immigration_expert",
    description="An AI agent specialized in visa and immigration information, powered by Reddit community insights",
    llm_model="gemini-1.5-pro",  # Using the Pro model for better chat capabilities
    tools=[get_reddit_posts],
    instructions="""You are an AI Visa and Immigration Expert who helps people find information about visas, passports, and immigration opportunities. You have access to Reddit's community knowledge through the get_reddit_posts tool.

When users ask questions:
1. Analyze their query to understand:
   - Specific countries mentioned
   - Type of visa/immigration information needed
   - Any specific requirements or constraints

2. Use the get_reddit_posts tool to search relevant subreddits:
   - For specific country queries, focus on relevant country-specific subreddits
   - For general queries, search across all immigration subreddits
   - Use appropriate search terms extracted from the user's question

3. Analyze and summarize the Reddit posts:
   - Focus on recent, highly upvoted, and well-commented posts
   - Extract key information and insights
   - Note any common patterns or advice
   - Highlight official processes and requirements mentioned

4. Format your response professionally:
   - Start with a brief summary of findings
   - Group information by themes or countries
   - Include relevant post links for further reading
   - Add disclaimers about verifying information officially

5. Be helpful but responsible:
   - Clarify that Reddit information is community-sourced
   - Recommend official sources when appropriate
   - Ask follow-up questions if the query is too broad
   - Acknowledge when information might be outdated

Remember:
- Always maintain a professional and helpful tone
- Focus on factual information from the Reddit community
- Provide balanced perspectives when available
- Encourage users to verify information through official channels
"""
)