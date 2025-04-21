from agents.reddit_scout.agent import get_reddit_posts as get_info_original
from agents.reddit_scout_mcp.agent import get_passport_visa_info as get_info_mcp
import time

def test_agent_performance():
    print("Testing original agent...")
    start_time = time.time()
    original_results = get_info_original(subreddit='digitalnomad', limit=3)
    original_time = time.time() - start_time
    print(f"Original agent took {original_time:.2f} seconds")
    
    print("\nTesting MCP agent (first run)...")
    start_time = time.time()
    mcp_results = get_info_mcp(subreddit='digitalnomad', limit=3)
    mcp_time_first = time.time() - start_time
    print(f"MCP agent first run took {mcp_time_first:.2f} seconds")
    
    print("\nTesting MCP agent (cached run)...")
    start_time = time.time()
    mcp_results_cached = get_info_mcp(subreddit='digitalnomad', limit=3)
    mcp_time_cached = time.time() - start_time
    print(f"MCP agent cached run took {mcp_time_cached:.2f} seconds")
    
    print("\nPerformance comparison:")
    print(f"Original agent: {original_time:.2f} seconds")
    print(f"MCP agent (first run): {mcp_time_first:.2f} seconds")
    print(f"MCP agent (cached run): {mcp_time_cached:.2f} seconds")
    print(f"Cache speedup: {mcp_time_first/mcp_time_cached:.2f}x")
    
    print("\nResults comparison:")
    print("\nOriginal agent results:")
    for post in original_results.get('digitalnomad', []):
        print(f"\nTitle: {post['title']}")
        print(f"URL: {post['url']}")
    
    print("\nMCP agent results:")
    for post in mcp_results.get('digitalnomad', []):
        print(f"\nTitle: {post['title']}")
        print(f"URL: {post['url']}")

if __name__ == "__main__":
    test_agent_performance() 