from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    """
    Creates the TgBot object from environment variables.
    """

    token: str
    admin_ids: list[int]
    use_redis: bool

    @staticmethod
    def from_env(env: Env):
        """
        Creates the TgBot object from environment variables.
        """
        token = env.str("BOT_TOKEN")
        admin_ids = env.list("ADMINS", subcast=int)
        use_redis = env.bool("USE_REDIS")
        return TgBot(token=token, admin_ids=admin_ids, use_redis=use_redis)


@dataclass
class WebhookConfig:
    webhook_url: str
    webhook_main_path: str
    webhook_other_bots_path: str
    webapp_host: str
    webapp_port: int

    @staticmethod
    def from_env(env: Env):
        """
        Creates the WebhookConfig object from environment variables.
        """
        webhook_url = env.str("WEBHOOK_URL")
        webhook_main_path = env.str("WEBHOOK_PATH")
        webhook_other_bots_path = env.str("WEBHOOK_OTHER_BOTS_PATH")
        webapp_host = env.str("WEBAPP_HOST")
        webapp_port = env.int("WEBAPP_PORT")
        return WebhookConfig(
            webhook_url=webhook_url,
            webhook_main_path=webhook_main_path,
            webhook_other_bots_path=webhook_other_bots_path,
            webapp_host=webapp_host,
            webapp_port=webapp_port,
        )


@dataclass
class Hearthstone:
    api_key: str

    @staticmethod
    def from_env(env: Env):
        """
        Creates the Hearthstone object from environment variables.
        """
        api_key = env.str("HEARTHSTONE_API_KEY")
        return Hearthstone(api_key=api_key)


@dataclass
class Config:
    tg_bot: TgBot
    webhook: WebhookConfig
    heartstone: Hearthstone


def load_config(path: str = None) -> Config:
    """
    This function takes an optional file path as input and returns a Config object.
    :param path: The path of env file from where to load the configuration variables.
    It reads environment variables from a .env file if provided, else from the process environment.
    :return: Config object with attributes set as per environment variables.
    """

    # Create an Env object.
    # The Env object will be used to read environment variables.
    env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot.from_env(env),
        webhook=WebhookConfig.from_env(env),
        heartstone=Hearthstone.from_env(env),
    )
