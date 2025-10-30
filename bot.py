import os
import requests
import logging
import sys

# Configurable endpoints in case the API changes
PERPLEXITY_CHAT_API = os.getenv("PERPLEXITY_CHAT_API", "https://api.perplexity.ai/v1/chat/completions")
PERPLEXITY_IMAGE_API = os.getenv("PERPLEXITY_IMAGE_API", "https://api.perplexity.ai/v1/images/generate")
MAX_LENGTH = 1000

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

logging.basicConfig(level=logging.INFO)

def notify_telegram_error(message):
    """Send an error notification to Telegram (optional)."""
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": f"❌ BOT ERROR:\n{message[:3500]}", "parse_mode": "HTML"}
        try:
            requests.post(url, data=payload, timeout=10)
        except Exception:
            pass

def fetch_crypto_news():
    if not PERPLEXITY_API_KEY:
        raise RuntimeError("PERPLEXITY_API_KEY is missing")
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
    try:
        resp = requests.post(PERPLEXITY_CHAT_API, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        content = data["choices"][0]["message"]["content"].strip()
        if len(content) > MAX_LENGTH:
            content = content[:MAX_LENGTH-3] + "..."
        return content
    except requests.HTTPError as e:
        logging.error(f"Perplexity API HTTPError: {e} - Response: {getattr(e.response, 'text', '')}")
        raise
    except Exception as e:
        logging.error(f"Perplexity API Error: {e}")
        raise

def generate_image(news_text):
    if not PERPLEXITY_API_KEY:
        raise RuntimeError("PERPLEXITY_API_KEY is missing")
    prompt = f"Create an eye-catching, non-branded image representing this crypto market news headline: {news_text[:100]}"
    headers = {
        "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "prompt": prompt,
        "size": "1024x1024"
    }
    try:
        resp = requests.post(PERPLEXITY_IMAGE_API, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["data"][0]["url"]
    except requests.HTTPError as e:
        logging.error(f"Perplexity Image API HTTPError: {e} - Response: {getattr(e.response, 'text', '')}")
        raise
    except Exception as e:
        logging.error(f"Perplexity Image API Error: {e}")
        raise

def send_to_telegram(text, image_url):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError("TELEGRAM_TOKEN or TELEGRAM_CHAT_ID is missing")
    send_photo_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "caption": text,
        "photo": image_url,
        "parse_mode": "HTML"
    }
    try:
        resp = requests.post(send_photo_url, data=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logging.error(f"Telegram API Error: {e}")
        raise

def main():
    try:
        if not all([TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, PERPLEXITY_API_KEY]):
            raise RuntimeError("One or more required environment variables are missing.")
        news = fetch_crypto_news()
        img_url = generate_image(news)
        send_to_telegram(news, img_url)
        logging.info("Successfully posted news and image to Telegram.")
    except Exception as e:
        err_msg = f"Error in bot flow: {e}"
        logging.error(err_msg)
        notify_telegram_error(err_msg)
        # Don't exit non-zero to avoid failing the workflow (optional)
        sys.exit(0)

if __name__ == "__main__":
    main()
