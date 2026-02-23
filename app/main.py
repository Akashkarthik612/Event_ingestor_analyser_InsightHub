from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.api.v1.api_router import api_router
from app.db.base import Base
from app.db.session import engine
# Import all models to register them with Base
import app.db.models  # noqa: F401


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    Base.metadata.create_all(bind=engine)
    print("🚀 InsightHub API Started")
    yield
    # Shutdown
    pass


def create_application() -> FastAPI:
    app = FastAPI(
        title="InsightHub",
        description="Real-time Event Ingestion & Analytics Platform",
        version="1.0.0",
        lifespan=lifespan,
    )

    # CORS (important later for frontend)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten later
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include versioned API
    app.include_router(api_router, prefix="/api/v1")

    return app


app = create_application()


@app.get("/")
def root():
    return {"message": "InsightHub API is running"}


@app.get("/health")
def health():
    """Basic health-check endpoint used by CI/tests."""
    return {"status": "ok"}
