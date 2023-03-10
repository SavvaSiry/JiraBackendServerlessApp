import telegram
from telegram.ext import Updater, MessageHandler, Filters
import requests

TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN_HERE'
SERVER_URL = 'YOUR_SERVER_URL_HERE'

def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="Hello! I'm your audio message bot. Send me an audio message and I'll send it to the server.")

def echo(update, context):
    file_id = update.message.voice.file_id
    file = context.bot.getFile(file_id)
    file_url = file.file_path
    headers = {'Content-Type': 'audio/ogg'}
    files = {'audio': requests.get(file_url).content}
    response = requests.post(SERVER_URL, headers=headers, files=files)
    context.bot.send_message(chat_id=update.effective_chat.id, text=response.text)

def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.voice, echo))
    dp.add_handler(MessageHandler(Filters.text, start))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
