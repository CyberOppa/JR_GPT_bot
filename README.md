# JR_GPT_bot

Telegram bot built with `aiogram` and OpenAI API integration.  
The project provides multiple chat modes (Random Fact, GPT chat, Persona chat) and runs in polling mode.

## Features

Implemented:

- `/start`: greeting + inline main menu
- `/help`: command list
- `/random`: generates a random science fact via OpenAI
- `/gpt`: starts a GPT chat with conversation context (FSM-based)
- `/talk`: starts a role-play chat with a selected person

Current personas in `/talk`:

- Alexander Pushkin
- Elon Musk
- Steve Jobs
- Albert Einstein

Not implemented yet:

- Quiz logic (`/quiz`): the main menu already contains a quiz button, but there is no quiz handler yet.

## Project Structure

```text
JR_GPT_bot/
|- main.py                    # Entry point, starts bot polling
|- config.py                  # Loads BOT_TOKEN and OPENAI_API_KEY from .env
|- requirements               # Python dependencies
|- handlers/
|  |- commands_handler.py     # /start, /help, menu callbacks
|  |- random_fact.py          # /random + repeat/stop
|  |- gpt_chat.py             # /gpt + stateful conversation
|  |- talk.py                 # /talk + persona selection + dialogue
|- keyboards/
|  |- inline.py               # Inline keyboards
|- services/
|  |- openai_service.py       # OpenAI client + ask_gpt()
|- states/
|  |- state.py                # FSM states for GPT/Talk modes
|- images/
   |- gpt.jpg
   |- random.png
   |- talk.jpg
```

## Technical Flow

1. `main.py` initializes `Bot` and `Dispatcher`.
2. Routers from `handlers/__init__.py` are included.
3. Handlers call `services/openai_service.py -> ask_gpt()` for model responses.
4. Conversation state is managed per chat with `aiogram` FSM (`states/state.py`).

## Requirements

- Python 3.11+ (recommended)
- Telegram Bot Token
- OpenAI API Key

## Installation

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements
```

## Configuration

Create a `.env` file in the project root:

```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

`config.py` loads these values via `python-dotenv`.

## Run

```bash
python main.py
```

The bot starts in polling mode.

## Notes

- `services/openai_service.py` currently has a direct test call at the end (`asyncio.run(main())`).
  Because of that, importing this module triggers an OpenAI request.
- The currently configured model is `gpt-4o-mini`.
- Image files in `images/` are required for photo messages.

<details>
<summary>Русская версия (нажмите, чтобы раскрыть)</summary>

## JR_GPT_bot

Телеграм-бот на `aiogram` с интеграцией OpenAI API.  
Проект включает несколько режимов общения (Random Fact, GPT-чат, диалог с персоной) и запускается в режиме polling.

## Функциональность

Реализовано:

- `/start`: приветствие и главное inline-меню
- `/help`: список команд
- `/random`: генерация случайного научного факта через OpenAI
- `/gpt`: чат с GPT с сохранением контекста (FSM)
- `/talk`: ролевой диалог с выбранной личностью

Персоны в `/talk`:

- Alexander Pushkin
- Elon Musk
- Steve Jobs
- Albert Einstein

Пока не реализовано:

- Логика квиза (`/quiz`): кнопка в меню уже есть, но обработчик пока отсутствует.

## Структура проекта

```text
JR_GPT_bot/
|- main.py                    # Точка входа, запуск polling
|- config.py                  # Читает BOT_TOKEN и OPENAI_API_KEY из .env
|- requirements               # Зависимости Python
|- handlers/
|  |- commands_handler.py     # /start, /help, callbacks меню
|  |- random_fact.py          # /random + повтор/выход
|  |- gpt_chat.py             # /gpt + контекст в состоянии
|  |- talk.py                 # /talk + выбор персоны + диалог
|- keyboards/
|  |- inline.py               # Inline-клавиатуры
|- services/
|  |- openai_service.py       # Клиент OpenAI + ask_gpt()
|- states/
|  |- state.py                # FSM-состояния для GPT/Talk
|- images/
   |- gpt.jpg
   |- random.png
   |- talk.jpg
```

## Технический поток

1. `main.py` инициализирует `Bot` и `Dispatcher`.
2. Подключаются роутеры из `handlers/__init__.py`.
3. Обработчики вызывают `services/openai_service.py -> ask_gpt()` для ответов модели.
4. Состояние диалога хранится по каждому чату через `aiogram` FSM (`states/state.py`).

## Требования

- Python 3.11+ (рекомендуется)
- Telegram Bot Token
- OpenAI API Key

## Установка

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements
```

## Конфигурация

Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

`config.py` загружает эти значения через `python-dotenv`.

## Запуск

```bash
python main.py
```

Бот запускается в режиме polling.

## Примечания

- В `services/openai_service.py` сейчас есть тестовый вызов (`asyncio.run(main())`) в конце файла.
  Из-за этого импорт модуля сразу отправляет запрос в OpenAI.
- Текущая модель: `gpt-4o-mini`.
- Для отправки изображений нужны файлы из `images/`.

</details>

<details>
<summary>Deutsche Version (zum Aufklappen)</summary>

## JR_GPT_bot

Telegram-Bot auf Basis von `aiogram` mit OpenAI-API-Anbindung.  
Das Projekt bietet mehrere Modi (Random Fact, GPT-Chat, Persona-Chat) und laeuft im Polling-Modus.

## Funktionen

Implementiert:

- `/start`: Begruessung und Inline-Hauptmenue
- `/help`: Kommando-Uebersicht
- `/random`: erzeugt einen zufaelligen Wissenschafts-Fakt ueber OpenAI
- `/gpt`: startet einen GPT-Chat mit Kontextspeicher (FSM)
- `/talk`: startet einen Rollenspiel-Chat mit ausgewaehlter Person

Personas in `/talk`:

- Alexander Pushkin
- Elon Musk
- Steve Jobs
- Albert Einstein

Noch nicht implementiert:

- Quiz-Logik (`/quiz`): Ein Quiz-Button ist im Menue vorhanden, aber es gibt noch keinen Handler.

## Projektstruktur

```text
JR_GPT_bot/
|- main.py                    # Einstiegspunkt, startet Polling
|- config.py                  # Laedt BOT_TOKEN und OPENAI_API_KEY aus .env
|- requirements               # Python-Abhaengigkeiten
|- handlers/
|  |- commands_handler.py     # /start, /help, Menue-Callbacks
|  |- random_fact.py          # /random + Wiederholen/Stop
|  |- gpt_chat.py             # /gpt + Verlauf im State
|  |- talk.py                 # /talk + Persona-Auswahl + Dialog
|- keyboards/
|  |- inline.py               # Inline-Keyboards
|- services/
|  |- openai_service.py       # OpenAI-Client + ask_gpt()
|- states/
|  |- state.py                # FSM-States fuer GPT/Talk
|- images/
   |- gpt.jpg
   |- random.png
   |- talk.jpg
```

## Technischer Ablauf

1. `main.py` initialisiert `Bot` und `Dispatcher`.
2. Router aus `handlers/__init__.py` werden eingebunden.
3. Handler rufen `services/openai_service.py -> ask_gpt()` fuer Modellantworten auf.
4. Dialogzustand wird pro Chat mit `aiogram` FSM (`states/state.py`) verwaltet.

## Voraussetzungen

- Python 3.11+ (empfohlen)
- Telegram Bot Token
- OpenAI API Key

## Installation

```bash
python -m venv .venv
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

pip install -r requirements
```

## Konfiguration

Lege im Projektroot eine `.env`-Datei an:

```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

`config.py` laedt diese Werte ueber `python-dotenv`.

## Start

```bash
python main.py
```

Der Bot startet im Polling-Modus.

## Hinweise

- In `services/openai_service.py` gibt es aktuell am Dateiende einen Testaufruf (`asyncio.run(main())`).
  Dadurch wird beim Import des Moduls direkt ein OpenAI-Request ausgeloest.
- Das aktuell konfigurierte Modell ist `gpt-4o-mini`.
- Fuer Foto-Nachrichten muessen die Dateien in `images/` vorhanden sein.

</details>
