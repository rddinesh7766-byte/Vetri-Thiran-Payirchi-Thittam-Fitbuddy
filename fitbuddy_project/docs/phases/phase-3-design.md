# Phase 3 – Project Design

```text
Browser (Jinja2 HTML/CSS/JS)
          |
          v
      FastAPI routes
      /          \
     /            \
 SQLite/ORM     Gemini AI layer
      |             |
 users + plans   workout + tip + revision
```

## Main modules
- `main.py` – application startup/static files.
- `routes.py` – browser and API endpoints.
- `schemas.py` – Pydantic validation and structured AI schema.
- `ai_service.py` – Gemini integration and demo fallback.
- `crud.py` – database operations.
- `models.py` – SQLAlchemy entities.
