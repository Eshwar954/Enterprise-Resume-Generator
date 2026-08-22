import logging

from fastapi import FastAPI

from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.health import router as health_router
from backend.app.api.routes.resume import router as resume_router
from backend.app.core.logging import RequestLoggingMiddleware, configure_logging
from backend.app.database import create_tables

configure_logging()
logger = logging.getLogger("app.main")

app = FastAPI(
    title="Enterprise-resume-agent",
    version="1.0"
)

app.add_middleware(RequestLoggingMiddleware)


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def startup():
    create_tables()
    logger.info("startup_complete")


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(resume_router)