"""Настройки бота из переменных окружения (или файла .env)."""

import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
DATA_PATH = os.getenv("DATA_PATH", "data/wardrobe.json")
