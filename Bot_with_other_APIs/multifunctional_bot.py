import asyncio
import requests
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
import random

# Конфигурация (замените на свои ключи)
from config import (
    TOKEN,
    OPENWEATHER_API_KEY,
    NEWS_API_KEY,
    NASA_API_KEY,
    THE_CAT_API_KEY
)

bot = Bot(token=TOKEN)
dp = Dispatcher()


# Состояния для FSM (Finite State Machine)
class WeatherState(StatesGroup):
    waiting_for_city = State()


# Клавиатура с основными функциями
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌤 Погода"), KeyboardButton(text="📰 Новости")],
        [KeyboardButton(text="🐱 Факт о кошках"), KeyboardButton(text="🪐 Космическое фото")],
        [KeyboardButton(text="ℹ️ Помощь")]
    ],
    resize_keyboard=True
)


# ========== Функции для работы с API ==========

# 1. Функция для получения погоды
async def get_weather(city: str):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric&lang=ru"
    response = requests.get(url)
    data = response.json()

    if data.get("cod") != 200:
        return None

    weather = {
        "city": data["name"],
        "temp": round(data["main"]["temp"]),
        "feels_like": round(data["main"]["feels_like"]),
        "description": data["weather"][0]["description"].capitalize(),
        "humidity": data["main"]["humidity"],
        "wind": data["wind"]["speed"]
    }
    return weather


# 2. Функция для получения новостей
async def get_news(topic="technology"):
    url = f"https://newsapi.org/v2/top-headlines?category={topic}&apiKey={NEWS_API_KEY}&pageSize=5"
    response = requests.get(url)
    data = response.json()

    if data["status"] != "ok" or not data["articles"]:
        return None

    articles = []
    for article in data["articles"]:
        articles.append({
            "title": article["title"],
            "url": article["url"],
            "source": article["source"]["name"]
        })
    return articles


# 3. Функция для получения фактов о кошках
async def get_cat_fact():
    url = "https://catfact.ninja/fact"
    response = requests.get(url)
    data = response.json()
    return data.get("fact")


# 4. Функция для получения космического фото дня от NASA
async def get_nasa_apod(random_date=False):
    if random_date:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * 5)  # 5 лет назад
        random_date = start_date + (end_date - start_date) * random.random()
        date_str = random_date.strftime("%Y-%m-%d")
        url = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}&date={date_str}'
    else:
        url = f'https://api.nasa.gov/planetary/apod?api_key={NASA_API_KEY}'

    response = requests.get(url)
    data = response.json()

    if "url" not in data:
        return None

    return {
        "url": data["url"],
        "title": data.get("title", "Без названия"),
        "explanation": data.get("explanation", "Описание отсутствует"),
        "date": data.get("date", "Дата неизвестна")
    }


# ========== Обработчики сообщений ==========

@dp.message(Command("start"))
async def start_command(message: types.Message):
    await message.answer(
        "👋 Привет! Я многофункциональный бот. Выбери что тебе интересно:",
        reply_markup=main_keyboard
    )


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "ℹ️ Доступные команды:\n\n"
        "/start - начать работу с ботом\n"
        "/weather <город> - узнать погоду\n"
        "/news - последние новости технологий\n"
        "/cat - случайный факт о кошках\n"
        "/space - космическое фото дня\n\n"
        "Или используйте кнопки меню",
        reply_markup=main_keyboard
    )


@dp.message(lambda message: message.text == "ℹ️ Помощь")
async def help_button(message: types.Message):
    await help_command(message)


@dp.message(Command("weather"))
@dp.message(lambda message: message.text == "🌤 Погода")
async def weather_handler(message: types.Message, state: FSMContext):
    # Если команда /weather с аргументом
    if message.text.startswith("/weather"):
        city = message.text.replace("/weather", "").strip()
        if not city:
            await message.answer("Пожалуйста, укажите город: /weather <город>")
            return

        weather = await get_weather(city)
        if not weather:
            await message.answer("Не удалось получить данные о погоде. Проверьте название города.")
            return

        response = (
            f"🌤 Погода в {weather['city']}:\n"
            f"🌡 Температура: {weather['temp']}°C (ощущается как {weather['feels_like']}°C)\n"
            f"📝 {weather['description']}\n"
            f"💧 Влажность: {weather['humidity']}%\n"
            f"🌬 Ветер: {weather['wind']} м/с"
        )
        await message.answer(response)
    else:
        await message.answer("Введите название города:")
        await state.set_state(WeatherState.waiting_for_city)


@dp.message(WeatherState.waiting_for_city)
async def process_city(message: types.Message, state: FSMContext):
    city = message.text
    weather = await get_weather(city)

    if not weather:
        await message.answer("Не удалось получить данные о погоде. Проверьте название города.")
        await state.clear()
        return

    response = (
        f"🌤 Погода в {weather['city']}:\n"
        f"🌡 Температура: {weather['temp']}°C (ощущается как {weather['feels_like']}°C)\n"
        f"📝 {weather['description']}\n"
        f"💧 Влажность: {weather['humidity']}%\n"
        f"🌬 Ветер: {weather['wind']} м/с"
    )
    await message.answer(response, reply_markup=main_keyboard)
    await state.clear()


@dp.message(Command("news"))
@dp.message(lambda message: message.text == "📰 Новости")
async def news_handler(message: types.Message):
    await message.answer("🔄 Получаю последние новости...")

    news = await get_news()
    if not news:
        await message.answer("Не удалось получить новости. Попробуйте позже.")
        return

    response = "📰 Последние новости технологий:\n\n"
    for i, article in enumerate(news, 1):
        response += f"{i}. {article['title']}\n{article['url']}\n\n"

    await message.answer(response[:4000])  # Ограничение Telegram на длину сообщения


@dp.message(Command("cat"))
@dp.message(lambda message: message.text == "🐱 Факт о кошках")
async def cat_handler(message: types.Message):
    fact = await get_cat_fact()
    if not fact:
        await message.answer("Не удалось получить факт о кошках. Попробуйте позже.")
        return

    await message.answer(f"🐱 Интересный факт о кошках:\n\n{fact}")


@dp.message(Command("space"))
@dp.message(lambda message: message.text == "🪐 Космическое фото")
async def space_handler(message: types.Message):
    await message.answer("🔄 Получаю космическое фото...")

    apod = await get_nasa_apod(random_date=True)
    if not apod:
        await message.answer("Не удалось получить фото. Попробуйте позже.")
        return

    caption = (
        f"🪐 {apod['title']}\n"
        f"📅 {apod['date']}\n\n"
        f"{apod['explanation'][:1000]}..."  # Обрезаем длинное описание
    )

    try:
        if apod['url'].endswith(('.jpg', '.jpeg', '.png')):
            await message.answer_photo(apod['url'], caption=caption)
        else:  # Если это видео (YouTube)
            await message.answer(f"{apod['title']}\n\n{caption}\n\nСсылка: {apod['url']}")
    except Exception as e:
        await message.answer(f"Не удалось отправить фото. Вот ссылка: {apod['url']}")


# Обработчик неизвестных команд
@dp.message()
async def unknown_message(message: types.Message):
    await message.answer("Я не понял ваш запрос. Используйте кнопки меню или команду /help", reply_markup=main_keyboard)


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
