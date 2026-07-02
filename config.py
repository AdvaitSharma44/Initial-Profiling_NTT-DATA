from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

from pydantic_settings import BaseSettings


class AppConfig(BaseSettings):
    """Application configuration loaded from environment or defaults."""

    app_name: str = "Lead Enrichment API"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    max_upload_size_mb: int = 5
    max_rows: int = 100_000
    allowed_extensions: Tuple[str, ...] = (".xlsx", ".csv")
    allowed_content_types: Tuple[str, ...] = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-excel",
        "text/csv",
        "application/csv",
        "text/plain",
    )
    allowed_origins: Tuple[str, ...] = (
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    )
    supported_regions: Tuple[str, ...] = (
        "Pan-India",
        "Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai",
        "Pune", "Kolkata", "Ahmedabad", "Jaipur", "Lucknow",
    )
    static_dir: Path = Path(__file__).resolve().parents[1] / "frontend"
    apollo_api_key: Optional[str] = None

    class Config:
        env_file = str(Path(__file__).resolve().parents[2] / ".env")
        env_file_encoding = "utf-8"
