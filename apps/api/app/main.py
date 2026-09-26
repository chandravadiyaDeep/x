from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import init_db
from app.routes import cleaning, datasets, health, readiness, reports

app = FastAPI(
    title="NUMPA API",
    description="Backend for NUMPA's Smart Data Cleaning and ML Readiness Assessment workflow.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    init_db()


app.include_router(health.router)
app.include_router(datasets.router, prefix="/v1/datasets", tags=["datasets"])
app.include_router(readiness.router, prefix="/v1/readiness", tags=["readiness"])
app.include_router(cleaning.router, prefix="/v1/cleaning", tags=["cleaning"])
app.include_router(reports.router, prefix="/v1/reports", tags=["reports"])
