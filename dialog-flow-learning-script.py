import os
import json
from dotenv import load_dotenv
from google.cloud import dialogflow_v2 as dialogflow
from google.oauth2 import service_account


def main():
    """Создает интенты в Dialogflow из JSON файла с вопросами и ответами."""
    load_dotenv()

    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    credentials_path = os.getenv('DIALOGFLOW_CREDENTIALS_PATH')
    questions_file = os.getenv('QUESTIONS_JSON_FILE', 'questions.json')

    credentials = service_account.Credentials.from_service_account_file(credentials_path)
    intents_client = dialogflow.IntentsClient(credentials=credentials)
    parent = dialogflow.AgentsClient.agent_path(project_id)

    with open(questions_file, 'r', encoding='utf-8') as f:
        questions_data = json.load(f)

    for category, data in questions_data.items():
        training_phrases = [
            dialogflow.Intent.TrainingPhrase(parts=[
                dialogflow.Intent.TrainingPhrase.Part(text=question)
            ]) for question in data["questions"]
        ]

        message = dialogflow.Intent.Message(
            text=dialogflow.Intent.Message.Text(text=[data["answer"]])
        )

        intent = dialogflow.Intent(
            display_name=category[:60],
            training_phrases=training_phrases,
            messages=[message]
        )

        intents_client.create_intent(request={"parent": parent, "intent": intent})
        print(f"Создан интент: {category}")


if __name__ == "__main__":
    main()