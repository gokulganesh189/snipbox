# SnipBox

A short note saving API built with Django REST Framework. Save snippets, group them by tags, and manage everything through a clean JWT-authenticated REST API.

---

## Tech Stack

- **Python 3.12** / **Django 4.2**
- **Django REST Framework** – API layer
- **Simple JWT** – token-based authentication
- **MySQL 8** – primary database
- **Redis 7** – response caching
- **drf-spectacular** – auto-generated OpenAPI docs

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
│   └── SnipBox.postman_collection.json
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
git clone https://github.com/your-username/snipbox.git
cd snipbox

# 2. Create and activate a virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Open .env and set your SECRET_KEY, DB credentials, REDIS_URL

# 5. Create the MySQL database
mysql -u root -p -e "CREATE DATABASE snipbox CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
mysql -u root -p -e "CREATE USER 'snipbox_user'@'localhost' IDENTIFIED BY 'snipbox_pass';"
mysql -u root -p -e "GRANT ALL PRIVILEGES ON snipbox.* TO 'snipbox_user'@'localhost'; FLUSH PRIVILEGES;"

# 6. Apply migrations
python manage.py migrate

# 7. Create a superuser (optional, for /admin)
python manage.py createsuperuser

# 8. Run the development server
python manage.py runserver
```

The API will be available at `http://127.0.0.1:8000/api/`.

---

## Running with Docker

```bash
# 1. Copy and edit the env file
cp .env.example .env

# 2. Build and start all services
docker-compose up --build

# 3. In a separate terminal, create a superuser
docker-compose exec web python manage.py createsuperuser
```

All three services (MySQL, Redis, Django) will start with health checks and proper dependency ordering.

---

## Running Tests

```bash
python manage.py test apps
```

Tests use Django's built-in test runner with an in-memory SQLite DB so they run without MySQL. Redis calls are gracefully ignored during tests (IGNORE_EXCEPTIONS=True).

---

## API Reference

Interactive docs are available at:
- **Swagger UI** – `http://localhost:8000/api/docs/`
- **ReDoc** – `http://localhost:8000/api/redoc/`

### Endpoints Summary

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/login/` | Obtain JWT token pair | ❌ |
| POST | `/api/auth/token/refresh/` | Refresh access token | ❌ |
| GET | `/api/snippets/` | Overview: count + snippet list | ✅ |
| POST | `/api/snippets/create/` | Create a snippet | ✅ |
| GET | `/api/snippets/<id>/` | Snippet detail | ✅ |
| PUT | `/api/snippets/<id>/` | Update a snippet | ✅ |
| DELETE | `/api/snippets/<id>/` | Delete a snippet | ✅ |
| GET | `/api/tags/` | List all tags | ✅ |
| GET | `/api/tags/<id>/` | Tag detail + linked snippets | ✅ |

See [`docs/curl_examples.md`](docs/curl_examples.md) for request/response examples, or import [`docs/SnipBox.postman_collection.json`](docs/SnipBox.postman_collection.json) into Postman.

---

## Caching Strategy

Redis caches are applied at the view level with per-user scoping for snippet lists. Cache is invalidated on any write operation (create, update, delete). TTLs are configured in `settings.py` and easy to tune without touching view code.

| Cache Key Pattern | TTL |
|---|---|
| `snipbox:snippets:list:user:<id>` | 5 minutes |
| `snipbox:snippets:detail:<id>` | 10 minutes |
| `snipbox:tags:list` | 30 minutes |
| `snipbox:tags:detail:<id>` | 15 minutes |

---

## Commit Convention

Each endpoint has its own commit following the pattern:

```
feat(auth): add login and JWT token refresh endpoints
feat(snippets): add overview API with total count and hyperlinks
feat(snippets): add create snippet endpoint with tag resolution
feat(snippets): add detail, update, and delete endpoints
feat(tags): add tag list and tag detail endpoints
feat(cache): integrate Redis caching across all read endpoints
chore(docker): add Dockerfile and docker-compose configuration
docs: add README, curl examples, and Postman collection
```

---

## Database Schema

```
User (Django built-in)
 └── id, username, email, password, ...

Tag
 └── id  : BigInt PK
 └── title : VARCHAR(100) UNIQUE

Snippet
 └── id         : BigInt PK
 └── title      : VARCHAR(255)
 └── note       : TEXT
 └── created_at : DATETIME (auto)
 └── updated_at : DATETIME (auto)
 └── created_by : FK → User (CASCADE)

Snippet_Tags (M2M join)
 └── snippet_id : FK → Snippet
 └── tag_id     : FK → Tag
```
