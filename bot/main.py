import os
from dotenv import load_dotenv
from groq import Groq
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Load API keys from .env file
load_dotenv()
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize Groq client
client = Groq(api_key=GROQ_API_KEY)

# Function to call Groq LLM
def chat_with_groq(prompt):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",  
            messages=[{"role": "user", "content": prompt}],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=False,  
            stop=None,
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

# Start command
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I am your AI assistant. How can I help you?")

# Handle messages
async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response = chat_with_groq(user_message)
    await update.message.reply_text(response)

# Main function to run the bot
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Commands
    app.add_handler(CommandHandler("start", start))
    
    # Message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
