from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from src.utils.logger_config import logger
from src.routes import api_routes
from src.routes.timetable_routes import router as timetable_router
from src.routes.dynamic_reallocation_routes import router as reallocation_router
# from src.routes.auth_routes import router as auth_router
from contextlib import asynccontextmanager
from src.utils.prisma import db
# from src.utils.config import DEBUG
import sys
from pathlib import Path

# Ensure project root is in Python path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("attempting to connect to db...")
    await db.connect()
    logger.info("connected to db.")
    yield
    logger.info("application stopped.")
    await db.disconnect()
    logger.info("disconnected from db.")

app = FastAPI(lifespan=lifespan)

# CORS: allow specific origins from env FRONTEND_URL and comma-separated CORS_ORIGINS
frontend_url = os.getenv("FRONTEND_URL")
cors_origins_env = os.getenv("CORS_ORIGINS", "")
origins = []
if frontend_url:
    origins.append(frontend_url)
if cors_origins_env:
    origins.extend([o.strip() for o in cors_origins_env.split(",") if o.strip()])

if not origins:
    # fallback for local dev
    origins = ["http://localhost:3000", "http://127.0.0.1:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_routes, prefix="/api")
app.include_router(timetable_router, prefix="/api")
app.include_router(reallocation_router, prefix="/api/dynamic-reallocation")
# app.include_router(auth_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "running the server"
    }