import logging

import betterlogging as bl
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from aiogram.webhook.aiohttp_server import (
    SimpleRequestHandler,
    TokenBasedRequestHandler,
    setup_application,
)
from aiohttp import web

from infrastructure.some_api.api import HearthstoneApi
from tgbot.config import Config, load_config
from tgbot.handlers import main_router, routers_list
from tgbot.middlewares.config import ConfigMiddleware
from tgbot.services import broadcaster


async def on_startup(bot: Bot, config: Config):
    await broadcaster.broadcast(bot, config.tg_bot.admin_ids, "Бот був запущений")
    await bot.set_webhook(
        f"{config.webhook.webhook_url}{config.webhook.webhook_main_path}"
    )


def register_global_middlewares(dp: Dispatcher, config: Config, session_pool=None):
    """
    Register global middlewares for the given dispatcher.
    Global middlewares here are the ones that are applied to all the handlers (you specify the type of update)

    :param dp: The dispatcher instance.
    :type dp: Dispatcher
    :param config: The configuration object from the loaded configuration.
    :param session_pool: Optional session pool object for the database using SQLAlchemy.
    :return: None
    """
    middleware_types = [
        ConfigMiddleware(config),
        # DatabaseMiddleware(session_pool),
    ]

    for middleware_type in middleware_types:
        dp.message.outer_middleware(middleware_type)
        dp.callback_query.outer_middleware(middleware_type)


def setup_logging():
    """
    Set up logging configuration for the application.

    This method initializes the logging configuration for the application.
    It sets the log level to INFO and configures a basic colorized log for
    output. The log format includes the filename, line number, log level,
    timestamp, logger name, and log message.

    Returns:
        None

    Example usage:
        setup_logging()
    """
    log_level = logging.INFO
    bl.basic_colorized_config(level=log_level)

    logging.basicConfig(
        level=logging.INFO,
        format="%(filename)s:%(lineno)d #%(levelname)-8s [%(asctime)s] - %(name)s - %(message)s",
    )
    logger = logging.getLogger(__name__)
    logger.info("Starting bot")


def get_storage(config):
    """
    Return storage based on the provided configuration.

    Args:
        config (Config): The configuration object.

    Returns:
        Storage: The storage object based on the configuration.

    """
    if config.tg_bot.use_redis:
        return RedisStorage.from_url(
            config.redis.dsn(),
            key_builder=DefaultKeyBuilder(with_bot_id=True, with_destiny=True),
        )
    else:
        return MemoryStorage()


def main():
    setup_logging()

    config = load_config(".env")
    storage = get_storage(config)
    session = AiohttpSession()
    hearthstone = HearthstoneApi(api_key=config.heartstone.api_key)
    bot_settings = {"session": session, "parse_mode": ParseMode.HTML}
    main_bot = Bot(token=config.tg_bot.token, **bot_settings)

    main_dispatcher = Dispatcher(storage=storage)
    multibot_dispatcher = Dispatcher(storage=storage)

    main_dispatcher.include_routers(main_router)
    multibot_dispatcher.include_routers(*routers_list)

    multibot_dispatcher.workflow_data.update(
        hearthstone=hearthstone,
    )

    register_global_middlewares(multibot_dispatcher, config)
    register_global_middlewares(main_dispatcher, config)

    main_requests_handler = SimpleRequestHandler(
        main_dispatcher,
        main_bot,
    )

    app = web.Application()
    main_requests_handler.register(app, path=config.webhook.webhook_main_path)

    TokenBasedRequestHandler(
        multibot_dispatcher,
        bot_settings=bot_settings,
    ).register(app, path=config.webhook.webhook_other_bots_path)

    main_dispatcher.startup.register(on_startup)
    setup_application(app, main_dispatcher, bot=main_bot, config=config)
    setup_application(app, multibot_dispatcher)
    web.run_app(
        app,
        host=config.webhook.webapp_host,
        port=config.webhook.webapp_port,
    )


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, SystemExit):
        logging.error("Бот був вимкнений!")
