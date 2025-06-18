import praw
import datetime as dt
import pandas as pd
import re

def scrape_headlines(subreddit='wallstreetbets', start_date="2025-06-15", end_date="2025-06-17", max_items=100, save_path="data/reddit_headlines.csv"): # Should decide what is optimal later
    """
    Scrape reddit headline associated with
    """
    reddit = praw.Reddit(
        client_id="g9nwtU6IkB7ey_6AdiVLmQ",
        client_secret="D-Wgdk1fBlBPJg7tYPZQJ0VSSZAc4w",
        user_agent="fin-scraper:v1 (by u/mtaylor121303)"
    )

    # convert start and end timestamps to UNIX
    start_timestamp = int(dt.datetime.fromisoformat(start_date).timestamp())
    end_timestamp = int(dt.datetime.fromisoformat(end_date).timestamp())

    posts = []
    for post in reddit.subreddit(subreddit).new(limit=max_items * 2):
        post_timestamp = int(post.created_utc)

        if post.score > 30:
            posts.append({
                'title': post.title,
                'timestamp': dt.datetime.fromtimestamp(post_timestamp),
                'score': post.score                                      
            })
        if len(posts) >= max_items:
            break

    df = pd.DataFrame(posts)
    df.to_csv(save_path, index=False)
    return df

if __name__ == "__main__":
    headlines = scrape_headlines(max_items=1_000)
