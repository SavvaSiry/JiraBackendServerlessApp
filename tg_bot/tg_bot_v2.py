import os
import io

import openai
import requests
import telebot
import base64
from pydub import AudioSegment

TOKEN = os.getenv('YOUR_TELEGRAM_BOT_TOKEN_HERE')
openai.api_key = os.getenv('OPENAI_KEY')
# SERVER_URL = 'YOUR_SERVER_URL_HERE'
bot = telebot.TeleBot(TOKEN)
YANDEX_API_TOKEN = YANDEX_API_KEY = os.getenv('YANDEX_KEY')
YANDEX_API_ENDPOINT = "https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"


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
    bot.reply_to(message, 'Ваш запрос отправлен: ' + '"' + text + '"\n\nОжидайте ответ...')
    if text:
        response_gpt = sent_to_gpt(text)
        bot.reply_to(message, 'Запрос: "' + text + '"' + response_gpt)
        # voice =
        text_to_voice(message, response_gpt)
    else:
        bot.reply_to(message, '\nSorry, I couldn\'t recognize any text from your voice message.')


@bot.message_handler(commands=['sendToGpt'])
def handle_gpt_request(message):
    bot.reply_to(message, sent_to_gpt(message.text.split('/sendToGpt ')[-1]))


def sent_to_gpt(text):
    print(text)
    headers = {'Content-type': 'text/plain; charset=utf-8'}
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": text}
            ],
            headers=headers
        )
        return completion.choices[0].message["content"]
    except Exception as e:
        return 'Sorry, an error occurred while processing your request.'


def text_to_voice(message, text):
    try:
        first_sentence = get_first_sentence(text)
        (lang_code, confidence) = detect_language(first_sentence)
        ya_speaker = get_ya_code_of_speach(lang_code)

        response = requests.post(
            YANDEX_API_ENDPOINT,
            headers={
                "Authorization": f"Bearer {YANDEX_API_TOKEN}"
            },
            data={
                "text": text,
                "voice": ya_speaker,
                "speed": 1.2,
                "format": "oggopus",
                'folderId': 'b1g1o8strsir61qnc8nj',
                "sampleRateHertz": 48000
            }
        )
        # print(text)
        # print(response.text)
    except Exception as e:
        print(e)
        return 'Sorry, an error occurred while voices your message.'

    # Send the audio file to Telegram chat
    audio_file = open("audio.ogg", "wb")
    audio_file.write(response.content)
    audio_file.close()
    #
    audio_data = AudioSegment.from_file(io.BytesIO(response.content), format='ogg')
    audio_file_name = "voice.ogg"
    audio_data.export(audio_file_name, format='ogg')

    # Send voice message to user who sent the original message
    with open(audio_file_name, 'rb') as audio_file:
        bot.send_voice(chat_id=message.from_user.id, voice=audio_file)


def detect_language(text):
    # Make a request to the Language Detection API
    api_url = "https://ws.detectlanguage.com/0.2/detect"
    headers = {'Authorization': 'Bearer 03f8ddd3b9a36cdfdd1231af27edbbb2'}
    data = {'q': text}
    response = requests.post(api_url, headers=headers, data=data)

    # Parse the response and return detected language
    if response.ok:
        lang_code = response.json()['data']['detections'][0]['language']
        confidence = response.json()['data']['detections'][0]['confidence']
        return (lang_code, confidence)
    else:
        return ("Unknown", 0)


def get_first_sentence(text):
    # Extract the first sentence from the text
    first_period = text.find('.')
    first_question = text.find('?')
    first_exclamation = text.find('!')

    sentence_end = min([i for i in [first_period, first_question, first_exclamation] if i != -1])
    if sentence_end == len(text) - 1:
        return text.strip()

    return text[:sentence_end].strip()


def get_ya_code_of_speach(code):
    switcher = {
        "en": "john",
        "de": "lea",
        "kk": "madi",
        "uz": "nigora",
        "ru": "zahar",
    }
    return switcher.get(code, "Invalid code")


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
