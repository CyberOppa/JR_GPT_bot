# JR_GPT_bot

A comprehensive, multi-functional Telegram bot built with **Python 3.11+**, **aiogram 3**, and **OpenAI API**.
This bot serves as a playground for various AI interactions, including role-playing, document analysis (RAG), quizzes, and YouTube video summarization.

---

## 🇬🇧 English Description

### Features

The bot runs in polling mode and supports the following commands:

*   **/start**: Initializes the bot and shows the main menu.
*   **/help**: Lists all available commands.
*   **/random**: Generates a random scientific fact using GPT, illustrated with a photo.
*   **/gpt**: Starts a context-aware chat session with ChatGPT (similar to the web interface).
*   **/talk**: Role-play conversation with famous personas (Elon Musk, Steve Jobs, Albert Einstein, Alexander Pushkin).
*   **/quiz**: Starts a trivia quiz on various topics (Science, Tech, Movies, etc.) with AI-generated questions and answer validation.
*   **/rag**: **RAG (Retrieval-Augmented Generation)** mode. Upload PDF/TXT files or paste text to ask questions specifically based on that content.
*   **/yt**: **YouTube Summarizer**. Paste a YouTube link to get a structured summary (TL;DR, Key Points) and an optional Text-to-Speech (TTS) reading of the summary.

### Technical Highlights & Hardening

*   **Robust Architecture**: Built with `aiogram` routers and FSM (Finite State Machine) for managing conversation states.
*   **OpenAI Integration**:
    *   Uses `gpt-4o-mini` for cost-effective and fast responses.
    *   **Reliability**: Implemented retry logic with exponential backoff for API errors.
    *   **Concurrency Control**: Semaphore limits parallel requests to prevent API rate limiting.
    *   **TTS Fix**: Custom timeout (60s) for Text-to-Speech to handle long generation times.
*   **RAG System**:
    *   Supports `.pdf`, `.txt`, `.md`, and Python files.
    *   Smart chunking algorithm with overlap.
    *   Background processing for PDF extraction.
    *   Expanded character support (including German/Russian) for tokenization.
*   **YouTube Tools**:
    *   Multi-strategy transcript fetching (Static API, List API, and fallback methods) to ensure transcripts are retrieved even if the library behaves inconsistently.
    *   Strict video ID validation.

### Project Structure

```text
JR_GPT_bot/
├── main.py                    # Application entry point
├── config.py                  # Configuration & Validation
├── handlers/                  # Message handlers (routers)
│   ├── commands_handler.py    # General commands
│   ├── gpt_chat.py            # Free chat mode
│   ├── quiz.py                # Quiz logic
│   ├── rag.py                 # RAG (Document Q&A)
│   ├── talk.py                # Persona chat
│   ├── youtube_summary.py     # YouTube tools
│   └── ...
├── services/
│   └── openai_service.py      # OpenAI wrapper (Chat & TTS)
├── utils/
│   ├── youtube_tools.py       # Robust transcript fetcher
│   ├── rag_tools.py           # Text chunking & retrieval
│   └── ...
└── images/                    # Static assets for menus
```

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <repo_url>
    cd JR_GPT_bot
    ```

2.  **Create a virtual environment**:
    ```bash
    python -m venv .venv
    # Windows:
    .\.venv\Scripts\Activate
    # Linux/Mac:
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    pip install -r requirements
    ```

4.  **Configuration**:
    Create a `.env` file in the root directory:
    ```env
    BOT_TOKEN='YOUR_TELEGRAM_TOKEN'
    OPENAI_API_KEY='YOUR_OPENAI_API_KEY'
    ```

5.  **Run**:
    ```bash
    python main.py
    ```

---

<details>
<summary><b>🇩🇪 Deutsche Beschreibung (Hier klicken zum Ausklappen)</b></summary>

### Übersicht

Ein multifunktionaler Telegram-Bot, entwickelt mit **Python 3.11+**, **aiogram 3** und der **OpenAI API**.
Dieser Bot bietet verschiedene KI-Interaktionen, darunter Rollenspiele, Dokumentenanalyse (RAG), Quizze und YouTube-Video-Zusammenfassungen.

### Funktionen

*   **/start**: Startet den Bot und zeigt das Hauptmenü.
*   **/help**: Listet alle verfügbaren Befehle auf.
*   **/random**: Generiert einen zufälligen wissenschaftlichen Fakt (mit Bild).
*   **/gpt**: Startet einen Chat mit ChatGPT, der den Kontext des Gesprächs behält.
*   **/talk**: Rollenspiel-Modus mit Persönlichkeiten (Elon Musk, Steve Jobs, Albert Einstein, Alexander Puschkin).
*   **/quiz**: Themenbezogenes Quiz (Wissenschaft, Technik, Filme etc.) mit KI-generierten Fragen und Bewertung.
*   **/rag**: **RAG (Retrieval-Augmented Generation)**. Laden Sie PDF/TXT-Dateien hoch oder fügen Sie Text ein, um Fragen basierend auf diesem Inhalt zu stellen.
*   **/yt**: **YouTube-Zusammenfassung**. Senden Sie einen YouTube-Link, um eine strukturierte Zusammenfassung und optional eine Audio-Version (TTS) zu erhalten.

### Technische Highlights

*   **Architektur**: Basiert auf `aiogram` Routern und FSM (Finite State Machine) zur Zustandsverwaltung.
*   **OpenAI Integration**:
    *   Verwendet `gpt-4o-mini` für schnelle Antworten.
    *   **Zuverlässigkeit**: Retry-Logik mit exponentiellem Backoff bei API-Fehlern.
    *   **TTS Fix**: Erhöhtes Timeout (60s) für Text-to-Speech-Anfragen.
*   **RAG System**:
    *   Unterstützt `.pdf`, `.txt`, `.md`.
    *   Intelligentes Text-Chunking mit Überlappung.
    *   Verbesserte Tokenisierung für deutsche und russische Zeichen.
*   **YouTube Tools**:
    *   Robuster Transkript-Abruf mit mehreren Fallback-Strategien, um Fehler der externen Bibliothek abzufangen.

### Installation

1.  **Repository klonen**:
    ```bash
    git clone <repo_url>
    ```

2.  **Virtuelle Umgebung erstellen**:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\Activate  # Windows
    ```

3.  **Abhängigkeiten installieren**:
    ```bash
    pip install -r requirements
    ```

4.  **Konfiguration**:
    Erstellen Sie eine `.env` Datei:
    ```env
    BOT_TOKEN=Ihr_Telegram_Token
    OPENAI_API_KEY=Ihr_OpenAI_Key
    ```

5.  **Starten**:
    ```bash
    python main.py
    ```

</details>

---

<details>
<summary><b>🇷🇺 Описание на русском (Нажмите, чтобы развернуть)</b></summary>

### Обзор

Многофункциональный Телеграм-бот, написанный на **Python 3.11+** с использованием **aiogram 3** и **OpenAI API**.
Бот предоставляет различные сценарии использования ИИ: ролевые диалоги, анализ документов (RAG), викторины и саммари YouTube-видео.

### Функционал

*   **/start**: Запуск бота и главное меню.
*   **/help**: Список команд.
*   **/random**: Случайный научный факт от GPT с картинкой.
*   **/gpt**: Чат с ChatGPT с сохранением контекста диалога.
*   **/talk**: Ролевой чат с известными личностями (Илон Маск, Стив Джобс, Эйнштейн, Пушкин).
*   **/quiz**: Викторина по темам (Наука, Кино, Технологии) с генерацией вопросов и проверкой ответов через ИИ.
*   **/rag**: **RAG (Retrieval-Augmented Generation)**. Загрузите PDF/TXT или вставьте текст, чтобы задавать вопросы по конкретному документу.
*   **/yt**: **Саммари YouTube**. Отправьте ссылку на видео для получения структурированного пересказа и озвучки (TTS).

### Технические детали

*   **Архитектура**: Использование роутеров `aiogram` и FSM для управления состоянием диалогов.
*   **Интеграция OpenAI**:
    *   Модель `gpt-4o-mini` для баланса скорости и цены.
    *   **Надежность**: Система повторных запросов (retries) при ошибках API.
    *   **TTS**: Увеличенный таймаут (60с) для генерации голоса.
*   **RAG Система**:
    *   Поддержка `.pdf`, `.txt`, `.md`.
    *   Умное разбиение текста на фрагменты (chunking) с перекрытием.
    *   Улучшенная токенизация для поддержки русского и немецкого языков.
*   **YouTube Инструменты**:
    *   Надежный алгоритм получения транскриптов с несколькими стратегиями (Static API, List API, fallback), чтобы избежать сбоев библиотеки.

### Установка

1.  **Клонирование репозитория**:
    ```bash
    git clone <repo_url>
    ```

2.  **Создание виртуального окружения**:
    ```bash
    python -m venv .venv
    .\.venv\Scripts\Activate  # Windows
    ```

3.  **Установка зависимостей**:
    ```bash
    pip install -r requirements
    ```

4.  **Конфигурация**:
    Создайте файл `.env` в корне проекта:
    ```env
    BOT_TOKEN=Ваш_Telegram_Token
    OPENAI_API_KEY=Ваш_OpenAI_Key
    ```

5.  **Запуск**:
    ```bash
    python main.py
    ```

</details>
