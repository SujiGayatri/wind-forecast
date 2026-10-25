from datetime import date, timedelta

import httpx

from ..config import settings


class ElexonService:
    def __init__(self):
        self.base = settings.elexon_base_url.rstrip("/")
        self.timeout = settings.request_timeout

    async def _get(self, path: str, params: dict):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base}{path}",
                params=params,
            )

            response.raise_for_status()

            payload = response.json()

            if isinstance(payload, dict):
                return payload.get("data", payload)

            if isinstance(payload, list):
                return payload

            return []

    async def actual_wind(self, start: str, end: str):
        """
        Retrieve FUELHH actual wind generation.

        FUELHH has a maximum settlement-date query range,
        so January is requested in <= 7-day chunks.
        """

        start_date = date.fromisoformat(start[:10])
        end_date = date.fromisoformat(end[:10])

        all_rows = []
        current = start_date

        while current < end_date:
            chunk_end = min(
                current + timedelta(days=6),
                end_date - timedelta(days=1),
            )

            rows = await self._get(
                "/datasets/FUELHH",
                {
                    "settlementDateFrom": current.isoformat(),
                    "settlementDateTo": chunk_end.isoformat(),
                },
            )

            all_rows.extend(rows)

            current = chunk_end + timedelta(days=1)

        wind_rows = [
            row
            for row in all_rows
            if str(row.get("fuelType", "")).upper() == "WIND"
        ]

        return [
            row
            for row in wind_rows
            if start <= str(row.get("startTime", "")) < end
        ]

    async def wind_forecast(self, start: str, end: str):
        """
        Retrieve raw WINDFOR forecast records using publication time.

        We fetch publication data in one-day chunks and later
        select the latest forecast published before the
        day-ahead decision cutoff.
        """

        start_dt = date.fromisoformat(start[:10])
        end_dt = date.fromisoformat(end[:10])

        all_rows = []
        current = start_dt

        while current < end_dt:
            chunk_end = min(
                current + timedelta(days=1),
                end_dt,
            )

            rows = await self._get(
                "/datasets/WINDFOR",
                {
                    "publishDateTimeFrom": (
                        current.isoformat() + "T00:00:00Z"
                    ),
                    "publishDateTimeTo": (
                        chunk_end.isoformat() + "T00:00:00Z"
                    ),
                },
            )

            all_rows.extend(rows)

            current = chunk_end

        return all_rows

    async def health(self):
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.base}/health"
            )

            return response.status_code == 200