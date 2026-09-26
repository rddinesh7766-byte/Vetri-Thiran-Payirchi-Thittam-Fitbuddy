import os

os.environ["DEMO_MODE"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///./data/test_fitbuddy.db"
os.environ["ADMIN_USERNAME"] = "admin"
os.environ["ADMIN_PASSWORD"] = "fitbuddy123"

from fastapi.testclient import TestClient

from app.main import app
from app.database import Base, engine


Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)
client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_home_page():
    response = client.get("/")
    assert response.status_code == 200
    assert "FitBuddy" in response.text


def test_generate_plan_and_feedback_flow():
    payload = {
        "username": "Dinesh",
        "user_id": "demo001",
        "age": 19,
        "weight": 68,
        "goal": "muscle gain",
        "intensity": "medium",
    }
    response = client.post("/api/plans", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["workout_plan"]["days"]) == 7
    assert data["nutrition_tip"]

    feedback = {"user_id": "demo001", "feedback": "Add more cardio and an extra rest day."}
    update_response = client.post("/api/plans/demo001/feedback", json=feedback)
    assert update_response.status_code == 200
    assert len(update_response.json()["workout_plan"]["days"]) == 7


def test_admin_view_and_delete():
    auth = ("admin", "fitbuddy123")
    response = client.get("/api/users", auth=auth)
    assert response.status_code == 200
    assert any(item["user_id"] == "demo001" for item in response.json())

    delete_response = client.delete("/api/users/demo001", auth=auth)
    assert delete_response.status_code == 200

    missing = client.delete("/api/users/demo001", auth=auth)
    assert missing.status_code == 404
