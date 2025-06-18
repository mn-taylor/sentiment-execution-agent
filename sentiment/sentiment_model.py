import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

def vader_sentiment_score(csv_path="reddit_headlines.csv", window=10):
    # load and make sure the headlines are sorted
    df = pd.read_csv(csv_path)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values('timestamp')

    analyzer = SentimentIntensityAnalyzer()
    df['sentiment_score'] = df["title"].apply(lambda t: analyzer.polarity_scores(str(t))['compound'])
    df['smoothed_sentiment'] = df['sentiment_score'].rolling(window=window, center=True).mean()

    df.to_csv(csv_path, index=False)
    return df

def interpolate_sentiment(csv_path, output_path):
    df = pd.read_csv(csv_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp')
    df.set_index('timestamp', inplace=True)

    sentiment_series = df["smoothed_sentiment"].resample('10min').mean()
    sentiment_series = sentiment_series.interpolate(method="linear")
    
    sentiment_series.to_csv(output_path, header=["sentiment_score"])
    return sentiment_series

if __name__ == '__main__':
    window = 15
    df = vader_sentiment_score(csv_path="data/reddit_headlines.csv", output_path="data/sentiment_scores.csv", window=window)

    plt.figure(figsize=(12, 6))
    plt.plot(df['timestamp'], df['sentiment_score'], alpha=0.4, label='Raw Sentiment', linestyle='--')
    plt.plot(df['timestamp'], df['smoothed_sentiment'], label=f'Smoothed Sentiment ({window}-point avg)', linewidth=2)
    plt.xlabel('Time')
    plt.ylabel('Sentiment Score')
    plt.title('Reddit Sentiment Over Time (Smoothed)')
    plt.legend()
    plt.tight_layout()

    plt.savefig("data/sentiment_scores.png", dpi=300)
    
    print(df.head())