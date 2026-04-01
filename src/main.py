import asyncio
import sys
from pathlib import Path
import httpx
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
sys.path.append(str(Path(__file__).parent.parent))
from src.config import settings
from src.text.tg_message import tg_message
bot = Bot(token=settings.BOT_TOKEN)

dp = Dispatcher()

base_url_backend = settings.BASE_URL_BACKEND

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(tg_message["rus"]["welcome"])

@dp.message(Command("reg"))
async def registration(message: Message):
    url = base_url_backend+"/users/"
    data = {  "tg_id": str(message.from_user.id), "name": str(message.from_user.first_name), "active": True}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, json = data)
            response.raise_for_status()
            await message.answer(tg_message["rus"]["registration"]["success"])
    except Exception:    
            await message.answer(tg_message["rus"]["registration"]["error"])
    

@dp.message(Command("create_family"))
async def create_family(message: Message):
    url = base_url_backend+"/families/"
    data = {  "title": str(message.from_user.last_name), "active": True}
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, json = data)
            response.raise_for_status()
            result = response.json()
            family_key = result["data"]["key"]
            await message.answer(tg_message["rus"]["create_family"]["success"])
            await message.answer(str(family_key))
    except Exception:    
            await message.answer(tg_message["rus"]["create_family"]["error"])

@dp.message(Command("joine_family"))
async def start(message: Message):
    # async with httpx.AsyncClient() as client:
        # response = await client.get("http://127.0.0.1:8000/start")
        # text = response.json()["text"]
    await message.answer(str(message.from_user.id))
    await message.answer(str(message.from_user.first_name))

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Бот запущен")
    asyncio.run(main())
