import os
import json
import time
import requests
from datetime import datetime

# Configuration - Set these in environment variables or replace directly
NEWS_API_KEY = ""  # Replace with your NewsAPI key
TELEGRAM_BOT_TOKEN = ""  # Your bot token
TELEGRAM_CHANNEL_ID = ""  # Your channel ID
INTERVAL_MINUTES = 30  # Check interval in minutes
JSON_FILE = 'news_data.json'

def fetch_news():
    """Fetch top headlines from News API"""
    url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json().get('articles', [])
    except requests.exceptions.RequestException as e:
        print(f"News API Error: {e}")
        return []

def load_existing_news():
    """Load existing news from JSON file"""
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading news file: {e}")
    return []

def save_news(news):
    """Save news to JSON file"""
    try:
        with open(JSON_FILE, 'w') as f:
            json.dump(news, f, indent=2)
    except Exception as e:
        print(f"Error saving news: {e}")

def filter_new_articles(existing, new_articles):
    """Filter out articles already in existing list"""
    existing_urls = {article['url'] for article in existing}
    return [article for article in new_articles
            if article['url'] not in existing_urls]

def send_to_telegram(article):
    """Send article to Telegram channel"""
    text = f"<b>{article['title']}</b>\n\n" \
           f"{article['description'] or 'No description available'}\n\n" \
           f"<a href='{article['url']}'>Read more</a>"

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': TELEGRAM_CHANNEL_ID,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False,
        'disable_notification': True
    }

    try:
        response = requests.post(url, json=payload)
        return response.json().get('ok', False)
    except Exception as e:
        print(f"Telegram send error: {e}")
        return False

def news_check():
    """Main function to check and process news"""
    print(f"\n{datetime.now().isoformat()} - Checking news...")

    # Fetch and process news
    existing = load_existing_news()
    new_articles = fetch_news()
    to_send = filter_new_articles(existing, new_articles)

    if not to_send:
        print("No new articles found")
        return

    print(f"Found {len(to_send)} new articles")

    # Update storage
    updated_news = existing + to_send
    save_news(updated_news)

    # Send to Telegram
    for article in to_send:
        if send_to_telegram(article):
            print(f"Sent: {article['title'][:50]}...")
            time.sleep(1)  # Avoid rate limiting
        else:
            print(f"Failed to send: {article['title']}")

if __name__ == "__main__":
    print(f"Bot started. Checking every {INTERVAL_MINUTES} minutes...")

    while True:
        news_check()
        # Wait for the specified interval before checking again
        time.sleep(INTERVAL_MINUTES * 6)
