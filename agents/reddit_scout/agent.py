import random
import os
from typing import Dict, List, TypedDict
from datetime import datetime

from google.adk.agents import Agent
import praw
from praw.exceptions import PRAWException

from dotenv import load_dotenv
print("--- Attempting to load .env file ---")
load_dotenv()
print(f"--- Current working directory: {os.getcwd()} ---")
print("--- Checking for environment variables ---")
print(f"CLIENT_ID exists: {'REDDIT_CLIENT_ID' in os.environ}")
print(f"CLIENT_SECRET exists: {'REDDIT_CLIENT_SECRET' in os.environ}")
print(f"USER_AGENT exists: {'REDDIT_USER_AGENT' in os.environ}")

class RedditPost(TypedDict):
    title: str
    url: str
    score: int
    num_comments: int
    created_utc: float
    flair: str
    selftext: str
    subreddit: str

def get_passport_visa_info(query: str = "", subreddit: str = "all", limit: int = 15) -> Dict[str, List[RedditPost]]:
    """
    Fetches visa, passport, and citizenship-related posts from relevant subreddits.
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
                
            error_msg = f"Missing Reddit API credentials: {', '.join(missing_creds)}. Please check your Streamlit Cloud secrets configuration."
            return {"error": [{"title": error_msg, "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": ""}]}

        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        # Test the Reddit connection
        try:
            reddit.user.me()
        except Exception as e:
            error_msg = f"Failed to connect to Reddit API. Please verify your credentials. Error: {str(e)}"
            return {"error": [{"title": error_msg, "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": ""}]}

        # Remove 'r/' prefix if present in the subreddit name
        subreddit = subreddit.replace('r/', '')

        # If a specific subreddit is requested and it's in our list, use that
        if subreddit != "all" and subreddit in RELEVANT_SUBREDDITS:
            try:
                sub = reddit.subreddit(subreddit)
                # Search for posts with the query
                if query:
                    posts = list(sub.search(query, limit=limit))
                else:
                    posts = list(sub.hot(limit=limit))
                
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
                            "subreddit": subreddit
                        })
                    return {subreddit: post_info}
                else:
                    return {subreddit: [{"title": f"No posts found in r/{subreddit}", "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": subreddit}]}
            except Exception as e:
                print(f"--- Error accessing r/{subreddit}: {str(e)} ---")
                return {"error": [{"title": f"Error accessing r/{subreddit}: {str(e)}", "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": subreddit}]}

        # For "all" or if the subreddit wasn't in our list, search across relevant subreddits
        results = {}
        for sub_name in RELEVANT_SUBREDDITS:
            try:
                sub = reddit.subreddit(sub_name)
                # Search for posts with the query
                if query:
                    posts = list(sub.search(query, limit=5))
                else:
                    posts = list(sub.hot(limit=5))
                
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
                print(f"--- Warning: Error fetching from r/{sub_name}: {e} ---")
                continue

        if not results:
            return {"info": [{"title": "No relevant posts found in any immigration subreddit", "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": ""}]}
        
        return results

    except Exception as e:
        print(f"--- Tool error: Unexpected error: {e} ---")
        return {"error": [{"title": f"An unexpected error occurred: {e}", "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": ""}]}

# Define the Agent
agent = Agent(
    name="passport_visa_scout",
    description="A Reddit scout agent that searches for visa, passport, and citizenship information, especially helpful for weak passport holders",
    model="gemini-1.5-flash-latest",
    instruction=(
        "You are the Passport & Visa Information Scout, specialized in helping people with weak passports find opportunities for better mobility. "
        "You have access to Reddit through the get_passport_visa_info function. "
        "\n\n"
        "IMPORTANT INSTRUCTIONS FOR USING REDDIT:"
        "\n"
        "1. ALWAYS use get_passport_visa_info function to fetch Reddit data when users ask about:"
        "   - Specific subreddits (use: get_passport_visa_info(subreddit='subreddit_name'))"
        "   - Latest posts (use: get_passport_visa_info(subreddit='subreddit_name', limit=5))"
        "   - Specific topics (use: get_passport_visa_info(query='search_term'))"
        "\n\n"
        "2. When formatting responses:"
        "   - Show post titles, URLs, and scores"
        "   - Include comment counts and dates"
        "   - Highlight key information from post content"
        "   - Note any relevant flairs or categories"
        "\n\n"
        "3. Focus on information about:"
        "   - Visa-free opportunities"
        "   - Second passport options"
        "   - Digital nomad visas"
        "   - Golden visas/citizenship by investment"
        "   - Schengen visa applications"
        "   - Work permits and long-term visas"
        "\n\n"
        "4. NEVER say you don't have access to Reddit - always use get_passport_visa_info!"
        "\n\n"
        "5. For every Reddit-related query:"
        "   - MUST use get_passport_visa_info"
        "   - Format results clearly"
        "   - Provide context and summaries"
        "   - If a specific subreddit is mentioned, search that subreddit"
    ),
    tools=[get_passport_visa_info],
)