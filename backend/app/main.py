from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .services.elexon import ElexonService
from .services.analysis import analyze


app = FastAPI(
    title="UK Wind Forecast Analysis Portal",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


service = ElexonService()


JAN_START = "2026-01-01T00:00:00Z"
FEB_START = "2026-02-01T00:00:00Z"


@app.get("/api/health")
async def health():
    try:
        ok = await service.health()

        return {
            "status": "ok" if ok else "degraded",
            "elexon": ok,
        }

    except Exception as exc:
        return {
            "status": "degraded",
            "elexon": False,
            "detail": str(exc),
        }


@app.get("/api/analysis")
async def analysis(
    start: str = Query(JAN_START),
    end: str = Query(FEB_START),
):
    try:
        # ---------------------------------------------------------
        # 1. Get actual wind generation from FUELHH
        # ---------------------------------------------------------
        actual = await service.actual_wind(
            start,
            end,
        )

        # ---------------------------------------------------------
        # 2. Get forecasts.
        #
        # We start 2 days before January because a forecast
        # used for Jan 1 may have been published on Dec 30/31.
        # ---------------------------------------------------------
        start_dt = datetime.fromisoformat(
            start.replace("Z", "+00:00")
        )

        forecast_start = (
            start_dt - timedelta(days=2)
        ).isoformat().replace("+00:00", "Z")

        forecast = await service.wind_forecast(
            forecast_start,
            end,
        )

        # ---------------------------------------------------------
        # 3. Calculate forecast accuracy
        # ---------------------------------------------------------
        result = analyze(
            actual,
            forecast,
        )

        result["period"] = {
            "start": start,
            "end": end,
        }

        result["source"] = (
            "Elexon BMRS FUELHH + WINDFOR"
        )

        return result

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Unable to retrieve Elexon data: {exc}"
            ),
        )


@app.get("/api/forecast/latest")
async def latest_forecast():
    try:
        # Actual January wind generation
        actual = await service.actual_wind(
            JAN_START,
            FEB_START,
        )

        # Include forecasts published shortly before
        # the January delivery period.
        forecast = await service.wind_forecast(
            "2025-12-30T00:00:00Z",
            FEB_START,
        )

        result = analyze(
            actual,
            forecast,
        )

        return {
            "data": result["latestForecast"],
            "summary": result["summary"],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=(
                f"Unable to retrieve Elexon data: {exc}"
            ),
        )