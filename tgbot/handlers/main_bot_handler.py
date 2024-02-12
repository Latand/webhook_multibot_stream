from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from tgbot.config import Config
from tgbot.misc.check_bot_token import is_bot_token

main_router = Router()


@main_router.message(Command("add", magic=F.args.func(is_bot_token)))
async def command_add_bot(
    message: Message, command: CommandObject, bot: Bot, config: Config
):
    new_bot = Bot(token=command.args, session=bot.session)
    try:
        bot_user = await new_bot.get_me()
    except TelegramUnauthorizedError:
        return message.answer("Invalid token")
    await new_bot.delete_webhook()
    other_bot_path = config.webhook.webhook_other_bots_path.format(
        bot_token=command.args
    )
    await new_bot.set_webhook(f"{config.webhook.webhook_url}{other_bot_path}")
    return await message.answer(f"Bot @{bot_user.username} successfuly added")
