from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .database import init_db
from .routes import router

ROOT_DIR = Path(__file__).resolve().parents[1]


@asynccontextmanager
async def lifespan(app: FastAPI):
    (ROOT_DIR / "data").mkdir(parents=True, exist_ok=True)
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="AI-powered 7-day fitness plan generator based on the SmartBridge FitBuddy project specification.",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=ROOT_DIR / "static"), name="static")
app.include_router(router)


@app.get("/health")
def health():
    return {"status": "ok", "app": settings.app_name, "demo_mode": settings.demo_mode}
