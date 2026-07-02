# Lead Enrichment Application - Project Structure

## Directory Layout

```
lead-enrichment-app/
├── backend/
│   ├── main.py                    # FastAPI application with all core logic
│   ├── adapters/
│   │   ├── apollo_adapter.py      # [TODO] Apollo.io API integration
│   │   ├── clearbit_adapter.py    # [TODO] Clearbit API integration
│   │   └── crunchbase_adapter.py  # [TODO] Crunchbase API integration
│   └── core/
│       ├── models.py              # [TODO] Pydantic models for internal use
│       ├── enrichment.py          # [TODO] Core enrichment logic
│       └── archive.py             # [TODO] Internal archive/database layer
├── frontend/
│   ├── index.html                 # [TODO] Main HTML with upload form
│   ├── app.js                     # [TODO] Vanilla JS or React app
│   └── styles.css                 # [TODO] Tailwind CSS styles
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment variables template
├── PROJECT_STRUCTURE.md           # This file
└── README.md                       # [TODO] Full documentation

```

## Files Created

### ✅ COMPLETED

1. **requirements.txt** - All necessary Python dependencies for FastAPI, pandas, file handling, and async operations.

2. **backend/main.py** - Comprehensive FastAPI backend containing:
   - ✅ File upload endpoint with validation
   - ✅ In-memory file processing using `io.BytesIO`
   - ✅ Region/City dropdown validation
   - ✅ **Skeleton functions** (ready for implementation):
     - `check_existing_data()` - Skip lookup if Industry already populated
     - `check_internal_archive()` - Query mock internal database
     - `disambiguate_company_results()` - Filter by region when API returns multiple matches
     - `call_external_api()` - Modular adapter (supports apollo, clearbit, crunchbase)
     - `convert_usd_to_inr_crores()` - Currency conversion with Crores formatting
     - `calculate_cagr()` - 3-5 year compound growth rate calculation
     - `map_industry_taxonomy()` - Strict vertical mapping + Manufacturing drill-down
     - `process_hierarchy_and_status()` - Handle Acquired/Subsidiary/Bankrupt flags
     - `apply_whale_catcher_logic()` - Employee proxy override (>50 employees)
     - `generate_confidence_tags()` - Tag generation: [Ready for Sales], [Whale], [Acquired], etc.
     - `enrich_dataframe_to_excel()` - Convert to downloadable Excel
   - ✅ Main `/enrich` endpoint orchestrating the full pipeline
   - ✅ Health check endpoint
   - ✅ Constants & configuration (regions, industry taxonomy, manufacturing subsectors)
   - ✅ Security: All in-memory, no disk saves, explicit RAM cleanup

## Next Steps (Awaiting Your Approval)

### Phase 2: Core Enrichment Logic Implementation
- [ ] Implement `call_external_api()` with actual Apollo/Clearbit/Crunchbase integration
- [ ] Build mock internal archive database (SQLite or in-memory)
- [ ] Implement real disambiguation logic using region filtering
- [ ] Add CAGR calculation and financial guardrails
- [ ] Implement industry taxonomy mapping with Manufacturing drill-down

### Phase 3: Frontend
- [ ] Create HTML form with file upload + region dropdown
- [ ] Build React/Vanilla JS app for real-time upload and progress
- [ ] Add file preview and validation feedback
- [ ] Integrate with backend `/enrich` endpoint

### Phase 4: API Adapters
- [ ] Apollo.io adapter with async requests
- [ ] Clearbit adapter with deduplication
- [ ] Crunchbase adapter with financial data extraction

### Phase 5: Testing & Deployment
- [ ] Unit tests for enrichment functions
- [ ] Integration tests for full pipeline
- [ ] Docker containerization
- [ ] Deployment configuration

## Running the Application

### Prerequisites
```bash
cd d:\Initial Profiling\lead-enrichment-app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Start Backend
```bash
cd backend
python main.py
```

The API will be available at:
- **Base URL:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

### API Endpoints (Current)

#### `POST /enrich` - Main Enrichment Endpoint
**Request:**
```
multipart/form-data:
  - file: <binary xlsx/csv>
  - region: "Mumbai" | "Delhi" | ... (from SUPPORTED_REGIONS)
```

**Response:**
```
binary/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename=enriched_leads.xlsx
```

#### `GET /health` - Health Check
**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-06-25T10:30:45.123456",
  "version": "1.0.0"
}
```

## Key Design Decisions

### Security & Performance
- **In-Memory Only:** All file processing uses `io.BytesIO` - no disk writes
- **Explicit Cleanup:** RAM buffers explicitly deleted after use
- **File Size Limits:** Max 50MB per file, 100k rows per request
- **Input Validation:** File extension, size, row count all validated

### Enrichment Logic
- **Skip Existing Data:** If company row has Industry populated, skip API lookup (saves credits)
- **Internal Archive First:** Before calling external APIs, check cached data
- **Region-Based Disambiguation:** When API returns multiple matches, use region to filter
- **Financial Guardrails:** Currency conversion, CAGR fallback, freshness checks
- **Whale Catcher:** If revenue missing but employees > 50, flag for manual review

### Output Quality
- **Confidence Tags:** Every row gets a tag: Ready for Sales, Whale, Acquired, Review, etc.
- **Never Delete Rows:** All rows returned, with flags/tags for action
- **Hierarchy Handling:** Subsidiary/Acquired companies show parent company info
- **Bankruptcy Flag:** Defunct entities flagged explicitly

## Configuration

See `.env.example` for required environment variables (API keys, credentials, etc.)

