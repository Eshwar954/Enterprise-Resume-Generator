from fastapi import FastAPI
from backend.app.api.routes.auth import router as auth_router
from backend.app.api.routes.health import router as health_router
from backend.app.database import create_tables

app=FastAPI(
    title="Enterprise-resume-agent",
    version="1.0"
)


@app.get("/")
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
def startup():
    create_tables()


app.include_router(health_router)
app.include_router(auth_router)
