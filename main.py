from __future__ import annotations

import logging
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from backend.api.router import router
from backend.models.config import AppConfig

config = AppConfig()

logger = logging.getLogger("lead_enrichment_api")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s"))
logger.addHandler(handler)

app = FastAPI(
    title=config.app_name,
    description="Secure B2B Lead Enrichment with in-memory file processing and mock enrichment adapters.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(config.allowed_origins),
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    allow_credentials=False,
)

if config.environment == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"

if frontend_dir.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")
else:
    logger.warning("Frontend static directory does not exist: %s", frontend_dir)


@app.middleware("http")
async def secure_headers_middleware(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "interest-cohort=()"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if config.environment == "production":
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains; preload"
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    logger.warning("HTTP error: %s %s", request.url, exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": str(exc.detail)})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled exception while processing request %s", request.url)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error", "detail": "An unexpected error occurred."},
    )


@app.get("/", response_class=HTMLResponse)
async def serve_spa() -> FileResponse:
    from pathlib import Path
    index_path = Path("index.html")
    if not index_path.exists():
        message = "Frontend index.html not found."
        logger.error(message)
        raise HTTPException(status_code=HTTP_500_INTERNAL_SERVER_ERROR, detail=message)
    return FileResponse(index_path, media_type="text/html")


app.include_router(router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=config.environment != "production")
