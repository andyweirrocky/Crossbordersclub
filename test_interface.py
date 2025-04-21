import argparse
from agents.reddit_scout.agent import get_reddit_posts as get_info_original
from agents.reddit_scout_mcp.agent import get_passport_visa_info as get_info_mcp
import time

def print_results(results, agent_name):
    print(f"\n{agent_name} Results:")
    print("-" * 80)
    
    for subreddit, posts in results.items():
        print(f"\nSubreddit: r/{subreddit}")
        print("=" * 40)
        
        for post in posts:
            print(f"\nTitle: {post['title']}")
            print(f"Score: {post['score']} | Comments: {post['num_comments']} | Date: {post['created_utc']}")
            if post['flair']:
                print(f"Flair: {post['flair']}")
            print(f"URL: {post['url']}")
            if post['selftext']:
                print(f"Content Preview: {post['selftext'][:200]}...")
            print("-" * 40)

def interactive_mode():
    while True:
        print("\nReddit Agent Testing Interface")
        print("=" * 30)
        print("1. Search specific subreddit")
        print("2. Search across all immigration subreddits")
        print("3. Compare agents (same query)")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ")
        
        if choice == "4":
            print("Goodbye!")
            break
            
        if choice in ["1", "2"]:
            query = input("Enter search query (press Enter for none): ").strip()
            subreddit = "all" if choice == "2" else input("Enter subreddit name: ").strip()
            limit = int(input("Enter number of posts to retrieve (1-15): ").strip())
            
            agent_choice = input("Choose agent (1: Original, 2: MCP, 3: Both): ").strip()
            
            if agent_choice in ["1", "3"]:
                start_time = time.time()
                results = get_info_original(query=query, subreddit=subreddit, limit=limit)
                orig_time = time.time() - start_time
                print(f"\nOriginal agent took {orig_time:.2f} seconds")
                print_results(results, "Original Agent")
                
            if agent_choice in ["2", "3"]:
                start_time = time.time()
                results = get_info_mcp(query=query, subreddit=subreddit, limit=limit)
                mcp_time = time.time() - start_time
                print(f"\nMCP agent took {mcp_time:.2f} seconds")
                print_results(results, "MCP Agent")
                
        elif choice == "3":
            query = input("Enter search query (press Enter for none): ").strip()
            subreddit = input("Enter subreddit name (press Enter for 'all'): ").strip() or "all"
            limit = int(input("Enter number of posts to retrieve (1-15): ").strip())
            
            # Test original agent
            start_time = time.time()
            orig_results = get_info_original(query=query, subreddit=subreddit, limit=limit)
            orig_time = time.time() - start_time
            print(f"\nOriginal agent took {orig_time:.2f} seconds")
            print_results(orig_results, "Original Agent")
            
            # Test MCP agent (first run)
            start_time = time.time()
            mcp_results = get_info_mcp(query=query, subreddit=subreddit, limit=limit)
            mcp_time_first = time.time() - start_time
            print(f"\nMCP agent (first run) took {mcp_time_first:.2f} seconds")
            print_results(mcp_results, "MCP Agent (First Run)")
            
            # Test MCP agent (cached run)
            start_time = time.time()
            mcp_results_cached = get_info_mcp(query=query, subreddit=subreddit, limit=limit)
            mcp_time_cached = time.time() - start_time
            print(f"\nMCP agent (cached run) took {mcp_time_cached:.2f} seconds")
            print(f"Cache speedup: {mcp_time_first/mcp_time_cached:.2f}x")
            
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Test Reddit Agents")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive mode")
    args = parser.parse_args()
    
    if args.interactive:
        interactive_mode()
    else:
        print("Please run with --interactive flag for interactive mode") 