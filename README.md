# FitBuddy – AI Fitness Plan Generator using Gemini Models

FitBuddy is a FastAPI + Jinja2 + SQLite web application that generates a personalized 7-day fitness plan, gives a goal-aligned nutrition/recovery tip, and lets the user revise the plan through feedback.

## Reference basis

This implementation follows the uploaded SmartBridge project document: user profile input, 7-day workout generation, nutrition/recovery tip, feedback-based plan update, SQLite persistence, admin view, FastAPI/Jinja2 UI, and local deployment. It also follows the interaction style demonstrated by the supplied reference video:

- Video: https://youtu.be/d2rKynGKtW8
- Project document: `FitBuddy – AI Fitness Plan Generator using Gemini Models(4).docx`

## Modernized AI stack

The original document names Gemini 1.5 Pro and Gemini Flash and installs the legacy `google-generativeai` package. This project uses Google's current `google-genai` SDK with structured JSON responses. The selected models are configurable through `.env` so the project can stay aligned with the document while allowing current model IDs.

Default model configuration:

- `GEMINI_WORKOUT_MODEL=gemini-2.5-pro` – richer generation/revision
- `GEMINI_TIP_MODEL=gemini-2.5-flash` – fast nutrition/recovery tip

The application has a `DEMO_MODE=true` fallback so the full UI/database flow can be tested without an API key. Set `DEMO_MODE=false` and add `GEMINI_API_KEY` to enable live Gemini calls.

## Features

1. Personalized 7-day workout plan based on name, age, weight, goal and intensity.
2. Warm-up, exercise, sets/reps or duration, rest and cooldown/recovery guidance.
3. Short nutrition/recovery tip generated separately.
4. Feedback-based plan regeneration that preserves the latest plan.
5. SQLite database using SQLAlchemy.
6. Responsive Jinja2 frontend inspired by the dark, fitness-focused reference UI.
7. Admin dashboard with HTTP Basic Authentication.
8. JSON APIs plus browser pages.
9. Input validation and friendly error handling.
10. Automated tests and GitHub Actions CI.

## Project structure

```text
fitbuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── crud.py
│   ├── ai_service.py
│   └── routes.py
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── result.html
│   ├── admin_login.html
│   └── all_users.html
├── static/
│   ├── css/styles.css
│   └── js/app.js
├── tests/test_app.py
├── docs/phases/phase-1-brainstorming.md
├── docs/phases/phase-2-requirements.md
├── docs/phases/phase-3-design.md
├── docs/phases/phase-4-planning.md
├── docs/phases/phase-5-development.md
├── docs/phases/phase-6-testing.md
├── docs/phases/phase-7-documentation.md
├── docs/phases/phase-8-demonstration.md
├── .env.example
├── .gitignore
├── requirements.txt
└── run.py
```

## VS Code setup – Windows

### 1. Install Python

Use Python 3.11+ and verify:

```powershell
python --version
```

### 2. Open the folder in VS Code

```powershell
cd fitbuddy
code .
```

### 3. Create and activate a virtual environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Create the environment file

```powershell
Copy-Item .env.example .env
```

For an immediate offline demo, keep:

```env
DEMO_MODE=true
```

For real Gemini generation:

```env
DEMO_MODE=false
GEMINI_API_KEY=your_real_key_here
```

### 6. Run the application

```powershell
python run.py
```

Or:

```powershell
uvicorn app.main:app --reload
```

Open:

- App: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Admin: http://127.0.0.1:8000/view-all-users

Default admin credentials are defined in `.env.example` and should be changed for real use.

## How to test the application manually

1. Open the home page.
2. Enter a name, unique user ID, age, weight, fitness goal and intensity.
3. Click **Generate My Plan**.
4. Confirm the 7 daily cards and nutrition/recovery tip are displayed.
5. Submit feedback such as `Add more cardio and give me an extra rest day.`
6. Confirm the updated plan replaces the active plan and the original plan remains stored.
7. Open the admin dashboard and verify the user record.
8. Use `/docs` to exercise the JSON endpoints.

## Automated tests

```powershell
pytest -q
```

The tests force demo mode, so they do not spend Gemini API quota.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Home page |
| POST | `/generate-workout` | Browser form → generate plan |
| POST | `/submit-feedback` | Browser form → revise plan |
| GET | `/view-all-users` | Authenticated admin page |
| POST | `/api/plans` | JSON plan generation |
| POST | `/api/plans/{user_id}/feedback` | JSON plan revision |
| GET | `/api/users` | Authenticated user list |
| DELETE | `/api/users/{user_id}` | Authenticated delete |
| GET | `/health` | Health check |

## Safety note

FitBuddy is a wellness planning demo, not a medical device or personal medical advice service. AI prompts explicitly ask for conservative, general wellness guidance and to suggest professional evaluation where pain, injury or a medical condition is involved.

## GitHub phase submission

The SmartBridge instructions in the supplied project document ask for eight phase-wise submissions. The `docs/phases/` directory provides one markdown artifact for each phase, ready to commit into a public repository.
