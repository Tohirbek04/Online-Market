import logging
import os
from random import randint

import django
import telebot
from telebot.types import KeyboardButton, ReplyKeyboardMarkup

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'root.settings')
django.setup()
from django.core.cache import cache

from users.models import User

API_TOKEN = '7408932603:AAGFHD_5RgTCOPo2RWBygz6E-AUktzEho6Y'
logging.basicConfig(level=logging.INFO)

bot = telebot.TeleBot(API_TOKEN)


def get_code(obj):
    code = randint(100000, 999000)
    while cache.get(code):
        code = randint(100000, 999000)
    cache.set(code, obj.phone, timeout=60)
    return code


@bot.message_handler(commands=['start'])
def send_welcome(message):
    text = f"""
Salom {message.from_user.first_name} 👋
@aAlijahon'ning rasmiy botiga xush kelibsiz

⬇ Kontaktingizni yuboring (tugmani bosib)"""
    rkm = ReplyKeyboardMarkup()
    rkm.add(KeyboardButton('☎ Kontaktni yuborish', request_contact=True))
    bot.send_message(message.chat.id, text, reply_markup=rkm)


@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    logging.info(f"Received contact: {message.contact}")
    phone_number = message.contact.phone_number[-9:]
    obj, created = User.objects.get_or_create(phone=phone_number)
    obj.first_name = message.from_user.first_name
    obj.telegram_id = message.from_user.id
    obj.save()
    code = get_code(obj)
    text = f"""🔒 Kodingiz: \n```{code}```"""
    bot.send_message(message.chat.id, text, parse_mode='MarkdownV2')
    text = """🔑 Yangi kod olish uchun /login ni bosing"""
    bot.send_message(message.chat.id, text)

bot.infinity_polling()
