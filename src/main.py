import asyncio
import sys
from pathlib import Path
import httpx
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import BotCommand

sys.path.append(str(Path(__file__).parent.parent))
from src.config import settings
from src.text.tg_message import tg_message

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()
base_url_backend = settings.BASE_URL_BACKEND

class JoinFamilyStates(StatesGroup):
    """Машина состояний для получения ключа семьи"""
    waiting_for_key = State()

async def call_api(method: str, path: str, json_data: dict | None = None) -> dict:
    """Делает запрос к бэку. Возвращает {"ok": bool, "data": dict|None, "error": str|None}"""
    try:
        async with httpx.AsyncClient(base_url=base_url_backend) as client:
            response = await client.request(method, path, json=json_data)
            response.raise_for_status()
            return {"ok": True, "body": response.json(), "error": None}
            
    except httpx.HTTPStatusError as e:
        try:
            detail = e.response.json().get("detail", f"Ошибка {e.response.status_code}")
        except Exception:
            detail = f"HTTP ошибка {e.response.status_code}"
        return {"ok": False, "data": None, "error": detail}
        
    except Exception as e:
        return {"ok": False, "data": None, "error": f"Ошибка соединения: {str(e)}"}






@dp.message(Command("info"))
async def cmd_info(message: Message):
    help_text = (
        "<b>Доступные команды:</b>\n\n"
        "/start — Приветствие\n"
        "/reg — Регистрация\n"
        "/unreg — Удаление профиля\n"
        "/create_family — Создание семьи\n"
        "/delete_family — Удаление семьи\n"
        "/joine_family — Вступление в семью\n"
        "/leave_family — Покидание семьи\n"
        "/info — Показ всех команд"
    )
    await message.answer(help_text, parse_mode="HTML")

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer(tg_message["rus"]["welcome"])


@dp.message(Command("reg"))
async def reg(message: Message):
    res = await call_api("POST", "/users/registration", {
        "tg_id": message.from_user.id,
        "name": message.from_user.first_name or "Пользователь",
        "active": True
    })
    if not res["ok"]:
        await message.answer(f"❌ {res['error']}")
        return
    await message.answer(tg_message["rus"]["registration"]["success"])

@dp.message(Command("unreg"))
async def unreg(message: Message):
    res = await call_api("DELETE", f"/users/unregistration/{message.from_user.id}")
    if not res["ok"]:
        await message.answer(f"❌ {res['error']}")
        return
    await message.answer(tg_message["rus"]["unregistration"]["success"])


@dp.message(Command("create_family"))
async def cmd_create_family(message: Message):
    family_res = await call_api("POST", "/families/", {
        "title": message.from_user.last_name,
        "active": True
    })
    if not family_res["ok"]:
        await message.answer(f"❌ {family_res['error']}")
        return
    user_res = await call_api("GET", f"/users/{message.from_user.id}")
    if not user_res["ok"]:
        await message.answer(f"❌ {user_res['error']}")
        return

    join_res = await call_api("PUT", f"/families/{family_res['body']['data']['id']}/join/user/{user_res['body']['data']['id']}", {
        "key": family_res['body']["data"]["key"]
    })
    if not join_res["ok"]:
        await message.answer(f"❌ {join_res['error']}")
        return

    await message.answer(tg_message["rus"]["create_family"]["success"])
    await message.answer(f"Давай станем семьей в @AI_Servant_bot_bot\nКлюч от нашей семьи <code>{family_res['body']['data']['key']}</code>", parse_mode="HTML")


@dp.message(Command("delete_family"))
async def cmd_delete_family(message: Message):
    user_res = await call_api("GET", f"/users/{message.from_user.id}")
    if not user_res["ok"]:
        await message.answer(f"❌ {user_res['error']}")
        return

    family_id = user_res['body']["data"].get("family_id")
    if not family_id:
        await message.answer("❌ Вы не состоите в семье.")
        return

    res = await call_api("DELETE", f"/families/{family_id}")
    if not res["ok"]:
        await message.answer(f"❌ {res['error']}")
        return

    await message.answer(tg_message["rus"]["delete_my_family"]["success"])


@dp.message(Command("joine_family"))
async def cmd_join_start(message: Message, state: FSMContext):
    user_res = await call_api("GET", f"/users/{message.from_user.id}")
    if not user_res["ok"]:
        await message.answer(f"❌ {user_res['error']}")
        return
    await message.answer("Вставьте ключ от семьи:")
    await state.set_state(JoinFamilyStates.waiting_for_key)


@dp.message(JoinFamilyStates.waiting_for_key)
async def cmd_join_process(message: Message, state: FSMContext):
    family_key = message.text.strip()
    if not family_key:
        await message.answer("❌ Ключ не может быть пустым. Введите его ещё раз:")
        return
    
    try:
        family_res = await call_api("GET", f"/families/key/{family_key}")
        if not family_res["ok"]:
            await message.answer(f"❌ {family_res['error']}")
            return

        user_res = await call_api("GET", f"/users/{message.from_user.id}")
        if not user_res["ok"]:
            await message.answer(f"❌ {user_res['error']}")
            return

        join_res = await call_api("PUT", f"/families/{family_res['body']['data']['id']}/join/user/{user_res['body']['data']['id']}", {
            "key": family_key
        })
        if not join_res["ok"]:
            await message.answer(f"❌ {join_res['error']}")
            return

        await message.answer(tg_message["rus"]["join_family"]["success"])
    finally:
        await state.clear()  


@dp.message(Command("leave_family"))
async def cmd_leave_family(message: Message):
    user_res = await call_api("GET", f"/users/{message.from_user.id}")
    if not user_res["ok"]:
        await message.answer(f"❌ {user_res['error']}")
        return

    family_id = user_res['body']["data"].get("family_id")
    user_id = user_res['body']["data"].get("id")
    
    if not family_id:
        await message.answer("❌ Вы не состоите в семье.")
        return

    res = await call_api("DELETE", f"/families/{family_id}/remove/user/{user_id}")
    if not res["ok"]:
        await message.answer(f"❌ {res['error']}")
        return

    await message.answer(tg_message["rus"]["leave_family"]["success"])


async def main():
    await bot.set_my_commands([
        # BotCommand(command="start", description="Приветствие"),
        BotCommand(command="reg", description="Регистрация"),
        # BotCommand(command="unreg", description="Удалить профиль"),
        BotCommand(command="create_family", description="Создать семью"),
        # BotCommand(command="delete_family", description="Удалить семью"),
        BotCommand(command="joine_family", description="Вступить по ключу"),
        # BotCommand(command="leave_family", description="Покинуть семью"),
        BotCommand(command="info", description="Справка по всем командам"),
    ])
    await dp.start_polling(bot)

if __name__ == "__main__":
    print("Бот запущен")
    asyncio.run(main())









