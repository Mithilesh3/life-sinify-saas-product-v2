from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
import traceback
import logging

from app.db.session import engine, Base
import app.db.models  # ensures models register

from app.modules.users.router import router as users_router
from app.modules.reports.router import router as reports_router
from app.modules.payments.router import router as payments_router
from app.modules.admin.router import router as admin_router

from app.core.config import settings


# =====================================================
# LOGGER
# =====================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(title=settings.APP_NAME)


# =====================================================
# CORS
# =====================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =====================================================
# GLOBAL ERROR HANDLER
# =====================================================

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):

    # Print full stack trace
    logger.error("Unhandled Exception:")
    traceback.print_exc()

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "message": "Internal Server Error"
        },
    )


# =====================================================
# STARTUP INITIALIZATION
# =====================================================

@app.on_event("startup")
def startup_event():

    try:

        # CREATE TABLES
        Base.metadata.create_all(bind=engine)

        # Ensure backward-compatible schema for existing deployments.
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE reports ADD COLUMN IF NOT EXISTS updated_at TIMESTAMPTZ")
            )
            connection.execute(text("SELECT 1"))

        logger.info("✅ Database connected.")
        logger.info("✅ Tables created successfully.")

    except Exception as e:

        logger.error("❌ Database initialization failed")
        traceback.print_exc()

        raise RuntimeError("Database initialization failed") from e


# =====================================================
# ROUTERS
# =====================================================

app.include_router(users_router, prefix="/api/users")
app.include_router(reports_router, prefix="/api/reports")
app.include_router(payments_router, prefix="/api/payments")
app.include_router(admin_router, prefix="/api/admin")


# =====================================================
# ROOT
# =====================================================

@app.get("/")
def root():

    return {
        "status": "Running",
        "engine_version": settings.ENGINE_VERSION
    }


# =====================================================
# HEALTH
# =====================================================

@app.get("/health")
def health_check():

    try:

        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        db_status = "connected"

    except SQLAlchemyError:

        db_status = "disconnected"

    return {
        "status": "healthy",
        "database": db_status
    }
