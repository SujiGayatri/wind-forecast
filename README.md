# Wind Forecast Analysis Portal

A focused full-stack prototype for a UK energy utility's day-ahead procurement team. It uses Elexon BMRS wind actuals (FUELHH) and wind forecasts (WINDFOR) for January 2026, compares forecast vs actual generation, and quantifies forecast error.

## Business problem
Wind generation is variable. The procurement team must make day-ahead electricity purchasing decisions before the delivery day, so they need to understand the latest wind forecast and the uncertainty in that forecast.

## Solution
The portal retrieves Elexon data through a Python FastAPI backend, aligns forecast and actual 30-minute intervals, selects the latest forecast available before each delivery day for the decision-support view, calculates MAE/RMSE/mean error, and presents the results in a React dashboard.

## Architecture
React + Vite + Recharts → FastAPI → Elexon Insights API

## Important scope assumption
For the day-ahead decision-support view, the application selects the latest WINDFOR forecast whose `publishTime` is before the UTC start of the delivery day. This makes the selection rule explicit and reproducible. The assignment does not specify an exact market decision timestamp, so this is a documented implementation assumption.

## Run locally
### Docker
```bash
docker compose up --build
```
Frontend: http://localhost:5173
Backend: http://localhost:8000/docs

### Without Docker
Backend:
```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

Create `frontend/.env` with `VITE_API_URL=http://localhost:8000` if needed.

## AI tools
AI assistance was used during development for code drafting, architecture discussion, debugging guidance, and documentation. The final implementation was reviewed against the assignment requirements and Elexon's current API documentation.

## Data source
Elexon Insights/BMRS public APIs. No API key is required. The project uses the assignment-specified FUELHH and WINDFOR datasets.

## Deployment
Deploy the frontend and backend separately. For Vercel, set `VITE_API_URL` to the deployed backend URL. For the backend, deploy the Docker container to a container-capable host.
