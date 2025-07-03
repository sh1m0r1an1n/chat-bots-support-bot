import logging
import os
import time
import traceback

from dotenv import load_dotenv
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import Bot, TelegramError


class TelegramLogHandler(logging.Handler):
    """Отправляет логи в Telegram"""

    def __init__(self, bot_token, chat_id, level=logging.INFO):
        super().__init__(level=level)
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

    def emit(self, record):
        """Отправка сообщения с логом"""
        log_entry = self.format(record)
        self.bot.send_message(chat_id=self.chat_id, text=log_entry)


def setup_logging(bot_token, chat_id):
    """Настройка логирования для Telegram"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    logging.getLogger('apscheduler.scheduler').setLevel(logging.WARNING)

    telegram_handler = TelegramLogHandler(bot_token, chat_id)
    telegram_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(telegram_handler)


def start(update, context):
    """Обработчик команды /start"""
    try:
        update.message.reply_text("Здравствуйте!")
        logging.info(f"Пользователь {update.message.chat.id} запустил бота")
    except Exception as e:
        logging.error(f"Ошибка в start-функции: {e}")


def echo(update, context):
    """Эхо-функция, которая возвращает полученное сообщение"""
    try:
        user_message = update.message.text
        update.message.reply_text(user_message)
        logging.info(f"Получено сообщение: {user_message}")
    except Exception as e:
        logging.error(f"Ошибка в эхо-функции: {e}")


def main():
    """Основная функция запуска бота."""
    load_dotenv()

    try:
        bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
        chat_id = os.environ["TELEGRAM_CHAT_ID"]
    except KeyError as e:
        logging.exception(f"Отсутствует переменная окружения: {e}")
        raise

    setup_logging(bot_token, chat_id)

    try:
        updater = Updater(token=bot_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

        logging.info("Эхобот запущен и готов к работе")
        updater.start_polling()
        updater.idle()
    except Exception as e:
        logging.critical(f"Ошибка при запуске бота: {e}")
        raise


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.critical(f"Критическая ошибка: {e}\n{traceback.format_exc()}")
            time.sleep(5)