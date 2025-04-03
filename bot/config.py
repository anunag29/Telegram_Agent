import os

BASE_DIR = os.getcwd()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "7932825476:AAHMV6hUdQ53MSIy8lDHlFR6cgOY92luzyI")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "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")
TEMP_DIR = os.getenv('TEMP_DIR', os.path.join(BASE_DIR,"bot/temp"))

