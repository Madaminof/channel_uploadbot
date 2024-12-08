import asyncio
import logging
import json
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties

# Bot tokeningizni kiriting
TOKEN = "7907590797:AAH6yrkSbxeay0KfRuxdwFTpzqY23J9qzKM"

# Dispatcher yaratamiz
dp = Dispatcher()

# Video yuborish uchun o'zgaruvchilar
video_id = None
waiting_for_code = False

# Kino kodi va message_id'larni saqlash uchun fayl nomi
kino_codes_file = "kino_codes.json"

# Kino kodi va message_id ni faylga saqlash
# Kino kodi va message_id ni faylga saqlash
def save_kino_code(kino_code, message_id):
    try:
        # Faylni ochish yoki yaratish
        with open(kino_codes_file, "r+") as file:
            try:
                data = json.load(file)  # Fayldan ma'lumotni o'qish
            except json.JSONDecodeError:  # Agar fayl bo'sh yoki noto'g'ri formatda bo'lsa
                data = {}

            data[kino_code] = message_id
            file.seek(0)
            json.dump(data, file)
    except FileNotFoundError:
        # Fayl mavjud bo'lmasa, yangi fayl yaratib saqlash
        with open(kino_codes_file, "w") as file:
            json.dump({kino_code: message_id}, file)


# Fayldan kino kodi va message_id'larni olish
def get_message_id_from_file(kino_code):
    try:
        with open(kino_codes_file, "r") as file:
            try:
                data = json.load(file)
            except json.JSONDecodeError:
                return None  # Fayl bo'sh yoki noto'g'ri formatda
            return data.get(kino_code)
    except FileNotFoundError:
        return None


# Fayldan kino kodi va message_id'larni olish
def get_message_id_from_file(kino_code):
    try:
        with open(kino_codes_file, "r") as file:
            data = json.load(file)
            return data.get(kino_code)
    except FileNotFoundError:
        return None


@dp.message(Command("start"))
async def command_start_handler(message: Message) -> None:
    """Botga start buyrug‘ini jo‘natganda ishlaydi."""
    await message.answer(
        "Botga xush kelibsiz! Avval video yuboring, keyin esa kino kodi yuborishingizni so'rayman."
    )


@dp.message()
async def handle_video(message: Message) -> None:
    """Video yuborish uchun handler."""
    global video_id, waiting_for_code

    if message.video:
        # Foydalanuvchi video yuborgan bo'lsa
        video_id = message.video.file_id
        waiting_for_code = True
        await message.answer("Kino kodi yuboring.")
    elif waiting_for_code:
        # Kino kodi yuborilsa, video va kodi kanalga yuboriladi
        caption = message.text.strip()
        if video_id:
            sent_message = await message.bot.send_video(
                chat_id='@kinotopbot01',
                video=video_id,
                caption=f"Kino kodi: {caption}"
            )
            # Kino kodi va message_id ni faylga saqlash
            save_kino_code(caption, sent_message.message_id)

            await message.answer(f"Video va kino kodi kanalga yuborildi. Message ID: {sent_message.message_id}")
            # Video va kod yuborilganidan so'ng, navbatni tozalash
            video_id = None
            waiting_for_code = False
        else:
            await message.answer("Iltimos, avval video yuboring.")
    else:
        await message.answer("Avval video yuboring, so'ngra kino kodi yuborishingizni kutyapman.")


async def main():
    logging.basicConfig(level=logging.INFO)

    # Bot obyektini to'g'ri konfiguratsiya qilamiz
    bot = Bot(
        token=TOKEN,
        session=AiohttpSession(),
        default=DefaultBotProperties(parse_mode="HTML")  # Yangi usulda parse_mode
    )

    # Start polling
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
