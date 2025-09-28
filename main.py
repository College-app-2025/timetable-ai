from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.utils.logger_config import logger
from src.routes import api_routes
from src.routes.timetable_routes import router as timetable_router
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
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

app.include_router(api_routes, prefix="/api")
app.include_router(timetable_router, prefix="/api")
# app.include_router(auth_router, prefix="/api")


@app.get("/")
async def root():
    return {
        "message": "running the server"
    }