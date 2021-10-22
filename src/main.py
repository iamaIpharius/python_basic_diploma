import telebot
import requests
from decouple import config
TOKEN = config('TOKEN')

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "( ͡° ͜ʖ ͡°)")


@bot.message_handler(commands=['helloworld'])
def send_welcome(message):
    bot.reply_to(message, "Hello, World!")


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if 'привет' in message.text.lower():

        bot.send_message(message.from_user.id,
                         "Привет, тебя приветствует бот компании Too Easy Travel! Чем я могу помочь?")

    else:
        bot.send_message(message.from_user.id,
                         "Прости, не понимаю тебя. Попробуй написать снова или воспользуйся командами.")


bot.infinity_polling()
