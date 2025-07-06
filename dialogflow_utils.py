import logging
import os
from google.cloud import dialogflow_v2 as dialogflow

class DialogflowConnector:
    """Класс для работы с Dialogflow API"""
    def __init__(self, project_id):
        self.project_id = project_id
        self.session_client = dialogflow.SessionsClient()
        self.log_prefix = os.getenv("BOT_LOG_PREFIX", "[DIALOGFLOW]")
        logging.info(f"{self.log_prefix} DialogflowConnector инициализирован")

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
                logging.info(f"{self.log_prefix} Fallback intent для пользователя {session_id}")
                return None

            logging.info(f"{self.log_prefix} Успешный ответ Dialogflow для {session_id}")
            return response.query_result.fulfillment_text
        except Exception as e:
            logging.error(f"{self.log_prefix} Dialogflow error: {e}")
            return None