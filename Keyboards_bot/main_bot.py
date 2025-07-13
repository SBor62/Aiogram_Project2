import logging
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram import F
from aiogram.types import Message, CallbackQuery
import keyboards as kb
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(
    token="BOT TOKEN",  # Замените на реальный токен
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Обработчик команды /start (Задание 1)
@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(f"Привет!", reply_markup=kb.main)


@dp.message(F.text == "Привет")
async def hello_button(message: Message):
    await message.answer(f"Привет, {message.from_user.first_name}!")


@dp.message(F.text == "Пока")
async def bye_button(message: Message):
    await message.answer(f"До свидания, {message.from_user.first_name}!")


# Обработчик команды /links (Задание 2)
@dp.message(Command("links"))
async def links_command(message: Message):
    await message.answer("Выберите категорию:", reply_markup=kb.links)


# Обработчик команды /dynamic (Задание 3)
@dp.message(Command("dynamic"))
async def dynamic_command(message: Message):
    await message.answer("Динамическое меню:", reply_markup=kb.dynamic)


# Обработчик callback-запросов для динамического меню
@dp.callback_query(F.data == "show_more")
async def show_more_callback(callback: CallbackQuery):
    await callback.message.edit_text("Выберите опцию:", reply_markup=kb.dynamic_extended)
    await callback.answer()


@dp.callback_query(F.data.startswith("option_"))
async def option_callback(callback: CallbackQuery):
    option = callback.data.split("_")[1]
    await callback.message.answer(f"Вы выбрали Опцию {option}")
    await callback.answer()


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
