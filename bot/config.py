import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TEMP_DIR = os.getenv('TEMP_DIR')

os.makedirs(TEMP_DIR, exist_ok=True)

Groq_Client = Groq(api_key=GROQ_API_KEY)



# TELEGRAM_BOT_TOKEN="7932825476:AAHMV6hUdQ53MSIy8lDHlFR6cgOY92luzyI"
# GROQ_API_KEY="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"
# TEMP_DIR="/home/anunag/Data/iitb_projects/Telegram_Agent/bot/temp"

