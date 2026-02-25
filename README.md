# SnipBox

A short note saving API built with Django REST Framework. Save snippets, group them by tags, and manage everything through a clean JWT-authenticated REST API.

# Postman Link `https://blue-desert-854758.postman.co/workspace/Default-workspace~d8892630-c060-4c3e-a436-c2cff212ae14/collection/25064619-2526a903-8edd-47b5-9155-699f1be0a430?action=share&creator=25064619&active-environment=25064619-63772d63-714d-4462-b301-4c582025873f`

---

## Tech Stack

- **Python 3.12** / **Django 6.0**
- **Django REST Framework** – API layer
- **Simple JWT** – token-based authentication
- **MySQL 8** – primary database
- **Redis 7** – response caching

---

## Project Structure

```
snipbox/
├── apps/
│   ├── authentication/      # Login + token refresh
│   └── snippets/            # Snippet & Tag CRUD + caching
├── snipbox/                 # Django project config
├── docs/
│   ├── curl_examples.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

---

## Local Setup (without Docker)

### Prerequisites

- Python 3.12+
- MySQL 8.0 running locally
- Redis 7 running locally

### Steps

```bash
# 1. Clone and enter the project
git clone https://github.com/gokulganesh189/snipbox.git
cd snipbox

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
make sure secrets.json is in root

# 5. Apply migrations
python manage.py migrate

# 6. Create a superuser (optional, for /admin)
python manage.py createsuperuser

# 8. Run the development server
python manage.py runserver
```

The API will be available at `http://localhost:8000/`.

---

## Running with Docker

```bash
# 1. Copy and edit the env file
make sure secrets.json is in root

# 2. Build and start all services
docker-compose up --build

# 3. In a separate terminal, create a superuser
docker-compose exec snip_box_backend python manage.py createsuperuser
```

All three services (MySQL, Redis, Django) will start with health checks and proper dependency ordering.

---

## Running Tests

```bash
docker exec -it snip_box_backend sh
python manage.py test
```

Tests use Django's built-in test runner with an in-memory SQLite DB so they run without MySQL. Redis calls are gracefully ignored during tests (IGNORE_EXCEPTIONS=True).

---

### Endpoints Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `acounts/login/` | Obtain JWT token pair | ❌ |
| POST | `accounts/token/refresh/` | Refresh access token | ❌ |
| GET | `snippet/overview/` | Overview: count + snippet list | ✅ |
| POST | `snippet/create/` | Create a snippet | ✅ |
| GET | `snippet/<id>/` | Snippet detail | ✅ |
| PUT | `snippet/<id>/` | Update a snippet | ✅ |
| DELETE | `snippet/<id>/` | Delete a snippet | ✅ |
| GET | `tags/` | List all tags | ✅ |
| GET | `tags/<id>/` | Tag detail + linked snippets | ✅ |


---

## Caching Strategy

Redis caches are applied at the view level with per-user scoping for snippet lists. Cache is invalidated on any write operation (create, update, delete). TTLs are configured in `settings.py` because of this no need to change in views.

| Cache Key Pattern | TTL |
|---|---|
| `snipbox:1:snippets:list:user:<user_id>` | 5 minutes |
| `snipbox:1:snippets:detail:<user_id>:<snippet_id>` | 10 minutes |
| `snipbox:1:tags:list` | 30 minutes |
| `snipbox:1:tags:detail:<tag_id>:<user_id>` | 15 minutes |

---

## Database Schema

```
User (Django built-in)
 └── id, username, email, password, ...

Tag
 └── id  : Int PK
 └── title : VARCHAR(100) UNIQUE

Snippet
 └── id         : Int PK
 └── title      : VARCHAR(255)
 └── note       : TEXT
 └── created_on : DATETIME (auto)
 └── updated_on : DATETIME (auto)
 └── created_by : FK → User (CASCADE)

Snippet_Tags (M2M join)
 └── snippet_id : FK → Snippet
 └── tag_id     : FK → Tag
```
