import requests
from bs4 import BeautifulSoup
import re

def scrape_headlines(max_items=5): # Should decide what is optimal later
    """
    Scrape Yahoo Finance Headlines from main page
    """
    base_url = "https://finance.yahoo.com/"
    url = base_url # TODO implement ticker specific page

    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: {url} ({response.status_code})")
    
    soup = BeautifulSoup(response.text, "html.parser")

    # keep h3 and h2 headlines
    headlines = set()
    for tag in soup.find_all(['h3', 'h2'], limit=50):
        if tag.text:
            # clear unnecessary spaces
            clean_text = re.sub(r'\s+', ' ', tag.text.strip())
            headlines.add(clean_text)

    return list(headlines)[:max_items]
    

def process_headlines(headlines):
    processed = []
    for h in headlines:
        h_clean = re.sub(r'[^\w\s]', '',  h.lower().strip())
        if h_clean:
            processed.append(h_clean)
    return processed

if __name__ == "__main__":
    headlines = scrape_headlines(max_items=20)
    processed = process_headlines(headlines)

    # check we're cleaning the headlines
    print("Raw Headlines:")
    for h in headlines:
        print("-", h)

    print("\nProcessed:")
    for p in processed:
        print("-", p)
