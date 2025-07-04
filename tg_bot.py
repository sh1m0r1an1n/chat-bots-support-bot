import logging
import os
import time
import traceback

from dotenv import load_dotenv
from google.cloud import dialogflow_v2 as dialogflow
from telegram import Bot
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater


class TelegramLogHandler(logging.Handler):
    """Отправляет логи в Telegram"""

    def __init__(self, bot_token, chat_id, level=logging.INFO):
        super().__init__(level=level)
        self.bot = Bot(token=bot_token)
        self.chat_id = chat_id

    def emit(self, record):
        """Отправка сообщения с логом"""
        log_entry = self.format(record)
        try:
            self.bot.send_message(chat_id=self.chat_id, text=log_entry)
        except Exception as e:
            logging.error(f"Ошибка отправки лога в Telegram: {e}")


class DialogflowConnector:
    """Класс для работы с Dialogflow API"""
    def __init__(self, project_id):
        self.project_id = project_id
        self.session_client = dialogflow.SessionsClient()

    def get_response(self, session_id, text, language_code='ru'):
        """Получает ответ от Dialogflow"""
        session = self.session_client.session_path(self.project_id, session_id)
        text_input = dialogflow.TextInput(text=text, language_code=language_code)
        query_input = dialogflow.QueryInput(text=text_input)
        response = self.session_client.detect_intent(
            request={"session": session, "query_input": query_input}
        )
        return response.query_result.fulfillment_text


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


def start(update, _):
    """Обработчик команды /start"""
    update.message.reply_text("Здравствуйте! Я ваш помощник. Задайте ваш вопрос.")
    logging.info(f"Пользователь {update.message.chat.id} запустил бота")


def handle_message(update, context):
    """Обработчик текстовых сообщений с интеграцией Dialogflow"""
    user_id = str(update.message.chat.id)
    user_text = update.message.text

    if 'dialogflow' not in context.bot_data:
        context.bot_data['dialogflow'] = DialogflowConnector(
            context.bot_data['dialogflow_project_id']
        )

    try:
        response = context.bot_data['dialogflow'].get_response(user_id, user_text)
        update.message.reply_text(response)
        logging.info(f"Обработано сообщение от {user_id}: {user_text}")
    except Exception as e:
        logging.error(f"Ошибка обработки сообщения: {e}")
        update.message.reply_text("Произошла ошибка при обработке вашего запроса")


def main():
    """Основная функция запуска бота."""
    load_dotenv()

    try:
        bot_token = os.environ["TG_BOT_TOKEN"]
        chat_id = os.environ["TG_CHAT_ID"]

        setup_logging(bot_token, chat_id)

        updater = Updater(token=bot_token)
        updater.dispatcher.bot_data['dialogflow_project_id'] = os.getenv("DIALOGFLOW_PROJECT_ID")
        dispatcher = updater.dispatcher

        dispatcher.add_handler(CommandHandler("start", start))
        dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

        logging.info("Бот с интеграцией Dialogflow запущен и готов к работе")
        updater.start_polling()
        updater.idle()

    except KeyError as e:
        logging.critical(f"Отсутствует переменная окружения: {e}")
        raise
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