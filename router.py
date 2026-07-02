from __future__ import annotations

import logging
from typing import List

import pandas as pd
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from fastapi.responses import StreamingResponse

from backend.models.config import AppConfig
from backend.models.schemas import CompanyData, HealthResponse, RawCompanyProfile
from backend.services.enrichment import (
    check_existing_data,
    check_internal_archive,
    build_company_data,
    companies_to_excel_payload,
    mock_external_api,
    parse_dataframe,
    validate_upload_file,
)

config = AppConfig()
router = APIRouter(prefix=config.api_prefix)
logger = logging.getLogger("lead_enrichment_api.router")


def normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = df.columns.astype(str).str.strip()
    return df


def get_company_name(row: pd.Series) -> str:
    candidate_keys = [
        "Company Name",
        "company_name",
        "Company",
        "company",
        "company_",
        "companyname",
        "Organization",
        "organization",
        "Organization Name",
        "organization_name",
        "Account Name",
        "account_name",
        "Account",
        "account",
        "Business Name",
        "business_name",
        "Legal Name",
        "legal_name",
        "Customer Name",
        "customer_name",
        "Client Name",
        "client_name",
        "Lead Company",
        "lead_company",
        "Name",
        "name",
        "company name",
    ]
    for key in candidate_keys:
        value = row.get(key)
        if pd.notna(value):
            text = str(value).strip()
            if text and text.lower() not in {"n/a", "na", "not available", "unknown", "none", "nan"}:
                return text

    for key, value in row.items():
        if pd.isna(value):
            continue
        text = str(value).strip()
        if not text or text.lower() in {"n/a", "na", "not available", "unknown", "none", "nan"}:
            continue
        lowered_key = str(key).strip().lower()
        if lowered_key in {
            "industry",
            "sub_sector",
            "status",
            "employee_count",
            "revenue",
            "revenue_inr_crores",
            "cagr",
            "data_freshness_year",
            "region",
            "confidence_tag",
            "apollo_revenue_display",
            "website",
            "city",
            "state",
            "country",
            "country_code",
            "phone",
            "email",
            "linkedin",
        }:
            continue
        return text

    return ""


@router.post("/enrich", response_class=StreamingResponse)
async def enrich_leads(file: UploadFile = File(...), region: str = Form(...)) -> StreamingResponse:
    """Enrich uploaded company leads and return an Excel file."""
    normalized_region = region.strip().title()
    if normalized_region not in config.supported_regions:
        raise HTTPException(
            status_code=400,
            detail=f"Region not supported. Allowed: {', '.join(config.supported_regions)}",
        )

    print(f"DEBUG: enrich_leads called, region={normalized_region}")
    try:
        extension, payload = await validate_upload_file(file)
        dataframe = parse_dataframe(payload, extension)
        dataframe = normalize_dataframe(dataframe)
        print(f"DEBUG: Parsed dataframe with {len(dataframe)} rows")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Failed to parse uploaded file: {exc}")

    enriched_companies: List[CompanyData] = []

    for index, row in dataframe.iterrows():
        company_name = get_company_name(row)
        if not company_name:
            logger.info("Skipping empty company name on row %s", index + 1)
            continue

        if check_existing_data(row):
            enriched_companies.append(
                CompanyData(
                    company_name=company_name,
                    region=normalized_region,
                    industry=str(row.get("Industry") or row.get("industry") or "").strip(),
                    confidence_tag="[Existing Data]",
                )
            )
            continue

        profile = check_internal_archive(company_name, normalized_region)
        if profile is None:
            profile = await mock_external_api(company_name, normalized_region)

        if profile is None:
            logger.warning("Apollo returned no profile for %s, using fallback region %s", company_name, normalized_region)
            profile = RawCompanyProfile(region=normalized_region)

        company_data = build_company_data(company_name, normalized_region, profile, row)
        enriched_companies.append(company_data)

    payload_bytes = companies_to_excel_payload(enriched_companies)
    return StreamingResponse(
        iter([payload_bytes]),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=enriched_leads.xlsx"},
    )


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=pd.Timestamp.now().to_pydatetime(),
        version="1.0.0",
        environment=config.environment,
    )
