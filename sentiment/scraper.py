import praw
import datetime as dt
import pandas as pd
from time import sleep
import re

def scrape_headlines(subreddit='wallstreetbets', max_items=100, save_path="data/reddit_headlines"): # Should decide what is optimal later
    """
    Scrape reddit headline associated with
    """
    reddit = praw.Reddit(
        client_id="g9nwtU6IkB7ey_6AdiVLmQ",
        client_secret="D-Wgdk1fBlBPJg7tYPZQJ0VSSZAc4w",
        user_agent="fin-scraper:v1 (by u/mtaylor121303)"
    )

    posts = []
    for post in reddit.subreddit(subreddit).new(limit=max_items*2):
        post_timestamp = int(post.created_utc)

        if post.score > 10:
            posts.append({
                'title': post.title,
                'timestamp': dt.datetime.fromtimestamp(post_timestamp),
                'score': post.score                                      
            })


    df = pd.DataFrame(posts)
    df.to_csv(save_path + "/" + subreddit + ".csv", index=False)
    sleep(2)
    return df

if __name__ == "__main__":
    scrape_headlines(subreddit="wallstreetbets", max_items=1000)
    scrape_headlines(subreddit="stocks", max_items=1000)
    scrape_headlines(subreddit="investing", max_items=1000)
    scrape_headlines(subreddit="StockMarke", max_items=1000)
