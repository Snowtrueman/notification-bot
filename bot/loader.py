import os
import logging
from db import get_session
from i18n_class import I18N
from dotenv import load_dotenv
from telebot import TeleBot, apihelper
from telebot.storage.memory_storage import StateMemoryStorage


def get_logger() -> logging.Logger:
    """
        Configures and creates logger.
    Returns:
        Logger instance.
    """

    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    logging.basicConfig(level=logging.INFO, filename="logs/log.log", filemode="w",
                        format="%(asctime)s : %(levelname)s | %(name)s --- %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    return logging.getLogger("bot")


def load_env() -> None:
    """
    Load all the variables found as environment variables in .env file.
    Returns:
        None
    """
    dotenv_path = os.path.join(os.path.dirname(__file__), ".env")

    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        logger.critical("Missing .env file. Can't find it in project root directory.")


logger = get_logger()
session = get_session()

apihelper.ENABLE_MIDDLEWARE = True
storage = StateMemoryStorage()

i18n = I18N(translations_path="bot/locale", domain_name="messages")
_ = i18n.gettext

load_env()
TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
NOTIFICATION_FREQUENCY = os.environ.get("NOTIFICATION_FREQUENCY")
bot = TeleBot(TOKEN, state_storage=storage, threaded=False)


