import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.utils.logging import setup_logging
from app.utils.metrics import get_metrics
from app.api.v1.api import api_router
from app.core.config import settings

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    version=settings.VERSION,
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up...")
    try:
        from app.db.session import get_db
        from sqlalchemy import text
        # We need to get a session to test
        async for session in get_db():
            await session.execute(text("SELECT 1"))
            logger.info("Database connection successful!")
            break
    except Exception as e:
        logger.error(f"Database connection failed: {e}")


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} - {response.status_code} - {process_time:.4f}s")
    return response

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/metrics")
async def metrics():
    return get_metrics()

from fastapi.responses import RedirectResponse

@app.get("/")
async def root():
    return RedirectResponse(url="/docs")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
