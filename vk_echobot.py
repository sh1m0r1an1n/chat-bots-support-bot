import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


def send_message(vk, user_id, message):
    """Отправляет сообщение пользователю"""
    print(f'Новое сообщение от {user_id}: {message}')

    vk.messages.send(
        peer_id=user_id,
        message=message,
        random_id=vk_api.utils.get_random_id()
    )
    print(f'Отправлен ответ пользователю {user_id}: {message}')



def main():
    """Основной цикл работы бота"""
    load_dotenv()
    vk_group_token = os.getenv('VK_GROUP_TOKEN')

    vk_session = vk_api.VkApi(token=vk_group_token)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    print('Бот запущен и ожидает сообщений...')

    for event in longpoll.listen():
        print(f"Получено событие: {event.type}")
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            print(f"Новое сообщение от {event.user_id}: {event.text}")
            send_message(vk, event.user_id, event.text)


if __name__ == "__main__":
    main()