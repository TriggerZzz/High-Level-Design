import os
import requests
import logging

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")
PERPLEXITY_API_URL = "https://api.perplexity.ai/v1/chat/completions"
PERPLEXITY_IMAGE_URL = "https://api.perplexity.ai/v1/images/generate"
MAX_LENGTH = 1000

logging.basicConfig(level=logging.INFO)

def fetch_crypto_news():
    prompt = (
        "Summarize today's top global news about the crypto market. "
        "Include major economic events, and highlight any breaking news about future events. "
        "Make the article no more than 1000 characters (with spaces). "
        "At the end of the article include these two hashtags: #CryptoNews #MarketOverview"
    )
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3-sonar-large-32k-online",
        "messages": [{"role": "user", "content": prompt}]
    }
    resp = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    result = resp.json()["choices"][0]["message"]["content"].strip()
    if len(result) > MAX_LENGTH:
        result = result[:MAX_LENGTH-3] + "..."
    return result

def generate_image(news_text):
    prompt = f"Create an eye-catching, non-branded image representing this crypto market news headline: {news_text[:100]}"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "size": "1024x1024"
    }
    resp = requests.post(PERPLEXITY_IMAGE_URL, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    return resp.json()["data"][0]["url"]

def send_to_telegram(text, image_url):
    send_photo_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": text,
        "photo": image_url,
        "parse_mode": "HTML"
    }
    resp = requests.post(send_photo_url, data=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main():
    try:
        news = fetch_crypto_news()
        img_url = generate_image(news)
        send_to_telegram(news, img_url)
        logging.info("Successfully posted news and image to Telegram.")
    except Exception as e:
        logging.error(f"Error in bot flow: {e}")
        raise

if __name__ == "__main__":
    main()
