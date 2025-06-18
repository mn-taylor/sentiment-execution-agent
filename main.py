from sentiment import scraper
from sentiment import sentiment_model
import matplotlib.pyplot as plt

subreddits = ["wallstreetbets", "investing", "StockMarket", "stocks"]

for subreddit in subreddits:
    # scraper.scrape_headlines(subreddit=subreddit, max_items=1000)

    path = "data/reddit_headlines" + "/" + subreddit + ".csv"
    window = 15
    df = sentiment_model.vader_sentiment_score(csv_path=path, window=window)

    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['sentiment_score'], alpha=0.4, label='Raw Sentiment', linestyle='--')
    plt.plot(df['timestamp'], df['smoothed_sentiment'], label=f'Smoothed Sentiment ({window}-point avg)', linewidth=2)
    plt.xlabel('Time')
    plt.ylabel('Sentiment Score')
    plt.title('Reddit Sentiment Over Time (Smoothed)')
    plt.legend()
    plt.tight_layout()

    plt.savefig(f"data/reddit_headlines/{subreddit}_sentiment_scores_.png", dpi=300)

    sentiment_model.interpolate_sentiment(path, "data/reddit_headlines" + "/" + subreddit + "_interpolated.csv")