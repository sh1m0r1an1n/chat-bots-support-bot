import logging
import os
import time
import traceback

from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from dialogflow_utils import DialogflowConnector
from logging_utils import setup_logging


def start(update, _):
    """Обработчик команды /start"""
    update.message.reply_text("Здравствуйте! Я ваш помощник. Задайте ваш вопрос.")
    logging.info(f"[TG БОТ] Пользователь {update.message.chat.id} запустил бота")


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
        logging.info(f"[TG БОТ] Обработано сообщение от {user_id}: {user_text}")
    except Exception as e:
        logging.error(f"[TG БОТ] Ошибка обработки сообщения: {e}")
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

        logging.info("[TG БОТ] Бот с интеграцией Dialogflow запущен и готов к работе")
        updater.start_polling()
        updater.idle()

    except KeyError as e:
        logging.critical(f"[TG БОТ] Отсутствует переменная окружения: {e}")
        raise
    except Exception as e:
        logging.critical(f"[TG БОТ] Ошибка при запуске бота: {e}")
        raise


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.critical(f"[TG БОТ] Критическая ошибка: {e}\n{traceback.format_exc()}")
            time.sleep(5)