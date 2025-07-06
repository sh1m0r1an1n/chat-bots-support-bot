# Чат-бот поддержки для "Игры глаголов" 📚

Рабочие версии ботов: Telegram (@Verb_Game_Assistant_Bot), [ВКонтакте](https://vk.com/club231412959)

## Функционал

- Умные ответы на частые вопросы через Dialogflow
- Две платформы: Telegram + ВКонтакте
- Автоматическое обучение на новых вопросах
- Интеллектуальное молчание при сложных запросах (передача оператору)
- Мониторинг работы через Telegram-логи

## Требования

- Python 3.10+
- Dialogflow ES (API v2)
- Telegram Bot API
- VK API
- Google Cloud Platform

## Установка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/sh1m0r1an1n/chat-bots-support-bot.git
cd chat-bots-support-bot
```

2. Установите зависимости:
```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` и заполните его:
```ini
# Dialogflow
DIALOGFLOW_PROJECT_ID=ваш-project-id
GOOGLE_APPLICATION_CREDENTIALS=путь/к/credentials.json

# Telegram
TG_BOT_TOKEN=ваш:telegram_токен
TG_CHAT_ID=ваш_chat_id_для_логов

# ВКонтакте 
VK_GROUP_TOKEN=ваш_vk_токен_группы
```

4. Обучение бота
Поместите файл с вопросами questions.json и запустите обучение:
```bash
python dialog-flow-learning-script.py
```
Пример файла questions.json:
```json
{
  "Опубликовать книгу": {
    "questions": [
      "Как издать свою книгу?",
      "Хочу опубликовать произведение",
      "Процесс публикации книги"
    ],
    "answer": "Чтобы опубликовать книгу... (полный ответ)"
  }
}
```

## Запуск ботов
```bash
# Telegram бот
python tg_bot.py

# VK бот (в отдельном терминале)
python vk_bot.py
```

## Пример работы
[Пример результата для Telegram:](media/demo_tg_bot.gif)
[Пример результата для ВКонтакте:](media/demo_vk_bot.gif)

## Запуск на сервере

1. Подготовка сервера
- Арендуйте VPS (например, Ubuntu 22.04)
- Получите данные доступа: IP, username (обычно root), пароль
- Подключитесь:
```bash
ssh root@ваш_IP
```

2. Настройка SSH-доступа
- На локальной машине создайте ключи:
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
``` 
- Скопируйте публичный ключ на сервер:
```bash
ssh-copy-id root@ваш_IP
``` 
- На сервере запретите вход по паролю:
```bash
nano /etc/ssh/sshd_config
``` 
Установите:
```text
PasswordAuthentication no
ChallengeResponseAuthentication no
``` 
- Перезапустите SSH:
```bash
systemctl restart sshd
``` 

3. Настройка доступа к GitHub
- Добавьте публичный ключ в GitHub (Settings → SSH and GPG keys)
- Включите SSH Agent Forwarding в `~/.ssh/config`:
```text
Host ваш_сервер
  HostName ваш_IP
  User root
  ForwardAgent yes
``` 

4. Установка бота
- На сервере:
```bash
apt update && apt install -y git python3-venv
git clone git@github.com:sh1m0r1an1n/chat-bots-devman-bot.git
cd chat-bots-devman-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
``` 

5. Настройка systemd
- Создайте сервисный файл:
```bash
nano /etc/systemd/system/devman-bot.service
``` 
- Добавьте конфигурацию:
```ini
[Unit]
Description=Verb Game Support Bot
After=network.target

[Service]
User=root
WorkingDirectory=/path/to/bot
ExecStart=/path/to/venv/bin/python /path/to/tg_bot.py
ExecStart=/path/to/venv/bin/python /path/to/vk_bot.py
Restart=always
Environment="PATH=/path/to/venv/bin"

[Install]
WantedBy=multi-user.target
```
- Запустите бота:
```bash
systemctl daemon-reload
systemctl enable verb-game-bot
systemctl start verb-game-bot
``` 

## Проверка работы

```bash
systemctl status verb-game-bot
journalctl -u verb-game-bot -f
``` 

## Обновление бота

```bash
cd /root/chat-bots-verb-game-bot
git pull
systemctl restart verb-game-bot
``` 