# MyLook — Telegram wardrobe bot

MyLook is a Telegram bot that helps you decide **what to wear**.

You add the clothes you own, and the bot suggests outfits made only from your clothes.

> The bot talks to users in Russian.

## What it does

1. **Add your clothes.** Send a photo and give each item a name and type (top, bottom, shoes, etc.).
2. **Add places.** For example "University", "Walk" or "Restaurant". Then mark which clothes fit which place.
3. **Get an outfit.** Pick a place, and the bot shows you **2 outfit ideas** from your wardrobe.
4. **Missing something?** The bot tells you what's missing (for example, "no shoes") and gives you search links for Wildberries, Ozon and Lamoda.

An outfit is either **top + bottom + shoes** or **one-piece (like a dress) + shoes**. If you have them, the bot also adds a jacket and an accessory.

## How to run it

You need **Python 3.10 or newer**.

**1. Get a bot token**

Open [@BotFather](https://t.me/BotFather) in Telegram, send `/newbot` and follow the steps. BotFather will give you a token. Keep it secret.

**2. Install**

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**3. Add your token**

Copy `.env.example` to a new file called `.env` and put your token inside:

```
BOT_TOKEN=your-token-here
```

**4. Start the bot**

```bash
python bot.py
```

Now open your bot in Telegram and send `/start`.

## Run the tests

```bash
pytest -q
```

## Where things are

| File / folder | What it is |
|---|---|
| `bot.py` | Starts the bot |
| `handlers/` | What the bot does for each button and command |
| `outfit.py` | How outfits are picked |
| `storage.py` | Saves your wardrobe to a file |
| `shop.py` | Shop search links |
| `texts.py` | All the bot's messages |
| `tests/` | Tests |
| `data/` | Your saved wardrobe (`wardrobe.json`, created automatically) |

## Built with

Python, [aiogram 3](https://docs.aiogram.dev/), pytest.

## License

[MIT](LICENSE)
