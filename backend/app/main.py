import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from app.api.v1.routers import (
    auth,
    company,
    accounting,
    partners,
    invoicing,
    repair,
    inventory,
    wallet,
    admin,
    treasury,
    purchases,
    users,
    dashboard,
)
from app.core.config import settings

# Configure structured logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("app")

app = FastAPI(title="Business Management System", version="0.1.0")

# Configure CORS with allowed origins from settings
import os
origins = [o.strip() for o in settings.ALLOWED_ORIGINS.split(",") if o.strip()]
logger.info(f"CORS allowed origins: {origins}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(company.router, prefix="/api/v1/companies", tags=["companies"])
app.include_router(accounting.router, prefix="/api/v1/accounting", tags=["accounting"])
app.include_router(partners.router, prefix="/api/v1/partners", tags=["partners"])
app.include_router(invoicing.router, prefix="/api/v1/invoicing", tags=["invoicing"])
app.include_router(repair.router, prefix="/api/v1/repair", tags=["repair"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["inventory"])
app.include_router(wallet.router, prefix="/api/v1/wallet", tags=["wallet"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["admin"])
app.include_router(treasury.router, prefix="/api/v1/treasury", tags=["treasury"])
app.include_router(purchases.router, prefix="/api/v1/purchases", tags=["purchases"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["dashboard"])

# Serve uploaded files
import os

try:
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
except PermissionError:
    logger.error(
        f"Cannot create upload directory '{settings.UPLOAD_DIR}'. "
        f"Ensure the directory exists and is writable by the application user. "
        f"Run: sudo chown -R <uid>:<gid> ./uploads && sudo chmod -R 775 ./uploads"
    )
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Task Scheduler for Automated Backups
from app.core.scheduler import start_scheduler, stop_scheduler

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.on_event("shutdown")
def shutdown_event():
    stop_scheduler()


@app.get("/")
async def root():
    return {"message": "Welcome to the Business Management System API"}


# Global exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"Validation error: {exc.errors()}")
    errors = []
    for err in exc.errors():
        errors.append(
            {
                "loc": err.get("loc", []),
                "msg": str(err.get("msg", "")),
                "type": err.get("type", ""),
            }
        )
    return JSONResponse(
        status_code=422,
        content={
            "detail": "Validation error",
            "errors": errors,
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    headers = {}
    origin = request.headers.get("origin")
    if origin:
        headers["Access-Control-Allow-Origin"] = origin
        headers["Access-Control-Allow-Credentials"] = "true"
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
        headers=headers,
    )
