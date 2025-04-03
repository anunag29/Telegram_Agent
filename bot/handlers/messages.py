import os

from telegram import Update, Document
from telegram.ext import CallbackContext

from ..agent import agent
from .voice import transcribe_audio
from ..config import TEMP_DIR
from .documents import process_pdf


async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text("Hello! I am Severus your AI assistant. How can I help you?")

async def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text
    response = agent.get_response(user_message, session_id=update.message.from_user.id)
    await update.message.reply_text(response)

async def handle_voice_message(update: Update, context: CallbackContext) -> None:
    file = await context.bot.get_file(update.message.voice.file_id)
    file_path = os.path.join(TEMP_DIR,"voice_message.ogg")
    await file.download_to_drive(file_path)
    
    transcription = transcribe_audio(file_path)
    os.remove(file_path)

    if transcription:
        print(transcription)
        response = agent.get_response(transcription, session_id=update.message.from_user.id)
        await update.message.reply_text(response)
    else:
        await update.message.reply_text("Sorry, I couldn't transcribe the audio.")

async def handle_document(update: Update, context: CallbackContext) -> None:
    """Handles PDF file uploads from users."""
    document: Document = update.message.document

    if document.mime_type != "application/pdf":
        await update.message.reply_text("Please upload a valid PDF document.")
        return

    # Download the PDF file
    file_path = os.path.join(TEMP_DIR, document.file_name)
    file = await context.bot.get_file(document.file_id)
    await file.download_to_drive(file_path)

    response = process_pdf(file_path)
    os.remove(file_path)
    await update.message.reply_text(response)
    
    