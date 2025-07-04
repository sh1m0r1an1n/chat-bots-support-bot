import os
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from google.cloud import dialogflow_v2 as dialogflow
import logging


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
            return "Извините, произошла ошибка при обработке вашего запроса"


def send_message(vk, user_id, message):
    """Отправляет сообщение пользователю"""
    try:
        vk.messages.send(
            peer_id=user_id,
            message=message,
            random_id=vk_api.utils.get_random_id()
        )
        print(f'Отправлен ответ пользователю {user_id}: {message}')
    except Exception as e:
        print(f"Ошибка отправки сообщения: {e}")


def main():
    """Основной цикл работы бота"""
    load_dotenv()

    dialogflow_connector = DialogflowConnector(os.getenv('DIALOGFLOW_PROJECT_ID'))

    vk_group_token = os.getenv('VK_GROUP_TOKEN')
    vk_session = vk_api.VkApi(token=vk_group_token)
    longpoll = VkLongPoll(vk_session)
    vk = vk_session.get_api()

    print('Бот запущен и ожидает сообщений...')

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            print(f"Новое сообщение от {event.user_id}: {event.text}")

            response = dialogflow_connector.get_response(str(event.user_id), event.text)

            send_message(vk, event.user_id, response or "Не удалось обработать запрос")


if __name__ == "__main__":
    main()