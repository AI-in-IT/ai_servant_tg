import asyncio
import sys
from pathlib import Path
import httpx
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
sys.path.append(str(Path(__file__).parent.parent))
from src.config import settings

bot = Bot(token=settings.BOT_TOKEN)

dp = Dispatcher()


@dp.message(Command("start"))
async def start(message: Message):
    # async with httpx.AsyncClient() as client:
        # response = await client.get("http://127.0.0.1:8000/start")
        # text = response.json()["text"]
    await message.answer(str(message.from_user.id))
    await message.answer(str(message.from_user.first_name))


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
