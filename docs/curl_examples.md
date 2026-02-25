# SnipBox API – cURL Examples

All requests assume the server is running at `http://localhost:8000`.
Replace `<ACCESS_TOKEN>` and `<REFRESH_TOKEN>` with values from the login response.

---

## Authentication

### Register User
```bash
curl -s -X POST http://localhost:8000/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice.bob.user", "password": "Alice@789Bob", "confirm_password": "Alice@789Bob"}' | python3 -m json.tool
```

### Register User Staff
```bash
curl -s -X POST http://localhost:8000/accounts/register/staff/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice.bob.staff", "password": "Alice@789Bob", "confirm_password": "Alice@789Bob"}' | python3 -m json.tool
```

### Register User Admin
```bash
curl -s -X POST http://localhost:8000/accounts/register/superuser/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice.bob.admin", "password": "Alice@789Bob", "confirm_password": "Alice@789Bob"}' | python3 -m json.tool
```

### Login
```bash
curl -s -X POST http://localhost:8000/accounts/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "alice.bob.user", "password": "Alice@789Bob"}' | python3 -m json.tool
```

### Refresh Token
```bash
curl -s -X POST http://localhost:8000/accounts/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "<REFRESH_TOKEN>"}' | python3 -m json.tool
```

---

## Snippets

### Overview (total count + list)
```bash
curl -s http://localhost:8000/snippet/overview/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" | python3 -m json.tool
```

### Create Snippet
```bash
curl -s -X POST http://localhost:8000/snippet/create/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Quick note", "note": "Test Note", "tag_titles": ["Test"]}' \
  | python3 -m json.tool
```

### Snippet Detail
```bash
curl -s http://localhost:8000/snippets/1/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" | python3 -m json.tool
```

### Update Snippet
```bash
curl -s -X PUT http://localhost:8000/snippets/1/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated note", "note": "New content here.", "tag_titles": ["updated"]}' \
  | python3 -m json.tool
```

### Delete Snippet
```bash
curl -s -X DELETE http://localhost:8000/snippets/1/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" | python3 -m json.tool
```

---

## Tags

### Tag List
```bash
curl -s http://localhost:8000/tags/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" | python3 -m json.tool
```

### Tag Detail (with linked snippets)
```bash
curl -s http://localhost:8000/tags/1/ \
  -H "Authorization: Bearer <ACCESS_TOKEN>" | python3 -m json.tool
```

