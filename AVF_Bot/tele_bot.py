import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import FSInputFile, BufferedInputFile, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from gtts import gTTS
from deep_translator import GoogleTranslator

# Настройки бота
API_TOKEN = '7781870968:AAFNkoMBhjAEitX_Dgqv5MwEKlD1RbtDLs4'
IMG_FOLDER = 'img'
AUDIO_FOLDER = 'audio'

# Создаем папки, если их нет
os.makedirs(IMG_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


def get_main_keyboard():
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="/help"),
        KeyboardButton(text="/voice"),
        KeyboardButton(text="/translate"),
    )
    return builder.as_markup(resize_keyboard=True)


@dp.message(Command("start"))
async def start_command(message: types.Message):
    keyboard = get_main_keyboard()
    await message.answer(
        f"Привет {message.from_user.first_name}! Я бот с несколькими функциями:\n"
        "1. Сохраняю все присланные фото\n"
        "2. Могу преобразовать текст в голосовое сообщение (/voice текст)\n"
        "3. Перевожу текст на английский\n\n"
        "Используй кнопки ниже или команды для взаимодействия!",
        reply_markup=keyboard
    )


@dp.message(Command("help"))
async def help_command(message: types.Message):
    await message.answer(
        "Доступные команды:\n"
        "/start - начать работу с ботом\n"
        "/help - показать это сообщение\n"
        "/voice текст - преобразовать текст в голосовое сообщение\n"
        "/translate текст - перевести текст на английский\n\n"
        "Просто отправь фото, и я его сохраню!\n"
        "Отправь любой текст, и я переведу его на английский!"
    )


@dp.message(lambda message: message.photo)
async def save_photo(message: types.Message):
    """Сохраняет фото в папку img"""
    try:
        photo = message.photo[-1]
        file_id = photo.file_id
        file = await bot.get_file(file_id)
        file_path = os.path.join(IMG_FOLDER, f"{file_id}.jpg")

        # Скачиваем файл
        file_bytes = await bot.download_file(file.file_path)

        # Сохраняем на диск
        with open(file_path, 'wb') as f:
            f.write(file_bytes.read())

        await message.reply(f"Фото успешно сохранено как {file_path}")
    except Exception as e:
        await message.reply(f"Ошибка при сохранении фото: {str(e)}")


@dp.message(Command("voice"))
async def send_voice_message(message: types.Message):
    """Отправляет голосовое сообщение"""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Укажите текст после /voice\nНапример: /voice Привет, как дела?")
        return

    text = parts[1]
    try:
        tts = gTTS(text=text, lang='ru')
        audio_path = os.path.join(AUDIO_FOLDER, f"{message.message_id}.mp3")
        tts.save(audio_path)

        # Создаем объект файла для отправки
        voice = FSInputFile(audio_path)

        # Отправляем голосовое сообщение
        await message.reply_voice(voice)

        # Удаляем временный файл
        os.remove(audio_path)
    except Exception as e:
        await message.reply(f"Ошибка при создании голосового сообщения: {str(e)}")


@dp.message(Command("translate"))
async def translate_command(message: types.Message):
    """Переводит текст на английский по команде"""
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        await message.reply("Укажите текст после /translate\nНапример: /translate Привет, мир!")
        return

    text = parts[1]
    await translate_text(message, text)


@dp.message()
async def handle_text(message: types.Message):
    """Обработка текстовых сообщений"""
    # Если это не команда, переводим текст
    if not message.text.startswith('/'):
        await translate_text(message, message.text)


async def translate_text(message: types.Message, text: str):
    """Переводит текст на английский"""
    try:
        translation = GoogleTranslator(source='auto', target='en').translate(text)
        await message.reply(f"Перевод на английский:\n{translation}")
    except Exception as e:
        await message.reply(f"Ошибка перевода: {str(e)}")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
