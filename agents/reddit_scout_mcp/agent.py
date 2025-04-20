import random
import os
from typing import Dict, List, TypedDict, Optional
from datetime import datetime
import json
from pathlib import Path
import time
import pickle
import gzip
import shutil
from dataclasses import dataclass
import logging

from google.adk.agents import Agent

from dotenv import load_dotenv
print("--- Attempting to load .env file ---")
load_dotenv()
print(f"--- Current working directory: {os.getcwd()} ---")
print("--- Checking for environment variables ---")
print(f"CLIENT_ID exists: {'REDDIT_CLIENT_ID' in os.environ}")
print(f"CLIENT_SECRET exists: {'REDDIT_CLIENT_SECRET' in os.environ}")
print(f"USER_AGENT exists: {'REDDIT_USER_AGENT' in os.environ}")

import praw
from praw.exceptions import PRAWException

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class CacheConfig:
    """Configuration for cache settings."""
    cache_dir: Path
    ttl: int
    max_size_mb: int
    compression: bool

def get_cache_config() -> CacheConfig:
    """Get cache configuration from environment variables with defaults."""
    cache_dir = Path(os.getenv("MCP_CACHE_DIR", ".mcp_cache"))
    ttl = int(os.getenv("MCP_TTL", "3600"))  # 1 hour default
    max_size_mb = int(os.getenv("MCP_MAX_SIZE_MB", "100"))  # 100MB default
    compression = os.getenv("MCP_COMPRESSION", "true").lower() == "true"
    
    return CacheConfig(cache_dir, ttl, max_size_mb, compression)

# Initialize cache configuration
CACHE_CONFIG = get_cache_config()
CACHE_CONFIG.cache_dir.mkdir(exist_ok=True)

class CacheStats:
    """Track cache statistics."""
    def __init__(self):
        self.hits = 0
        self.misses = 0
        self.errors = 0
        self.total_size = 0
    
    def hit(self):
        self.hits += 1
    
    def miss(self):
        self.misses += 1
    
    def error(self):
        self.errors += 1
    
    def update_size(self, size_bytes: int):
        self.total_size += size_bytes
    
    def get_stats(self) -> Dict[str, int]:
        return {
            "hits": self.hits,
            "misses": self.misses,
            "errors": self.errors,
            "total_size_mb": self.total_size // (1024 * 1024)
        }

CACHE_STATS = CacheStats()

class RedditPost(TypedDict):
    title: str
    url: str
    score: int
    num_comments: int
    created_utc: float
    flair: str
    selftext: str
    subreddit: str

def get_cache_key(query: str, subreddit: str, limit: int) -> str:
    """Generate a cache key from the function parameters."""
    return f"{query}_{subreddit}_{limit}"

def get_cache_path(cache_key: str) -> Path:
    """Get the cache file path for a given key."""
    return CACHE_CONFIG.cache_dir / f"{cache_key}.cache"

def cleanup_expired_cache() -> None:
    """Remove expired cache files."""
    current_time = time.time()
    for cache_file in CACHE_CONFIG.cache_dir.glob("*.cache"):
        try:
            with open(cache_file, 'rb') as f:
                cached_data = pickle.load(f)
                if current_time - cached_data['timestamp'] > CACHE_CONFIG.ttl:
                    cache_file.unlink()
                    logger.info(f"Removed expired cache file: {cache_file}")
        except Exception as e:
            logger.error(f"Error cleaning up cache file {cache_file}: {e}")
            CACHE_STATS.error()

def get_cache_size() -> int:
    """Get total size of cache directory in bytes."""
    return sum(f.stat().st_size for f in CACHE_CONFIG.cache_dir.glob("*.cache"))

def enforce_cache_size_limit() -> None:
    """Remove oldest cache files if size limit is exceeded."""
    current_size = get_cache_size()
    max_size_bytes = CACHE_CONFIG.max_size_mb * 1024 * 1024
    
    if current_size > max_size_bytes:
        # Sort files by modification time
        cache_files = sorted(
            CACHE_CONFIG.cache_dir.glob("*.cache"),
            key=lambda x: x.stat().st_mtime
        )
        
        while current_size > max_size_bytes and cache_files:
            oldest_file = cache_files.pop(0)
            current_size -= oldest_file.stat().st_size
            oldest_file.unlink()
            logger.info(f"Removed oldest cache file to enforce size limit: {oldest_file}")

def get_from_cache(cache_key: str) -> Optional[Dict[str, List[RedditPost]]]:
    """Try to get results from cache."""
    cache_path = get_cache_path(cache_key)
    if cache_path.exists():
        try:
            open_func = gzip.open if CACHE_CONFIG.compression else open
            mode = 'rb' if CACHE_CONFIG.compression else 'rb'
            with open_func(cache_path, mode) as f:
                cached_data = pickle.load(f)
                if time.time() - cached_data['timestamp'] < CACHE_CONFIG.ttl:
                    logger.info("Cache hit")
                    CACHE_STATS.hit()
                    return cached_data['data']
                else:
                    logger.info("Cache miss (expired)")
                    CACHE_STATS.miss()
        except Exception as e:
            logger.error(f"Cache read error: {e}")
            CACHE_STATS.error()
    else:
        logger.info("Cache miss (not found)")
        CACHE_STATS.miss()
    return None

def save_to_cache(cache_key: str, data: Dict[str, List[RedditPost]]) -> None:
    """Save results to cache."""
    cache_path = get_cache_path(cache_key)
    try:
        cache_data = {
            'timestamp': time.time(),
            'data': data
        }
        
        open_func = gzip.open if CACHE_CONFIG.compression else open
        mode = 'wb' if CACHE_CONFIG.compression else 'wb'
        with open_func(cache_path, mode) as f:
            pickle.dump(cache_data, f)
        
        # Update cache size and enforce limits
        CACHE_STATS.update_size(cache_path.stat().st_size)
        enforce_cache_size_limit()
        
        logger.info(f"Saved to cache: {cache_path}")
    except Exception as e:
        logger.error(f"Cache write error: {e}")
        CACHE_STATS.error()

def get_passport_visa_info(query: str = "", subreddit: str = "all", limit: int = 15) -> Dict[str, List[RedditPost]]:
    """
    Fetches visa, passport, and citizenship-related posts from relevant subreddits.
    Uses local caching for better performance.
    """
    logger.info(f"Fetching information about {query if query else 'visa/passport'} from r/{subreddit}")
    
    # Clean up expired cache before proceeding
    cleanup_expired_cache()
    
    # Try to get from cache first
    cache_key = get_cache_key(query, subreddit, limit)
    cached_result = get_from_cache(cache_key)
    if cached_result is not None:
        return cached_result
    
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

    client_id = os.getenv("REDDIT_CLIENT_ID")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET")
    user_agent = os.getenv("REDDIT_USER_AGENT")

    if not all([client_id, client_secret, user_agent]):
        missing_creds = []
        if not client_id:
            missing_creds.append("REDDIT_CLIENT_ID")
        if not client_secret:
            missing_creds.append("REDDIT_CLIENT_SECRET")
        if not user_agent:
            missing_creds.append("REDDIT_USER_AGENT")
            
        error_msg = f"Missing Reddit API credentials in .env file: {', '.join(missing_creds)}. Please create a .env file with these credentials."
        print(f"--- Tool error: {error_msg} ---")
        return {"error": [{"title": error_msg, "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": ""}]}

    try:
        reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent,
        )

        # Remove 'r/' prefix if present in the subreddit name
        subreddit = subreddit.replace('r/', '')

        # If a specific subreddit is requested, use that
        if subreddit != "all":
            try:
                sub = reddit.subreddit(subreddit)
                # Get hot posts directly without search query
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
                    result = {subreddit: post_info}
                    save_to_cache(cache_key, result)
                    return result
                else:
                    result = {subreddit: [{"title": f"No posts found in r/{subreddit}", "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": subreddit}]}
                    save_to_cache(cache_key, result)
                    return result
            except Exception as e:
                print(f"--- Error accessing r/{subreddit}: {str(e)} ---")
                return {"error": [{"title": f"Error accessing r/{subreddit}: {str(e)}", "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": subreddit}]}

        # For "all", search across relevant subreddits
        results = {}
        for sub_name in RELEVANT_SUBREDDITS:
            try:
                sub = reddit.subreddit(sub_name)
                posts = list(sub.hot(limit=5))  # Limit to 5 posts per subreddit when searching all
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
                    results[sub_name] = post_info
            except Exception as e:
                print(f"--- Warning: Error fetching from r/{sub_name}: {e} ---")
                continue

        if not results:
            result = {"info": [{"title": "No posts found in any subreddit", "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": ""}]}
            save_to_cache(cache_key, result)
            return result
        
        save_to_cache(cache_key, results)
        return results

    except Exception as e:
        print(f"--- Tool error: Unexpected error: {e} ---")
        return {"error": [{"title": f"An unexpected error occurred: {e}", "url": "", "score": 0, "num_comments": 0, "created_utc": "", "flair": "", "selftext": "", "subreddit": ""}]}

# Define the Agent with caching capabilities
agent = Agent(
    name="passport_visa_scout_mcp",
    description="A Reddit scout agent that searches for visa, passport, and citizenship information with caching",
    model="gemini-1.5-flash-latest",
    instruction=(
        "You are the Passport & Visa Information Scout with caching, specialized in helping people with weak passports find opportunities for better mobility. "
        "You have access to Reddit through the get_passport_visa_info function with local caching. "
        "\n\n"
        "IMPORTANT INSTRUCTIONS FOR USING REDDIT WITH CACHING:"
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
        "   - Indicate if the content is from cache"
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
        "   - Leverage caching for better performance"
    ),
    tools=[get_passport_visa_info],
) 