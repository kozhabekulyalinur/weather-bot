import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "")

DEFAULT_CITY = os.getenv("DEFAULT_CITY", "Astana")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "KZ")
UNITS = "metric"
LANG = "ru"

API_RETRIES = 3
API_RETRY_DELAY = 2

USERS_FILE = BASE_DIR / "users.json"
