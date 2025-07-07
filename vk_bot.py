import logging
import os
import time

from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

from dialogflow_utils import detect_intent_text
from logging_utils import setup_logging


def send_message(vk, user_id, message):
    """Отправляет сообщение пользователю"""
    vk.messages.send(
        peer_id=user_id,
        message=message,
        random_id=vk_api.utils.get_random_id()
    )
    logging.info(f'[VK БОТ] Отправлен ответ пользователю {user_id}')


def main():
    """Основной цикл работы VK бота."""
    load_dotenv()
    os.environ["BOT_LOG_PREFIX"] = "[DIALOGFLOW][VK БОТ]"

    tg_bot_token = os.environ["TG_BOT_TOKEN"]
    tg_chat_id = os.environ["TG_CHAT_ID"]
    dialogflow_project_id = os.environ["DIALOGFLOW_PROJECT_ID"]
    vk_group_token = os.environ["VK_GROUP_TOKEN"]

    setup_logging(tg_bot_token, tg_chat_id)
    logging.info("[VK БОТ] Инициализация бота")

    vk_session = vk_api.VkApi(token=vk_group_token)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    logging.info("[VK БОТ] Бот VK запущен и ожидает сообщений...")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            logging.info(f"[VK БОТ] Новое сообщение от {event.user_id}: {event.text}")
            
            session_id = f"vk-{event.user_id}"
            response = detect_intent_text(dialogflow_project_id, session_id, event.text)
            if response:
                send_message(vk, event.user_id, response)


if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            logging.exception(f"[VK БОТ] Критическая ошибка: {e}")
            time.sleep(5)