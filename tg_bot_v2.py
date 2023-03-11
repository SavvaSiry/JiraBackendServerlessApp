import os
import openai
import telebot
import requests

TOKEN = os.getenv('YOUR_TELEGRAM_BOT_TOKEN_HERE')
openai.api_key = os.getenv('OPENAI_KEY')
# SERVER_URL = 'YOUR_SERVER_URL_HERE'
bot = telebot.TeleBot(TOKEN)
YANDEX_API_KEY = os.getenv('YANDEX_KEY')


@bot.message_handler(content_types=['voice'])
def handle_voice_message(message):
    # Download voice message
    file_info = bot.get_file(message.voice.file_id)
    file_url = f'https://api.telegram.org/file/bot{bot.token}/{file_info.file_path}'
    response = requests.get(file_url)

    if response.status_code != 200:
        bot.reply_to(message, 'Sorry, something went wrong while downloading the voice message.')
        return

    # Send voice message to Yandex SpeechKit API
    headers = {'Authorization': f'Bearer {YANDEX_API_KEY}'}
    response = requests.post('https://stt.api.cloud.yandex.net/speech/v1/stt:recognize',
                             params={'lang': 'auto', 'folderId': 'b1g1o8strsir61qnc8nj'},
                             headers=headers,
                             data=response.content,
                             stream=True)

    if response.status_code != 200:
        print(response.json())
        bot.reply_to(message, 'Sorry, something went wrong with the SpeechKit API.')
        return

    # Send text message back to user
    text = response.json().get('result')
    bot.reply_to(message, 'Ваш запрос отправлен: ' + '"' + text + '"\n\nОжидайте ответа...')
    if text:
        bot.reply_to(message, 'Запрос: "' + text + '"' + sent_to_gpt(text))
    else:
        bot.reply_to(message, 'Sorry, I couldn\'t recognize any text from your voice message.')


@bot.message_handler(commands=['sendToGpt'])
def handle_gpt_request(message):
    bot.reply_to(message, sent_to_gpt(message.text.split('/sendToGpt ')[-1]))


def sent_to_gpt(text):
    print(text)
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": text}
            ]
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        return 'Sorry, an error occurred while processing your request.'


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    if message.text.startswith('/'):
        # Ignore messages that start with a command
        return

    response_text = 'Sorry, please use the command /sendToGpt to ask something.'
    bot.reply_to(message, response_text)


@bot.message_handler(commands=['start'])
async def start_handler(message):
    bot.reply_to(message, "Hello! I'm your audio message bot. Send me an audio message and I'll send it to the server.")


bot.polling()
