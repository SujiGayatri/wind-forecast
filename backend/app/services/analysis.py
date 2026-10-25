import pandas as pd


def _records(df):
    if df.empty:
        return []

    cleaned = df.astype(object).where(
        pd.notna(df),
        None,
    )

    return cleaned.to_dict(orient="records")


def analyze(actual_rows, forecast_rows):
    actual = pd.DataFrame(actual_rows)
    forecast = pd.DataFrame(forecast_rows)

    if actual.empty or forecast.empty:
        return {
            "summary": {
                "mae": None,
                "rmse": None,
                "meanError": None,
                "matchedIntervals": 0,
                "latestForecastIntervals": 0,
            },
            "latestForecast": [],
            "comparison": [],
        }

    # ---------------------------------------------------------
    # ACTUALS
    # ---------------------------------------------------------

    actual["startTime"] = pd.to_datetime(
        actual["startTime"],
        utc=True,
        errors="coerce",
    )

    actual["generation"] = pd.to_numeric(
        actual["generation"],
        errors="coerce",
    )

    actual = actual.dropna(
        subset=["startTime", "generation"]
    )

    # FUELHH is half-hourly.
    # Convert to hourly average MW.
    actual["hour"] = actual["startTime"].dt.floor("h")

    actual_hourly = (
        actual
        .groupby("hour", as_index=False)["generation"]
        .mean()
        .rename(
            columns={
                "hour": "startTime",
                "generation": "actualGeneration",
            }
        )
    )

    # ---------------------------------------------------------
    # FORECASTS
    # ---------------------------------------------------------

    forecast["startTime"] = pd.to_datetime(
        forecast["startTime"],
        utc=True,
        errors="coerce",
    )

    forecast["publishTime"] = pd.to_datetime(
        forecast["publishTime"],
        utc=True,
        errors="coerce",
    )

    forecast["generation"] = pd.to_numeric(
        forecast["generation"],
        errors="coerce",
    )

    forecast = forecast.dropna(
        subset=[
            "startTime",
            "publishTime",
            "generation",
        ]
    )

    # Forecast data can contain duplicate versions
    # of the same delivery interval.
    forecast = forecast.drop_duplicates(
        subset=["startTime", "publishTime"],
        keep="last",
    )

    # ---------------------------------------------------------
    # NORMALIZE FORECAST TO HOURLY DELIVERY INTERVALS
    # ---------------------------------------------------------

    forecast["hour"] = forecast["startTime"].dt.floor("h")

    # If multiple records exist for the same hour and
    # publication time, average them.
    forecast_hourly = (
        forecast
        .groupby(
            ["hour", "publishTime"],
            as_index=False
        )["generation"]
        .mean()
        .rename(
            columns={
                "hour": "startTime",
            }
        )
    )

    # ---------------------------------------------------------
    # DAY-AHEAD FORECAST SELECTION
    # ---------------------------------------------------------
    #
    # Assumption:
    # The procurement decision is made before the delivery
    # date begins. Therefore we select the latest forecast
    # published before 00:00 UTC on the delivery date.
    #
    # This assumption will be documented in README.
    # ---------------------------------------------------------

    forecast_hourly["deliveryDay"] = (
        forecast_hourly["startTime"].dt.floor("D")
    )

    forecast_hourly["decisionCutoff"] = (
        forecast_hourly["deliveryDay"]
    )

    eligible = forecast_hourly[
        forecast_hourly["publishTime"]
        < forecast_hourly["decisionCutoff"]
    ].copy()

    latest = (
        eligible
        .sort_values(
            [
                "startTime",
                "publishTime",
            ]
        )
        .groupby(
            "startTime",
            as_index=False
        )
        .tail(1)
        .sort_values("startTime")
    )

    # ---------------------------------------------------------
    # MATCH WITH ACTUALS
    # ---------------------------------------------------------

    latest = latest.merge(
        actual_hourly,
        on="startTime",
        how="inner",
    )

    latest["error"] = (
        latest["actualGeneration"]
        - latest["generation"]
    )

    latest["absoluteError"] = (
        latest["error"].abs()
    )

    latest["squaredError"] = (
        latest["error"] ** 2
    )

    # ---------------------------------------------------------
    # ACCURACY METRICS
    # ---------------------------------------------------------

    if len(latest):
        mae = latest["absoluteError"].mean()

        rmse = (
            latest["squaredError"].mean()
        ) ** 0.5

        mean_error = latest["error"].mean()

    else:
        mae = None
        rmse = None
        mean_error = None

    # ---------------------------------------------------------
    # CHART DATA
    # ---------------------------------------------------------

    chart = latest.copy()

    # ---------------------------------------------------------
    # CLEAN OUTPUT
    # ---------------------------------------------------------

    def clean(df, columns):
        if df.empty:
            return []

        out = df[columns].copy()

        for column in columns:
            if column in [
                "startTime",
                "publishTime",
            ]:
                out[column] = (
                    out[column]
                    .dt.strftime(
                        "%Y-%m-%dT%H:%M:%SZ"
                    )
                )

        return _records(out)

    latest_columns = [
        "startTime",
        "publishTime",
        "generation",
        "actualGeneration",
        "error",
        "absoluteError",
    ]

    chart_columns = [
        "startTime",
        "generation",
        "actualGeneration",
        "error",
        "absoluteError",
    ]

    return {
        "summary": {
            "mae": (
                round(float(mae), 2)
                if mae is not None
                else None
            ),
            "rmse": (
                round(float(rmse), 2)
                if rmse is not None
                else None
            ),
            "meanError": (
                round(float(mean_error), 2)
                if mean_error is not None
                else None
            ),
            "matchedIntervals": int(len(latest)),
            "latestForecastIntervals": int(
                len(latest)
            ),
        },
        "latestForecast": clean(
            latest,
            latest_columns,
        ),
        "comparison": clean(
            chart,
            chart_columns,
        ),
    }