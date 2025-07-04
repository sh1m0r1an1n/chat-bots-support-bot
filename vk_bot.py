import logging
import os
import time
import traceback

from dotenv import load_dotenv
from google.cloud import dialogflow_v2 as dialogflow
from telegram import Bot
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


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
        logging.info("DialogflowConnector инициализирован")

    def get_response(self, session_id, text, language_code='ru'):
        """Получает ответ от Dialogflow"""
        try:
            session = self.session_client.session_path(self.project_id, session_id)
            text_input = dialogflow.TextInput(text=text, language_code=language_code)
            query_input = dialogflow.QueryInput(text=text_input)
            response = self.session_client.detect_intent(
                request={"session": session, "query_input": query_input}
            )

            if response.query_result.intent.is_fallback:
                logging.info(f"Fallback intent для пользователя {session_id}")
                return None

            logging.info(f"Успешный ответ Dialogflow для {session_id}")
            return response.query_result.fulfillment_text
        except Exception as e:
            logging.error(f"Dialogflow error: {e}")
            return None


def setup_logging(bot_token, chat_id):
    """Настройка логирования для Telegram"""
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    telegram_handler = TelegramLogHandler(bot_token, chat_id)
    telegram_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    )
    logger.addHandler(telegram_handler)


def send_message(vk, user_id, message):
    """Отправляет сообщение пользователю"""
    try:
        vk.messages.send(
            peer_id=user_id,
            message=message,
            random_id=vk_api.utils.get_random_id()
        )
        logging.info(f'Отправлен ответ пользователю {user_id}')
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения: {e}")


def main():
    """Основной цикл работы бота"""
    load_dotenv()

    tg_bot_token = os.environ["TG_BOT_TOKEN"]
    tg_chat_id = os.environ["TG_CHAT_ID"]
    dialogflow_project_id = os.environ["DIALOGFLOW_PROJECT_ID"]
    vk_group_token = os.environ["VK_GROUP_TOKEN"]

    try:
        setup_logging(tg_bot_token, tg_chat_id)
        logging.info("Инициализация бота VK")

        dialogflow_connector = DialogflowConnector(dialogflow_project_id)

        vk_session = vk_api.VkApi(token=vk_group_token)
        longpoll = VkLongPoll(vk_session)
        vk = vk_session.get_api()

        logging.info("Бот VK запущен и ожидает сообщений...")

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                logging.info(f"Новое сообщение от {event.user_id}: {event.text}")

                response = dialogflow_connector.get_response(
                    str(event.user_id),
                    event.text
                )

                if response:
                    send_message(vk, event.user_id, response)

    except KeyError as e:
        logging.critical(f"Отсутствует переменная окружения: {e}")
        raise
    except Exception as e:
        logging.critical(f"Ошибка в работе бота: {e}")
        raise


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.critical(f"Критическая ошибка: {e}\n{traceback.format_exc()}")
            time.sleep(5)