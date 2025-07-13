import logging
import sqlite3
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Инициализация бота
bot = Bot(
    token="7949255195:AAFrfEYQVe2oCHpO5mxgvLYjBqEwqZZdWT4",  # Замените на реальный токен
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

storage = MemoryStorage()
dp = Dispatcher(storage=storage)


# Определение состояний (FSM)
class StudentForm(StatesGroup):
    name = State()
    age = State()
    grade = State()


# Обработчик команды /start
@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я бот для записи данных учеников.\n"
        "Введи /add, чтобы добавить нового ученика."
    )


# Обработчик команды /add
@dp.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    await state.set_state(StudentForm.name)
    await message.answer("Введите имя ученика:")


# Обработчик ввода имени
@dp.message(StudentForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(StudentForm.age)
    await message.answer("Введите возраст ученика:")


# Обработчик ввода возраста
@dp.message(StudentForm.age)
async def process_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть числом! Попробуйте снова:")
        return

    await state.update_data(age=int(message.text))
    await state.set_state(StudentForm.grade)
    await message.answer("Введите класс ученика (например, 10А):")


# Обработчик ввода класса и сохранение в БД
@dp.message(StudentForm.grade)
async def process_grade(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data.get("name")
    age = data.get("age")
    grade = message.text

    # Сохраняем данные в базу
    conn = sqlite3.connect("school_data.db")
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO students (name, age, grade) VALUES (?, ?, ?)",
        (name, age, grade)
    )

    conn.commit()
    conn.close()

    await state.clear()
    await message.answer("Данные ученика успешно сохранены!")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
