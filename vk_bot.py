import logging
import os
import requests.exceptions
import time
import traceback

from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from dialogflow_utils import detect_intent_text
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
    """Основной цикл работы VK бота."""
    load_dotenv()
    os.environ["BOT_LOG_PREFIX"] = "[DIALOGFLOW][VK БОТ]"

    tg_bot_token = os.environ["TG_BOT_TOKEN"]
    tg_chat_id = os.environ["TG_CHAT_ID"]
    dialogflow_project_id = os.environ["DIALOGFLOW_PROJECT_ID"]
    vk_group_token = os.environ["VK_GROUP_TOKEN"]

    try:
        setup_logging(tg_bot_token, tg_chat_id)
        logging.info("[VK БОТ] Инициализация бота")

        vk_session = vk_api.VkApi(token=vk_group_token)
        longpoll = VkLongPoll(vk_session)
        vk = vk_session.get_api()

        logging.info("[VK БОТ] Бот VK запущен и ожидает сообщений...")

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                logging.info(f"[VK БОТ] Новое сообщение от {event.user_id}: {event.text}")
                
                response = detect_intent_text(dialogflow_project_id, str(event.user_id), event.text)
                if response:
                    send_message(vk, event.user_id, response)
    
    except requests.exceptions.ReadTimeout as e:
        logging.warning(f"[VK БОТ][DIALOGFLOW] Таймаут соединения: {e}")
        raise
    except Exception as e:
        logging.critical(f"[VK БОТ][DIALOGFLOW] Ошибка в работе бота: {e}")
        raise


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.critical(f"[VK БОТ] Критическая ошибка: {e}\n{traceback.format_exc()}")
            time.sleep(5)