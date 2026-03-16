# JR_GPT_bot

Telegram bot built with `aiogram` and OpenAI API integration.  
The project provides multiple chat modes and runs in polling mode.

## Features

Implemented commands:

- `/start`: greeting + inline main menu
- `/help`: command list
- `/random`: random science fact via OpenAI
- `/gpt`: GPT chat with context (FSM-based)
- `/talk`: role-play chat with selected person
- `/quiz`: topic-based quiz with answer evaluation
- `/rag`: ask questions over uploaded text/PDF or pasted text
- `/yt`: summarize a YouTube video transcript (fixed 3 min read, with language selection) + read aloud

Security and performance hardening:

- Input/output hardening for Telegram (`HTML` escaping where needed, long text chunking)
- Per-user rate limits for expensive flows (`/gpt`, `/talk`, `/quiz`, `/rag`, `/yt`, TTS)
- OpenAI request timeout + retry/backoff for transient failures
- Global concurrency guard for OpenAI requests to avoid overload spikes
- RAG source limits:
- Max upload size: `5 MB`
- Max stored source text: `120000` chars
- Max stored RAG chunks: `220`
- Max injected context per answer: `12000` chars
- PDF extraction in background thread (non-blocking event loop)
- YouTube link parsing with stricter video-id validation and transcript caching

Current personas in `/talk`:

- Alexander Pushkin
- Elon Musk
- Steve Jobs
- Albert Einstein

## Project Structure

```text
JR_GPT_bot/
|- main.py                    # Entry point, starts polling
|- config.py                  # Loads and validates BOT_TOKEN / OPENAI_API_KEY
|- requirements               # Python dependencies
|- handlers/
|  |- commands_handler.py     # /start, /help, menu callbacks
|  |- random_fact.py          # /random + repeat/stop
|  |- gpt_chat.py             # /gpt + stateful conversation
|  |- talk.py                 # /talk + persona selection + dialogue
|  |- quiz.py                 # /quiz + topic selection + Q/A flow
|  |- rag.py                  # /rag + source upload + context Q/A
|  |- youtube_summary.py      # /yt + transcript summary by read-time
|- keyboards/
|  |- inline.py               # Inline keyboards
|- services/
|  |- openai_service.py       # OpenAI client + ask_gpt()
|- states/
|  |- state.py                # FSM states for GPT/Talk/Quiz/RAG/YT
|- utils/
|  |- quiz_generate.py        # Quiz question generation/checking
|  |- rag_tools.py            # Chunking + retrieval helpers
|  |- youtube_tools.py        # YouTube URL parsing + transcript fetch
|- images/
   |- gpt.jpg
   |- quiz.png
   |- random.png
   |- talk.jpg
```

## Technical Flow

1. `main.py` initializes `Dispatcher` and starts polling.
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

Create a `.env` file in project root:

```env
BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
```

`config.py` validates these variables on startup.

## Run

```bash
python main.py
```

## Notes

- Configured model: `gpt-4o-mini`
- `openai_service.py` has no import-time test call side effects
- Image files in `images/` are required for photo messages
- OpenAI calls are protected by retries, timeout, and concurrency semaphore
- Large model responses are split into safe Telegram-sized chunks
- RAG and YouTube flows include request throttling and safer content handling

---

## Русская версия

Телеграм-бот на `aiogram` с интеграцией OpenAI API.

Команды:

- `/start`, `/help`, `/random`, `/gpt`, `/talk`, `/quiz`, `/rag`, `/yt`

Что реализовано:

- Режим случайных фактов
- Контекстный GPT-чат
- Диалог с персоной
- Квиз по теме с проверкой ответа
- RAG-режим: вопросы по загруженному тексту/PDF
- Краткие summary для YouTube-ссылок (фиксированная длина 3 минуты, с выбором языка) + озвучка

Ключевые детали:

- В `config.py` есть проверка обязательных переменных `.env`
- `services/openai_service.py` не делает тестовый вызов при импорте
- Текущая модель: `gpt-4o-mini`

---

## Deutsche Version

Telegram-Bot auf Basis von `aiogram` mit OpenAI-API.

Befehle:

- `/start`, `/help`, `/random`, `/gpt`, `/talk`, `/quiz`, `/rag`, `/yt`

Umgesetzte Modi:

- Zufallsfakten
- GPT-Chat mit Kontext
- Persona-Dialog
- Themen-Quiz mit Antwortpruefung
- RAG-Modus: Fragen zu hochgeladenen Texten/PDFs
- YouTube-Zusammenfassungen (feste Länge 3 Minuten, mit Sprachauswahl) + Vorlesen

Wichtige Hinweise:

- `config.py` prueft erforderliche `.env`-Variablen beim Start
- `services/openai_service.py` fuehrt beim Import keine Testaufrufe aus
- Aktuelles Modell: `gpt-4o-mini`
