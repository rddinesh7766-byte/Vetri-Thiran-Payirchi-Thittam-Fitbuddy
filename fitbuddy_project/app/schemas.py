from typing import Literal

from pydantic import BaseModel, Field, field_validator

Goal = Literal["weight loss", "muscle gain", "general wellness", "strength", "flexibility"]
Intensity = Literal["low", "medium", "high"]


class UserInput(BaseModel):
    username: str = Field(min_length=2, max_length=100)
    user_id: str = Field(min_length=2, max_length=64, pattern=r"^[A-Za-z0-9_-]+$")
    age: int = Field(ge=13, le=100)
    weight: float = Field(gt=20, le=300)
    goal: Goal
    intensity: Intensity

    @field_validator("username", "user_id", mode="before")
    @classmethod
    def strip_strings(cls, value: str) -> str:
        return value.strip()


class FeedbackRequest(BaseModel):
    user_id: str = Field(min_length=2, max_length=64)
    feedback: str = Field(min_length=5, max_length=1200)


class Exercise(BaseModel):
    name: str
    sets: str
    reps_or_duration: str
    rest: str
    notes: str = ""


class WorkoutDay(BaseModel):
    day: str
    focus: str
    duration_minutes: int = Field(ge=10, le=240)
    warm_up: str
    exercises: list[Exercise]
    cool_down: str
    recovery: str


class WorkoutPlan(BaseModel):
    overview: str
    days: list[WorkoutDay] = Field(min_length=7, max_length=7)
    weekly_notes: list[str] = Field(min_length=1, max_length=5)
