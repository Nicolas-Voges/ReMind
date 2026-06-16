# ReMind Backend

ReMind is a flashcard learning application powered by a Spaced Repetition system to optimize memory retention.

## 🛠️ Tech Stack
- **Backend:** Django & Django Rest Framework (DRF)
- **Database:** PostgreSQL
- **Caching & Queue:** Redis & Django-RQ

## 🚀 Getting Started

Make sure **Docker Desktop** is running in the background.

1. Create a `.env` file in the root directory based on the `.env.template` file.
2. Start the Docker containers in live-log mode:
   ```bash
   docker compose up --build
   ```
3. The server will be up and running at `http://localhost:8000`. A Django admin superuser is automatically generated on the first startup.