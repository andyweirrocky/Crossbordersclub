from agents.reddit_scout.agent import get_passport_visa_info

def search_digital_nomad_info():
    print("Searching for digital nomad visa information...")
    print("\nChecking r/digitalnomad specifically...")
    dn_results = get_passport_visa_info(query="digital nomad visa", subreddit='digitalnomad', limit=3)
    
    print("\nResults from r/digitalnomad:")
    for post in dn_results.get('digitalnomad', []):
        print(f"\nTitle: {post['title']}")
        print(f"URL: {post['url']}")
        print(f"Score: {post['score']}")
        print(f"Comments: {post['num_comments']}")
        print(f"Date: {post['created_utc']}")
        if post.get('selftext'):
            print(f"Preview: {post['selftext'][:200]}...")
    
    print("\nSearching across all relevant subreddits for digital nomad visa info...")
    all_results = get_passport_visa_info(query="digital nomad visa", subreddit='all', limit=2)
    
    print("\nResults from all relevant subreddits:")
    for subreddit, posts in all_results.items():
        if posts:  # Only show subreddits that returned posts
            print(f"\n=== Posts from r/{subreddit} ===")
            for post in posts[:2]:
                print(f"\nTitle: {post['title']}")
                print(f"URL: {post['url']}")
                print(f"Score: {post['score']}")
                print(f"Comments: {post['num_comments']}")
                if post.get('selftext'):
                    print(f"Preview: {post['selftext'][:200]}...")

if __name__ == "__main__":
    search_digital_nomad_info() 