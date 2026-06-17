# ReMind Backend

ReMind is a flashcard learning application powered by a Spaced Repetition system to optimize memory retention.

##  Tech Stack
- **Backend:** Django & Django Rest Framework (DRF)
- **Database:** PostgreSQL
- **Caching & Queue:** Redis & Django-RQ

## Installation


### Option 1: Using Docker (Recommended)

1. Clone the repository
2. Create a `.env` file based on `.env.template`:
   ```bash
   cp .env.template .env
   ```
3. Update the `.env` file with your configuration values
4. Build and start the containers:
   ```cmd
   docker compose up --build
   ```

The backend will be available at `http://localhost:8000`

### Option 2: Local Setup

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv env
   "env\Scripts\activate"  # On Windows
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file based on `.env.template`
5. Set up the database:
   ```bash
   python manage.py migrate
   ```
6. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
7. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## Quick Start

### Start the Application

```cmd
docker compose up --build
```

### Run Migrations

```cmd
docker compose exec web python manage.py migrate
```

### Create a Superuser

```cmd
docker compose exec web python manage.py createsuperuser
```

### Access the Admin Panel

Navigate to `http://localhost:8000/admin` and log in with your superuser credentials.

---

## Configuration

### Environment Variables

Copy the `.env.template` file to `.env` and update the values according to your setup:

```bash
cp .env.template .env
```

| Variable | Description |
|----------|-------------|
| `DJANGO_SUPERUSER_USERNAME` | Default superuser username |
| `DJANGO_SUPERUSER_PASSWORD` | Default superuser password |
| `DJANGO_SUPERUSER_EMAIL` | Default superuser email address |
| `SECRET_KEY` | Django secret key for cryptographic operations |
| `DEBUG` | Enable/disable Django debug mode (set to `False` in production) |
| `ALLOWED_HOSTS` | Comma-separated list of allowed host addresses |
| `CSRF_TRUSTED_ORIGINS` | Comma-separated list of trusted origins for CSRF protection |
| `DB_NAME` | PostgreSQL database name |
| `DB_USER` | PostgreSQL database user |
| `DB_PASSWORD` | PostgreSQL database password |
| `DB_HOST` | PostgreSQL host address |
| `DB_PORT` | PostgreSQL port number |
| `REDIS_HOST` | Redis server hostname |
| `REDIS_LOCATION` | Redis connection URL for caching |
| `REDIS_PORT` | Redis port number |
| `REDIS_DB` | Redis database number |
| `EMAIL_HOST` | SMTP server for sending emails |
| `EMAIL_PORT` | SMTP port (typically 587 or 465) |
| `EMAIL_HOST_USER` | SMTP authentication username |
| `EMAIL_HOST_PASSWORD` | SMTP authentication password |
| `EMAIL_USE_TLS` | Enable TLS encryption for SMTP |
| `EMAIL_USE_SSL` | Enable SSL encryption for SMTP |
| `DEFAULT_FROM_EMAIL` | Sender email address for application emails |
| `USE_EMAIL_FILE_BACKEND` | Set to `True` to save emails locally instead of sending them (DEBUG must be True) |
| `FRONTEND_BASE_URL` | Base URL for frontend application |


---