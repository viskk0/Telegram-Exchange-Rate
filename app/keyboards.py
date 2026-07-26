from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

MainKeyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="💲Получить курс доллара!"), KeyboardButton(text="🪙Получить курс рубля!")],
    [KeyboardButton(text="₸Получить курс тенге!"), KeyboardButton(text='💶Получить курс евро!')],
    [KeyboardButton(text="🛠️Подписка")]
], resize_keyboard=True)

subscribeKeyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="💎Купить Premium! (⭐99)", callback_data="buySubscribe")]
])