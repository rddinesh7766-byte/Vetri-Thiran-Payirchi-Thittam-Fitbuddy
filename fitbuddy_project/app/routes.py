import json
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from . import crud
from .ai_service import generate_nutrition_tip, generate_workout_plan, revise_workout_plan
from .config import settings
from .database import get_db
from .schemas import FeedbackRequest, UserInput

router = APIRouter()
security = HTTPBasic()
templates = Jinja2Templates(directory="templates")


def admin_guard(credentials: HTTPBasicCredentials) -> str:
    valid = credentials.username == settings.admin_username and credentials.password == settings.admin_password
    if not valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin credentials",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username


def _render_result(request: Request, user, plan, nutrition_tip, updated=False, message=None):
    return templates.TemplateResponse(
        request=request,
        name="result.html",
        context={
            "user": user,
            "plan": plan,
            "nutrition_tip": nutrition_tip,
            "updated": updated,
            "message": message,
        },
    )


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={"error": None})


@router.post("/generate-workout", response_class=HTMLResponse)
def generate_workout_form(
    request: Request,
    username: str = Form(...),
    user_id: str = Form(...),
    age: int = Form(...),
    weight: float = Form(...),
    goal: str = Form(...),
    intensity: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        data = UserInput(
            username=username,
            user_id=user_id,
            age=age,
            weight=weight,
            goal=goal,
            intensity=intensity,
        )
        user = crud.save_user(db, data)
        plan = generate_workout_plan(data)
        tip = generate_nutrition_tip(data.goal)
        stored = crud.save_plan(db, data.user_id, plan.model_dump_json(), tip)
        return _render_result(request, user, plan, tip, updated=False, message="Your personalized plan is ready.")
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error": str(exc)},
            status_code=400,
        )


@router.post("/submit-feedback", response_class=HTMLResponse)
def submit_feedback_form(
    request: Request,
    user_id: str = Form(...),
    feedback: str = Form(...),
    db: Session = Depends(get_db),
):
    try:
        req = FeedbackRequest(user_id=user_id, feedback=feedback)
        user = crud.get_user_with_plan(db, req.user_id)
        if user is None or user.plan is None:
            raise ValueError("User ID not found. Generate a plan first.")
        current_json = user.plan.updated_plan or user.plan.original_plan
        current_plan = json.loads(current_json)
        from .schemas import WorkoutPlan
        revised = revise_workout_plan(WorkoutPlan.model_validate(current_plan), req.feedback)
        crud.update_plan(db, req.user_id, revised.model_dump_json(), req.feedback)
        return _render_result(
            request,
            user,
            revised,
            user.plan.nutrition_tip,
            updated=True,
            message="Your plan has been updated using your feedback.",
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/view-all-users", response_class=HTMLResponse)
def view_all_users(
    request: Request,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    admin_guard(credentials)
    users = crud.get_all_users(db)
    return templates.TemplateResponse(
        request=request,
        name="all_users.html",
        context={"users": users},
    )


@router.post("/api/plans")
def api_generate_plan(data: UserInput, db: Session = Depends(get_db)):
    try:
        user = crud.save_user(db, data)
        plan = generate_workout_plan(data)
        tip = generate_nutrition_tip(data.goal)
        crud.save_plan(db, data.user_id, plan.model_dump_json(), tip)
        return {"user": data.model_dump(), "workout_plan": plan.model_dump(), "nutrition_tip": tip}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/api/plans/{user_id}/feedback")
def api_update_plan(user_id: str, data: FeedbackRequest, db: Session = Depends(get_db)):
    if user_id != data.user_id:
        raise HTTPException(status_code=400, detail="Path user_id and body user_id must match.")
    user = crud.get_user_with_plan(db, user_id)
    if user is None or user.plan is None:
        raise HTTPException(status_code=404, detail="User or plan not found.")
    current_json = user.plan.updated_plan or user.plan.original_plan
    from .schemas import WorkoutPlan
    revised = revise_workout_plan(WorkoutPlan.model_validate_json(current_json), data.feedback)
    crud.update_plan(db, user_id, revised.model_dump_json(), data.feedback)
    return {"user_id": user_id, "workout_plan": revised.model_dump(), "nutrition_tip": user.plan.nutrition_tip}


@router.get("/api/users")
def api_users(
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    admin_guard(credentials)
    users = crud.get_all_users(db)
    return [
        {
            "user_id": user.user_id,
            "username": user.username,
            "age": user.age,
            "weight": user.weight,
            "goal": user.goal,
            "intensity": user.intensity,
            "has_updated_plan": bool(user.plan and user.plan.updated_plan),
            "created_at": user.created_at.isoformat() if user.created_at else None,
        }
        for user in users
    ]


@router.delete("/api/users/{user_id}")
def api_delete_user(
    user_id: str,
    credentials: HTTPBasicCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    admin_guard(credentials)
    deleted = crud.delete_user(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found.")
    return JSONResponse({"message": f"User {user_id} deleted."})
