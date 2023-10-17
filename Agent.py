# System and logic
import sys
from math import ceil

# Telegram libraries
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Info files
from bot_info import TOKEN, BOT_NAME

# Settings file
from settings.generate_config import generate_settings
import configparser
import sys

# Text processing
import text_processing as tp

# PDF generator
from pdf.pdf_generator import PdfGenerator

# OpenAI and generation
import openai
from chat import Chat

# Global variables
chat: Chat = None
pdf: PdfGenerator = None

# Commands to interact with the bot
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"Hello, I'm {BOT_NAME}! I am an NLP agent for Sergiy Horef. Type /help to see what I can do.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Please enter your idea so I could extrapolate it. I will provide a pdf and a txt files with the extrapolation.")

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("This is a custom command, you can add whatever text you want here.")

# Logic to handle responses
def handle_response(text: str) -> str:
    response: str = chat.generate_response(arg=text)
    return response

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pdf = PdfGenerator()
    print('Pdf initialized.')

    message_type: str = update.message.chat.type
    text: str = update.message.text
    print(f'User ({update.message.chat.id})-{update.message.from_user.first_name} in {message_type}: "{text}"')

    # To check if the message is private, or in a group chat.
    if message_type == 'group':
        if BOT_NAME in text:
            text_clean: str = text.replace(BOT_NAME, '').strip()
            await update.message.reply_text(f'Idea provided: {text}.')
            pdf.add_text(f"Idea provided: {text}\n")
            await update.message.reply_text(f'Extrapolation in progress...')
            response: str = handle_response(text_clean)
        else:
            return
    else:
        await update.message.reply_text(f'Idea provided: {text}.')
        pdf.add_text(f"Idea provided: {text}\n")
        await update.message.reply_text(f'Extrapolation in progress...')
        response: str = handle_response(text)
    
    print('Bot:', response)
    pdf.add_text(f"Extrapolation:\n {response}")
    pdf.save_pdf()
    print('Num of characters in the response:', len(response))
    # Telegram has a limit of 4096 characters per message. In case the message is longer, will have to split the text
    if len(response) > 4000:
        await update.message.reply_text(f'Extrapolation is too long to be sent in one message.\n Splitting into multiple messages...')
        for i in range(0, len(response), 4096):
            await update.message.reply_text(response[i:i+4096])
    else:
        await update.message.reply_text(f'Extrapolation:\n {response}')
    await update.message.reply_document(document=open('pdf/txt_result.txt', 'rb'))
    await update.message.reply_document(document=open('pdf/pdf_result.pdf', 'rb'))

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__ == '__main__':
    # Generating the settings file. 
    # Should be done before each run to ensure the settings are up to date.
    generate_settings()
    print('Settings generated.')

    # Initializing the chat.
    chat = Chat()
    print('Chat initialized.')

    # Setting up the API key.
    openai.api_key_path = chat.api_key_path

    # Setting up the bot.
    print('Starting bot...')
    app = Application.builder().token(TOKEN).build()

    # Commands handler for the bot
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('custom', custom_command))

    # Message handler for the bot
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Error handler for the bot
    app.add_error_handler(error)

    # Polling the bot
    print('Polling...')
    app.run_polling(poll_interval=3)