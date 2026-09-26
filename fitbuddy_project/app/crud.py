from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from .models import Plan, User
from .schemas import UserInput


def save_user(db: Session, data: UserInput) -> User:
    user = db.scalar(select(User).where(User.user_id == data.user_id))
    if user is None:
        user = User(
            user_id=data.user_id,
            username=data.username,
            age=data.age,
            weight=data.weight,
            goal=data.goal,
            intensity=data.intensity,
        )
        db.add(user)
    else:
        user.username = data.username
        user.age = data.age
        user.weight = data.weight
        user.goal = data.goal
        user.intensity = data.intensity
    db.commit()
    db.refresh(user)
    return user


def save_plan(
    db: Session,
    user_id: str,
    original_plan: str,
    nutrition_tip: str,
) -> Plan:
    plan = db.scalar(select(Plan).where(Plan.user_id == user_id))
    if plan is None:
        plan = Plan(
            user_id=user_id,
            original_plan=original_plan,
            nutrition_tip=nutrition_tip,
        )
        db.add(plan)
    else:
        plan.original_plan = original_plan
        plan.updated_plan = None
        plan.nutrition_tip = nutrition_tip
        plan.last_feedback = None
    db.commit()
    db.refresh(plan)
    return plan


def get_user_with_plan(db: Session, user_id: str) -> User | None:
    return db.scalar(
        select(User).options(joinedload(User.plan)).where(User.user_id == user_id)
    )


def update_plan(db: Session, user_id: str, revised_plan: str, feedback: str) -> Plan | None:
    plan = db.scalar(select(Plan).where(Plan.user_id == user_id))
    if plan is None:
        return None
    plan.updated_plan = revised_plan
    plan.last_feedback = feedback
    db.commit()
    db.refresh(plan)
    return plan


def get_original_plan(db: Session, user_id: str) -> str | None:
    plan = db.scalar(select(Plan).where(Plan.user_id == user_id))
    return plan.original_plan if plan else None


def get_all_users(db: Session) -> list[User]:
    return list(
        db.scalars(select(User).options(joinedload(User.plan)).order_by(User.created_at.desc())).unique().all()
    )


def delete_user(db: Session, user_id: str) -> bool:
    user = db.scalar(select(User).where(User.user_id == user_id))
    if user is None:
        return False
    db.delete(user)
    db.commit()
    return True
