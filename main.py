import telebot
from telebot import types
from flask import Flask
from threading import Thread

# --- RENDER UCHUN UYG'OQ SAQLASH QISMI ---
app = Flask('')


@app.route('/')
def home():
    return "Bot is alive!"


def run():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run)
    t.start()


# ---------------------------------------

TOKEN = "8252262081:AAHeR1h5eiytPH1-q2GWJK8-dfRRdEo7bBE"
ADMIN_ID = 7081992826
bot = telebot.TeleBot(TOKEN)

# MAHSULOTLAR (Narxi va turi bilan)
PRODUCTS = {
    'Burgerlar': {
        'CheeseBurger': 35000,
        'ChickenBurger': 30000,
        'BigBurger': 45000
    },
    'Ichimliklar': {
        'Coca-Cola 0.5': 10000,
        'Fanta 0.5': 10000,
        'Suv': 4000
    }
}

user_data = {}
user_language = {}
user_cart = {}  # Savatni saqlash: {chat_id: {mahsulot: soni}}


def main_keyboard(lang):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == 'UZ':
        keyboard.add("📝 Menu", "🛒 Savat")
        keyboard.add("📞 Aloqa")
    else:
        keyboard.add("📝 Меню", "🛒 Корзина")
        keyboard.add("📞 Контакты")
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add("🇺🇿 O‘zbekcha", "🇷🇺 Русский")
    bot.send_message(message.chat.id, "Tilni tanlang / Выберите язык:", reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text in ["🇺🇿 O‘zbekcha", "🇷🇺 Русский"])
def set_language(message):
    lang = 'UZ' if "O‘zbekcha" in message.text else 'RU'
    user_language[message.chat.id] = lang
    msg = "Menuni tanlang 👇" if lang == 'UZ' else "Выберите меню 👇"
    bot.send_message(message.chat.id, msg, reply_markup=main_keyboard(lang))


# MENU (Kategoriyalar)
@bot.message_handler(func=lambda message: message.text in ["📝 Menu", "📝 Меню"])
def show_categories(message):
    lang = user_language.get(message.chat.id, 'UZ')
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for cat in PRODUCTS.keys():
        keyboard.add(cat)
    keyboard.add("⬅️" if lang == 'UZ' else "⬅️ Назад")
    bot.send_message(message.chat.id, "Kategoriyani tanlang:" if lang == 'UZ' else "Выберите категорию:",
                     reply_markup=keyboard)


# MAHSULOTLARNI KO'RSATISH
@bot.message_handler(func=lambda message: message.text in PRODUCTS.keys())
def show_products(message):
    category = message.text
    lang = user_language.get(message.chat.id, 'UZ')
    keyboard = types.InlineKeyboardMarkup()

    for item, price in PRODUCTS[category].items():
        keyboard.add(types.InlineKeyboardButton(text=f"{item} - {price} so'm", callback_data=f"buy_{item}"))

    bot.send_message(message.chat.id, f"{category}:", reply_markup=keyboard)


# SAVATGA QO'SHISH (Inline tugma bosilganda)
@bot.callback_query_handler(func=lambda call: call.data.startswith('buy_'))
def add_to_cart(call):
    item = call.data.replace('buy_', '')
    chat_id = call.message.chat.id

    if chat_id not in user_cart:
        user_cart[chat_id] = {}

    user_cart[chat_id][item] = user_cart[chat_id].get(item, 0) + 1
    bot.answer_callback_query(call.id, f"{item} savatga qo'shildi!")


# SAVATNI KO'RSATISH VA BUYURTMA
@bot.message_handler(func=lambda message: message.text in ["🛒 Savat", "🛒 Корзина"])
def show_cart(message):
    chat_id = message.chat.id
    lang = user_language.get(chat_id, 'UZ')
    cart = user_cart.get(chat_id, {})

    if not cart:
        bot.send_message(chat_id, "Savat bo'sh" if lang == 'UZ' else "Корзина пуста")
        return

    text = "🛒 Savat / Корзина:\n\n"
    total = 0
    for item, count in cart.items():
        price = 0
        for cat in PRODUCTS.values():
            if item in cat: price = cat[item]
        summa = price * count
        total += summa
        text += f"🔹 {item}: {count} dona = {summa} so'm\n"

    text += f"\n💰 Jami: {total} so'm"

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("✅ Buyurtmani tasdiqlash" if lang == 'UZ' else "✅ Подтвердить заказ")
    keyboard.add("🗑 Tozalash" if lang == 'UZ' else "🗑 Очистить")
    keyboard.add("⬅️" if lang == 'UZ' else "⬅️ Наzad")

    bot.send_message(chat_id, text, reply_markup=keyboard)


# TASDIQLASH (Ism va Kontakt so'rash qismi sizniki kabi davom etadi...)
# Bu yerga ism va telefon so'rash funksiyalarini qo'shishingiz mumkin.

keep_alive()  # Render'da uyg'oq turish uchun
bot.polling(none_stop=True)
