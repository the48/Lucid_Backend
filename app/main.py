from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer
import uvicorn
import logging
from contextlib import asynccontextmanager

from database import engine, Base
from controllers.user_controller import router as user_router
from services.cache_service import cache_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FastAPI MVC Application")
    
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise
    
    yield
    
    logger.info("Shutting down FastAPI MVC Application")
    
    try:
        cache_service.clear_expired()
        logger.info("Cache cleared successfully")
    except Exception as e:
        logger.error(f"Failed to clear cache: {e}")

app = FastAPI(
    title ="FastAPI Backend Project",
    description = "A FastAPI Application with MVC, DI, JWTs, ORM",
    version = "1.0.0",
    docs_url = "/docs",
    redoc_url = "/redoc",
    lifespan = lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(user_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "path": str(request.url.path)
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code = 500,
        content={
            "error": "Internal server error",
            "status_code": 500,
            "path": str(request.url.path)
        }
    )

@app.get("/")
async def root():
    """
    General Information
    """
    return {
        "message": "Lucid Technologies Backend Developer Technical Assessment",
        "version": "1.0.48",
        "docs": "/docs",
        "health": "/api/health",
        "author": "Jack"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host = "0.0.0.0",
        port = 8000,
        reload = False,
        log_level = "info"
    )