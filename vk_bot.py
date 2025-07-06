import logging
import os
import time
import traceback

from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from dialogflow_utils import DialogflowConnector
from logging_utils import setup_logging


def send_message(vk, user_id, message):
    """Отправляет сообщение пользователю"""
    try:
        vk.messages.send(
            peer_id=user_id,
            message=message,
            random_id=vk_api.utils.get_random_id()
        )
        logging.info(f'[VK БОТ] Отправлен ответ пользователю {user_id}')
    except Exception as e:
        logging.error(f"[VK БОТ] Ошибка отправки сообщения: {e}")


def main():
    """Основной цикл работы бота"""
    load_dotenv()

    tg_bot_token = os.getenv("TG_BOT_TOKEN")
    tg_chat_id = os.getenv("TG_CHAT_ID")
    dialogflow_project_id = os.getenv("DIALOGFLOW_PROJECT_ID")
    vk_group_token = os.getenv("VK_GROUP_TOKEN")

    try:
        setup_logging(tg_bot_token, tg_chat_id)
        logging.info("[VK БОТ] Инициализация бота")

        dialogflow_connector = DialogflowConnector(dialogflow_project_id)

        vk_session = vk_api.VkApi(token=vk_group_token)
        longpoll = VkLongPoll(vk_session)
        vk = vk_session.get_api()

        logging.info("[VK БОТ] Бот VK запущен и ожидает сообщений...")

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                logging.info(f"[VK БОТ] Новое сообщение от {event.user_id}: {event.text}")

                response = dialogflow_connector.get_response(
                    str(event.user_id),
                    event.text
                )

                if response:
                    send_message(vk, event.user_id, response)

    except KeyError as e:
        logging.critical(f"[VK БОТ] Отсутствует переменная окружения: {e}")
        raise
    except Exception as e:
        logging.critical(f"[VK БОТ] Ошибка в работе бота: {e}")
        raise


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.critical(f"[VK БОТ] Критическая ошибка: {e}\n{traceback.format_exc()}")
            time.sleep(5)