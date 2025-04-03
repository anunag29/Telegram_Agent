import os

BASE_DIR = os.getcwd()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TEMP_DIR = os.getenv('TEMP_DIR', os.path.join(BASE_DIR,"bot/temp"))
