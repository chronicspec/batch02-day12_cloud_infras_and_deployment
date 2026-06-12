import time
import signal
import logging
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes_chat import router as chat_router
from app.api.routes_facilities import router as facilities_router
from app.config import get_settings
from app.auth import verify_api_key
from app.rate_limiter import check_rate_limit
from app.cost_guard import check_budget

logging.basicConfig(level=logging.INFO, format='{"ts":"%(asctime)s","lvl":"%(levelname)s","msg":"%(message)s"}')
logger = logging.getLogger(__name__)

is_ready = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    global is_ready
    logger.info(json.dumps({"event": "startup", "msg": "Starting up..."}))
    is_ready = True
    yield
    is_ready = False
    logger.info(json.dumps({"event": "shutdown", "msg": "Shutting down gracefully..."}))

def handle_sigterm(signum, frame):
    logger.info(json.dumps({"event": "signal", "signum": signum, "msg": "SIGTERM received"}))

signal.signal(signal.SIGTERM, handle_sigterm)


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="VinWonders facility assistant prototype.",
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        ms = round((time.time() - start) * 1000, 1)
        logger.info(json.dumps({
            "event": "request",
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "ms": ms
        }))
        return response

    @app.get("/health", tags=["Operations"])
    def health():
        return {"status": "ok", "version": settings.app_version}

    @app.get("/ready", tags=["Operations"])
    def ready():
        if not is_ready:
            raise HTTPException(503, "Not ready")
        return {"ready": True}

    dependencies = [
        Depends(verify_api_key),
        Depends(check_rate_limit),
        Depends(check_budget),
    ]

    app.include_router(facilities_router, prefix=settings.api_prefix, dependencies=dependencies)
    app.include_router(chat_router, prefix=settings.api_prefix, dependencies=dependencies)
    return app


app = create_app()

