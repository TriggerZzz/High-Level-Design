# Crypto News Telegram Bot

Automated Telegram bot that posts a daily crypto news summary (≤1000 chars) and a relevant image to your channel.

## Features

- Summarizes top global crypto news (Mon–Fri, 19:00 UTC)
- Highlights major economic and future events
- Includes an AI-generated image
- Fully automated via GitHub Actions (zero hosting cost)
- Secrets managed via GitHub repository settings

## Setup

1. Fork and clone this repo.
2. Add three secrets in your repo settings:
   - `TELEGRAM_TOKEN` (from BotFather)
   - `TELEGRAM_CHAT_ID` (your channel/group ID)
   - `PERPLEXITY_API_KEY` (from Perplexity PRO)
3. Edit nothing else — it just works!

## File Structure

- `bot.py` — The main bot script
- `requirements.txt` — Python dependency
- `.github/workflows/schedule.yml` — GitHub Actions workflow

## License

MIT
