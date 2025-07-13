from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Для задания 1
main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Привет")],
    [KeyboardButton(text="Пока")]
], resize_keyboard=True)

# Для задания 2
links = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Новости", url="https://news.google.com/")],
    [InlineKeyboardButton(text="Музыка", url="https://www.youtube.com/music")],
    [InlineKeyboardButton(text="Видео", url="https://www.youtube.com/")]
])

# Для задания 3
dynamic = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Показать больше", callback_data="show_more")]
])

dynamic_extended = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Опция 1", callback_data="option_1")],
    [InlineKeyboardButton(text="Опция 2", callback_data="option_2")]
])
