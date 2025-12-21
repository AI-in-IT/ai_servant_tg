import asyncio
import httpx 
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
load_dotenv()

BOT_TOKEN=os.getenv("BOT_TOKEN")

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    async with httpx.AsyncClient() as client:
        response = await client.get("http://127.0.0.1:8000/start")
        text = response.json()["text"]
    await message.answer(text)



async def main():
    await dp.start_polling(bot)



if __name__ == "__main__":
    asyncio.run(main())