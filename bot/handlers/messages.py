import os

from telegram import Update
from telegram.ext import CallbackContext

from ..agent import get_response
from .voice import transcribe_audio
from ..config import TEMP_DIR


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I am Severus your AI assistant. How can I help you?")

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response = get_response(user_message, session_id=update.message.from_user.id)
    await update.message.reply_text(response)

async def handle_voice_message(update: Update, context: CallbackContext) -> None:
    file = await context.bot.get_file(update.message.voice.file_id)
    file_path = os.path.join(TEMP_DIR,"voice_message.ogg")
    await file.download_to_drive(file_path)
    
    transcription = transcribe_audio(file_path)
    os.remove(file_path)

    if transcription:
        response = get_response(transcription, session_id=update.message.from_user.id)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Sorry, I couldn't transcribe the audio.")
    
    