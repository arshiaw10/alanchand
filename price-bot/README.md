# Price Bot 📊

A Telegram bot that publishes live **Iranian market prices** — currencies, gold & coins, and
cryptocurrencies — scraped from [alanchand.com](https://alanchand.com).

## Features

- 💱 Currency rates with buy/sell prices and USD cross-rate
- 🏅 Gold and coin prices
- ₿ Cryptocurrency prices in Toman and USD
- 📈 Trend indicators (up / down / flat) per item
- ⏱ Background scheduler scrapes on a fixed interval (default: every 5 minutes)
- 💾 Atomic JSON-file persistence with an in-memory cache
- ℹ️ Status dashboard (last scrape, next run, item counts, last error)

## Project layout

```
price-bot/
├── src/pricebot/
│   ├── bot/            # Telegram layer: handlers, keyboards, message rendering
│   ├── scraper/        # HTTP client + section parsers
│   ├── services/       # Business logic and scheduling
│   ├── storage/        # JSON-file repository
│   ├── __main__.py     # Entry point
│   ├── config.py       # Typed, validated configuration
│   └── models.py       # Shared data models
├── tests/              # Unit tests
├── pyproject.toml
└── .env.example
```

## Getting started

### 1. Prerequisites

- Python **3.11+**
- A Telegram bot token — create one via [@BotFather](https://t.me/BotFather)

### 2. Install

```bash
cd price-bot
python -m venv venv
venv\Scripts\pip install -e ".[dev]"     # Windows
# source venv/bin/activate && pip install -e ".[dev]"   # macOS/Linux
```

Or with Make (Windows):

```bash
make install
```

### 3. Configure

```bash
copy .env.example .env        # Windows
# cp .env.example .env        # macOS/Linux
```

Then edit `.env` and set `TELEGRAM_BOT_TOKEN`.

### 4. Run

```bash
venv\Scripts\pricebot          # installed entry point
# or
venv\Scripts\python -m pricebot
```

The bot starts the scheduler and begins polling Telegram immediately.

## Quality checks

```bash
make check     # lint + typecheck + tests
make test      # tests only
```

## Configuration reference

| Variable | Default | Description |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | *(required)* | Bot token from @BotFather |
| `SOURCE_URL` | `https://alanchand.com` | Website to scrape |
| `SCRAPE_INTERVAL_MINUTES` | `5` | Minutes between scrapes |
| `REQUEST_TIMEOUT` | `30` | HTTP timeout in seconds |
| `DATA_DIR` | `./data` | Where the JSON cache is stored |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL` |

## Building a standalone executable (optional)

```bash
venv\Scripts\pip install pyinstaller
venv\Scripts\pyinstaller --name price-bot --onefile src/pricebot/__main__.py
```

The binary lands in `dist/price-bot.exe` (Windows) or `dist/price-bot` (macOS/Linux).

## License

MIT
