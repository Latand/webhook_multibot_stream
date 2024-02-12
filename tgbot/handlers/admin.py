from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from infrastructure.some_api.api import HearthstoneApi
from tgbot.filters.admin import AdminFilter

admin_router = Router()
admin_router.message.filter(AdminFilter())


@admin_router.message(CommandStart())
async def admin_start(message: Message, hearthstone: HearthstoneApi):
    info = await hearthstone.get_info()
    classes = info["classes"]
    await message.reply(f"Вітаю, адміне!: {classes}")
