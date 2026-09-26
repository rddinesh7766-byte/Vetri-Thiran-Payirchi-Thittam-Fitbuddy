import json
from functools import lru_cache

from google import genai
from google.genai import types

from .config import settings
from .schemas import UserInput, WorkoutPlan

SYSTEM_INSTRUCTION = """
You are FitBuddy, a conservative general-wellness fitness planning assistant.
Create practical beginner-friendly plans. Never diagnose conditions or prescribe treatment.
Do not recommend dangerous rapid weight loss, extreme fasting, dehydration, illegal drugs,
unsafe supplements, or training through sharp pain. For pain, injury, pregnancy, known
medical conditions, or other red flags, advise the user to consult a qualified professional.
Keep the plan realistic, progressive, and recoverable.
"""


def _demo_plan(data: UserInput) -> WorkoutPlan:
    goal = data.goal.title()
    intensity_note = {
        "low": "easy-to-moderate effort with extra recovery",
        "medium": "moderate effort with controlled progression",
        "high": "challenging effort while keeping safe technique and recovery",
    }[data.intensity]
    templates = [
        ("Day 1", "Full body foundation", ["Bodyweight squat", "Incline push-up", "Glute bridge"]),
        ("Day 2", "Cardio + core", ["Brisk walk", "Dead bug", "Bird dog"]),
        ("Day 3", "Upper body", ["Dumbbell row", "Shoulder press", "Wall push-up"]),
        ("Day 4", "Recovery + mobility", ["Easy walk", "Hip mobility", "Thoracic rotations"]),
        ("Day 5", "Lower body", ["Reverse lunge", "Romanian deadlift", "Calf raise"]),
        ("Day 6", "Conditioning", ["Step-ups", "Marching high knees", "Plank"]),
        ("Day 7", "Rest + flexibility", ["Gentle walk", "Full-body stretching", "Breathing drill"]),
    ]
    days = []
    for day, focus, exercises in templates:
        duration = 35 if "Recovery" in focus or day == "Day 7" else 45
        exercise_models = []
        for ex in exercises:
            if ex in {"Brisk walk", "Easy walk", "Gentle walk"}:
                sets, reps = "1", "20–30 min"
            elif ex in {"Hip mobility", "Thoracic rotations", "Full-body stretching", "Breathing drill"}:
                sets, reps = "2", "30–45 sec"
            else:
                sets, reps = "3", "8–12 reps"
            exercise_models.append(
                {"name": ex, "sets": sets, "reps_or_duration": reps, "rest": "45–75 sec", "notes": intensity_note}
            )
        days.append(
            {
                "day": day,
                "focus": focus,
                "duration_minutes": duration,
                "warm_up": "5–8 min easy movement + dynamic mobility.",
                "exercises": exercise_models,
                "cool_down": "5–8 min easy walking and gentle stretching.",
                "recovery": "Hydrate, sleep well, and stop if you feel sharp pain or unusual symptoms.",
            }
        )
    return WorkoutPlan(
        overview=f"Demo plan for {data.username}: {goal} with {data.intensity} intensity. This offline plan demonstrates the full FitBuddy workflow.",
        days=days,
        weekly_notes=[
            "Prioritize consistent technique over speed or load.",
            "Increase difficulty gradually only when the current level feels manageable.",
            "This is general wellness information, not medical advice.",
        ],
    )


@lru_cache(maxsize=1)
def get_client():
    if not settings.gemini_api_key:
        return None
    return genai.Client(api_key=settings.gemini_api_key)


def _generate_structured(prompt: str, model_name: str) -> WorkoutPlan:
    client = get_client()
    if client is None:
        raise RuntimeError("Gemini API key is not configured.")
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.6,
            response_mime_type="application/json",
            response_schema=WorkoutPlan,
        ),
    )
    if getattr(response, "parsed", None) is not None:
        return WorkoutPlan.model_validate(response.parsed)
    if response.text:
        return WorkoutPlan.model_validate_json(response.text)
    raise RuntimeError("Gemini returned an empty response.")


def generate_workout_plan(data: UserInput) -> WorkoutPlan:
    if settings.demo_mode:
        return _demo_plan(data)
    prompt = f"""
Create exactly a 7-day workout plan for this user.

Profile:
- Name: {data.username}
- Age: {data.age}
- Weight: {data.weight} kg
- Fitness goal: {data.goal}
- Workout intensity: {data.intensity}

Requirements:
- Return exactly 7 days.
- Every day must include warm-up, main exercises with sets and reps/duration, cooldown and recovery guidance.
- Make rest/recovery explicit.
- Avoid unsafe or excessively aggressive recommendations.
- Keep language concise and practical.
"""
    return _generate_structured(prompt, settings.gemini_workout_model)


def revise_workout_plan(current_plan: WorkoutPlan, feedback: str) -> WorkoutPlan:
    if settings.demo_mode:
        revised = current_plan.model_copy(deep=True)
        revised.overview = revised.overview + f" Updated from feedback: {feedback}"
        if "cardio" in feedback.lower():
            revised.days[1].focus = "Cardio + core (feedback update)"
            revised.days[1].exercises[0].name = "Brisk cardio walk / cycling"
        if "rest" in feedback.lower():
            revised.days[6].focus = "Rest + flexibility (feedback update)"
        return revised
    prompt = f"""
Revise the following FitBuddy 7-day plan using the user's feedback.

CURRENT PLAN:
{json.dumps(current_plan.model_dump(), ensure_ascii=False, indent=2)}

USER FEEDBACK:
{feedback}

Rules:
- Keep all useful details that were not requested to change.
- Implement the requested change conservatively.
- Still return exactly 7 days with the full schema.
"""
    return _generate_structured(prompt, settings.gemini_workout_model)


def generate_nutrition_tip(goal: str) -> str:
    if settings.demo_mode:
        tips = {
            "weight loss": "Build meals around protein, vegetables, whole-food carbohydrates and adequate water; use a sustainable calorie deficit rather than extreme restriction.",
            "muscle gain": "Include a protein-rich food at each meal and eat enough overall energy to support training and recovery.",
            "general wellness": "Aim for regular meals built from minimally processed foods and keep hydration consistent throughout the day.",
            "strength": "Pair resistance training with adequate protein, carbohydrates and hydration to support performance and recovery.",
            "flexibility": "Stay hydrated and include protein- and micronutrient-rich foods while keeping recovery and sleep consistent.",
        }
        return tips[goal]
    client = get_client()
    if client is None:
        raise RuntimeError("Gemini API key is not configured.")
    response = client.models.generate_content(
        model=settings.gemini_tip_model,
        contents=(
            f"Give one concise, actionable general nutrition or recovery tip for a fitness goal of '{goal}'. "
            "Keep it to 1–2 sentences. Do not give medical advice or extreme dieting guidance."
        ),
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            temperature=0.4,
            max_output_tokens=120,
        ),
    )
    text = (response.text or "").strip()
    if not text:
        raise RuntimeError("Gemini returned an empty nutrition tip.")
    return text


# Compatibility names matching the source project document.
generate_workout_gemini = generate_workout_plan
generate_nutrition_tip_with_flash = generate_nutrition_tip
update_workout_plan = revise_workout_plan
from google import genai

client = genai.Client(api_key=settings.gemini_api_key)

for model in client.models.list():
    print(model.name)