import logging

from telegram import Bot


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