"""FastAPI application entry point."""

from fastapi import FastAPI

from app.api.router import router

app = FastAPI(
    title="Financial Analytics Service",
    version="0.1.0",
    description="API for importing and analyzing personal financial transactions.",
)
app.include_router(router)