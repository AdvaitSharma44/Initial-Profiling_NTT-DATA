# Frontend Test Page

This is a simple HTML/Tailwind UI for testing the `/enrich` backend endpoint.

## Usage

1. Run the FastAPI backend from `backend/main.py`.
2. Open `frontend/index.html` in your browser.
3. Upload a `.xlsx` or `.csv` file and select a supported region.
4. The app will post to `http://localhost:8000/enrich` and download the returned file.

## Notes
- The frontend is intentionally minimal and uses a CDN-hosted Tailwind stylesheet.
- It expects the backend to be running locally on port `8000`.
