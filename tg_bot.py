import logging
import os
import time

from dotenv import load_dotenv
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from dialogflow_utils import detect_intent_text
from logging_utils import setup_logging


def start(update, _):
    """Обработчик команды /start"""
    update.message.reply_text("Здравствуйте! Я ваш помощник. Задайте ваш вопрос.")
    logging.info(f"[TG БОТ] Пользователь {update.message.chat.id} запустил бота")


def help_command(update, _):
    """Обработчик команды /help"""
    help_text = """
🤖 Доступные команды:
/start - Начать работу с ботом
/help - Показать эту справку
\n💬 Просто напишите ваш вопрос, и я постараюсь помочь!
    """
    update.message.reply_text(help_text)
    logging.info(f"[TG БОТ] Пользователь {update.message.chat.id} запросил помощь")


def handle_message(update, context):
    """Обработчик текстовых сообщений с интеграцией Dialogflow"""
    user_id = str(update.message.chat.id)
    user_text = update.message.text
    project_id = context.bot_data['dialogflow_project_id']

    session_id = f"tg-{user_id}"
    response = detect_intent_text(project_id, session_id, user_text)
    update.message.reply_text(response)
    logging.info(f"[TG БОТ] Обработано сообщение от {user_id}: {user_text}")


def main():
    """Основная функция запуска бота."""
    load_dotenv()
    os.environ["BOT_LOG_PREFIX"] = "[DIALOGFLOW][TG БОТ]"

    bot_token = os.environ["TG_BOT_TOKEN"]
    chat_id = os.environ["TG_CHAT_ID"]

    setup_logging(bot_token, chat_id)

    updater = Updater(token=bot_token)
    updater.dispatcher.bot_data['dialogflow_project_id'] = os.environ["DIALOGFLOW_PROJECT_ID"]
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    logging.info("[TG БОТ] Бот с интеграцией Dialogflow запущен и готов к работе")
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.exception(f"[TG БОТ] Критическая ошибка: {e}")
            time.sleep(5)