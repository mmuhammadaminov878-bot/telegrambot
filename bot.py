import telebot
from telebot import types

TOKEN = "8252262081:AAHeR1h5eiytPH1-q2GWJK8-dfRRdEo7bBE"  # BotFather'dan olgan token
ADMIN_ID = 7081992826  # Sizning Telegram ID

bot = telebot.TeleBot(TOKEN)
user_data = {}
user_language = {}  # foydalanuvchi tilini saqlash uchun


# Til tanlash tugmalari
def language_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("🇺🇿 O‘zbekcha", "🇷🇺 Русский")
    return keyboard


# Buyurtma va aloqa tugmalari tilga qarab
def main_keyboard(lang):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == 'UZ':
        keyboard.add("📝 Buyurtma berish", "📞 Aloqa")
    else:
        keyboard.add("📝 Сделать заказ", "📞 Контакты")
    return keyboard


# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Tilni tanlang / Выберите язык:", reply_markup=language_keyboard())


# Tilni saqlash
@bot.message_handler(func=lambda message: message.text in ["🇺🇿 O‘zbekcha", "🇷🇺 Русский"])
def set_language(message):
    if message.text == "🇺🇿 O‘zbekcha":
        user_language[message.chat.id] = 'UZ'
        bot.send_message(message.chat.id, "Assalomu alaykum! Buyurtma berish uchun tugmani bosing 👇",
                         reply_markup=main_keyboard('UZ'))
    else:
        user_language[message.chat.id] = 'RU'
        bot.send_message(message.chat.id, "Здравствуйте! Чтобы сделать заказ, нажмите кнопку 👇",
                         reply_markup=main_keyboard('RU'))


# Buyurtma boshlash
@bot.message_handler(
    func=lambda message: message.chat.id in user_language and message.text in ["📝 Buyurtma berish", "📝 Сделать заказ"])
def order_start(message):
    lang = user_language[message.chat.id]
    if lang == 'UZ':
        bot.send_message(message.chat.id, "Ismingizni kiriting:")
    else:
        bot.send_message(message.chat.id, "Введите ваше имя:")
    user_data[message.chat.id] = {}


# Ismni olish
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'name' not in user_data[message.chat.id])
def get_name(message):
    user_data[message.chat.id]['name'] = message.text
    lang = user_language[message.chat.id]
    if lang == 'UZ':
        bot.send_message(message.chat.id, "Telefon raqam yoki Telegram username kiriting:")
    else:
        bot.send_message(message.chat.id, "Введите телефон или Telegram username:")


# Kontaktni olish
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'contact' not in user_data[message.chat.id])
def get_contact(message):
    user_data[message.chat.id]['contact'] = message.text
    lang = user_language[message.chat.id]
    if lang == 'UZ':
        bot.send_message(message.chat.id, "Buyurtma matnini yozing:")
    else:
        bot.send_message(message.chat.id, "Введите текст заказа:")


# Buyurtmani olish va adminga yuborish
@bot.message_handler(func=lambda message: message.chat.id in user_data and 'order' not in user_data[message.chat.id])
def get_order(message):
    user_data[message.chat.id]['order'] = message.text

    data = user_data[message.chat.id]
    text = (
        "📦 YANGI BUYURTMA / НОВЫЙ ЗАКАЗ\n\n"
        f"👤 Ism / Имя: {data['name']}\n"
        f"📞 Aloqa / Контакты: {data['contact']}\n"
        f"📝 Buyurtma / Заказ: {data['order']}"
    )

    bot.send_message(ADMIN_ID, text)

    lang = user_language[message.chat.id]
    if lang == 'UZ':
        bot.send_message(message.chat.id, "✅ Buyurtmangiz qabul qilindi! Tez orada bog‘lanamiz.")
    else:
        bot.send_message(message.chat.id, "✅ Ваш заказ принят! Мы свяжемся с вами в ближайшее время.")

    user_data.pop(message.chat.id)


# Aloqa tugmasi
@bot.message_handler(
    func=lambda message: message.chat.id in user_language and message.text in ["📞 Aloqa", "📞 Контакты"])
def contact(message):
    lang = user_language[message.chat.id]
    if lang == 'UZ':
        bot.send_message(message.chat.id, "📲 Aloqa: +998885707565")
    else:
        bot.send_message(message.chat.id, "📲 Контакты: +998885707565")


bot.polling()

