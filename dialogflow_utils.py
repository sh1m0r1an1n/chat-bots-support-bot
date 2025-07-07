import logging
import os
from google.cloud import dialogflow_v2 as dialogflow


def detect_intent_text(project_id, session_id, text, language_code='ru'):
    """Возвращает fulfillment_text из Dialogflow или None, если intent fallback."""
    log_prefix = os.getenv("BOT_LOG_PREFIX", "[DIALOGFLOW]")
    
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)
    text_input = dialogflow.TextInput(text=text, language_code=language_code)
    query_input = dialogflow.QueryInput(text=text_input)
    
    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )
    
    if response.query_result.intent.is_fallback:
        logging.info(f"{log_prefix} Fallback intent для пользователя {session_id}")
        return None
    
    logging.info(f"{log_prefix} Успешный ответ Dialogflow для {session_id}")
    return response.query_result.fulfillment_text