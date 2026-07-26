from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

MainKeyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="💲Получить курс доллара!"), KeyboardButton(text="🪙Получить курс рубля!")],
    [KeyboardButton(text="₸Получить курс тенге!"), KeyboardButton(text='💶Получить курс евро!')]
], resize_keyboard=True)