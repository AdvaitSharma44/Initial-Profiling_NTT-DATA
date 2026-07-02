from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response payload."""

    error: str
    detail: Optional[str] = None


class EnrichmentRequest(BaseModel):
    """Schema for mandatory form fields in the enrichment request."""

    region: str = Field(..., description="Region/City for disambiguation")


class RawCompanyProfile(BaseModel):
    """Internal profile payload used during enrichment."""

    industry: Optional[str] = None
    sub_sector: Optional[str] = None
    revenue_usd: Optional[float] = None
    revenue_inr_crores: Optional[float] = None
    employee_count: Optional[int] = None
    status: Optional[str] = None
    parent_company: Optional[str] = None
    cagr: Optional[float] = None
    data_freshness_year: Optional[int] = None
    history_revenue_crores: Dict[int, float] = Field(default_factory=dict)
    region: Optional[str] = None


class CompanyData(BaseModel):
    """Final enriched company payload returned to the client."""

    company_name: str
    region: str
    industry: Optional[str] = None
    sub_sector: Optional[str] = None
    revenue_inr_crores: Optional[float] = None
    employee_count: Optional[int] = None
    status: Optional[str] = None
    parent_company: Optional[str] = None
    cagr: Optional[float] = None
    data_freshness_year: Optional[int] = None
    confidence_tag: str = "[Requires Manual Review]"


class HealthResponse(BaseModel):
    """Health check response payload."""

    status: str
    timestamp: datetime
    version: str
    environment: str
