from telegram.ext import Application, CommandHandler, MessageHandler, filters

from .config import *
from .handlers import *

def main():
    bot = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    bot.add_handler(MessageHandler(filters.Document.PDF, handle_document))


    print("Bot is running...")
    bot.run_polling()

if __name__ == "__main__":
    main()
