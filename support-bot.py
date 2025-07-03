import logging
import os
import time
import traceback

from dotenv import load_dotenv
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import Bot, TelegramError
from google.cloud import dialogflow_v2 as dialogflow


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


class DialogflowConnector:
    """Класс для работы с Dialogflow API"""
    def __init__(self, project_id):
        self.project_id = project_id
        self.session_client = dialogflow.SessionsClient()

    def get_response(self, session_id, text, language_code='ru'):
        """Получает ответ от Dialogflow"""
        try:
            session = self.session_client.session_path(self.project_id, session_id)
            text_input = dialogflow.TextInput(text=text, language_code=language_code)
            query_input = dialogflow.QueryInput(text=text_input)
            response = self.session_client.detect_intent(
                request={"session": session, "query_input": query_input}
            )
            return response.query_result.fulfillment_text
        except Exception as e:
            logging.error(f"Dialogflow error: {e}")
            return


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
        update.message.reply_text("Здравствуйте! Я ваш помощник. Задайте ваш вопрос.")
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


def handle_message(update, context):
    """Обработчик текстовых сообщений с интеграцией Dialogflow"""
    try:
        user_id = str(update.message.chat.id)
        user_text = update.message.text

        dialogflow_connector = context.bot_data.get('dialogflow')
        if not dialogflow_connector:
            project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
            dialogflow_connector = DialogflowConnector(project_id)
            context.bot_data['dialogflow'] = dialogflow_connector

        response = dialogflow_connector.get_response(user_id, user_text)
        update.message.reply_text(response)

        logging.info(f"Обработано сообщение от {user_id}: {user_text}")
    except Exception as e:
        logging.error(f"Ошибка обработки сообщения: {e}")
        update.message.reply_text("Произошла ошибка при обработке вашего запроса")


def main():
    """Основная функция запуска бота."""
    load_dotenv()

    try:
        bot_token = os.environ["TELEGRAM_BOT_TOKEN"]
        chat_id = os.environ["TELEGRAM_CHAT_ID"]
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.getenv("DIALOGFLOW_CREDENTIALS_PATH")
    except KeyError as e:
        logging.exception(f"Отсутствует переменная окружения: {e}")
        raise

    setup_logging(bot_token, chat_id)

    try:
        updater = Updater(token=bot_token)
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

        logging.info("Бот с интеграцией Dialogflow запущен и готов к работе")
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