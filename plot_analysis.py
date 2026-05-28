#!/usr/bin/env python3
"""
London Bike analysis — one file does everything.

Run (from any folder):
    python plot_analysis.py

Or in Cursor: open this file → click Run (▶)
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MYSQL = Path("/opt/homebrew/bin/mysql") if Path("/opt/homebrew/bin/mysql").exists() else Path("mysql")
SQL_MODE = (
    "STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,"
    "ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION"
)


def _install_matplotlib() -> None:
    print("Installing matplotlib (one-time)...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "-q"])


try:
    import matplotlib.pyplot as plt
except ImportError:
    _install_matplotlib()
    import matplotlib.pyplot as plt

QUERIES = {
    "hourly": """
        SELECT HOUR(timestamp) AS hour, AVG(cnt) AS avg_rentals
        FROM bike_sharing
        GROUP BY HOUR(timestamp)
        ORDER BY hour
    """,
    "weather": """
        SELECT
            CASE weather_code
                WHEN 1 THEN 'Clear'
                WHEN 2 THEN 'Cloudy'
                WHEN 3 THEN 'Light rain'
                WHEN 4 THEN 'Heavy rain'
                WHEN 7 THEN 'Fog'
                WHEN 10 THEN 'Storm'
                WHEN 26 THEN 'Snow'
                ELSE 'Other'
            END AS weather,
            AVG(cnt) AS avg_rentals
        FROM bike_sharing
        GROUP BY weather_code
        ORDER BY avg_rentals DESC
    """,
    "weekend": """
        SELECT
            CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
            AVG(cnt) AS avg_rentals
        FROM bike_sharing
        GROUP BY is_weekend
    """,
    "temperature": """
        SELECT FLOOR(t1 / 5) * 5 AS temp_low, AVG(cnt) AS avg_rentals
        FROM bike_sharing
        GROUP BY FLOOR(t1 / 5)
        ORDER BY temp_low
    """,
    "season": """
        SELECT
            CASE season
                WHEN 0 THEN 'Spring'
                WHEN 1 THEN 'Summer'
                WHEN 2 THEN 'Autumn'
                WHEN 3 THEN 'Winter'
            END AS season_name,
            AVG(cnt) AS avg_rentals
        FROM bike_sharing
        GROUP BY season
        ORDER BY FIELD(season, 0, 1, 2, 3)
    """,
}


def _mysql_cmd(*args: str, database: str | None = None) -> list[str]:
    cmd = [str(MYSQL), "-u", "root", "-h", "127.0.0.1", *args]
    if database:
        cmd.append(database)
    return cmd


def _ping_mysql() -> bool:
    r = subprocess.run(_mysql_cmd("-e", "SELECT 1"), capture_output=True, text=True)
    return r.returncode == 0


def _start_mysql() -> None:
    brew = Path("/opt/homebrew/bin/brew")
    if brew.exists():
        print("Starting MySQL...")
        subprocess.run([str(brew), "services", "start", "mysql"], check=False)
        import time
        time.sleep(3)


def run_mysql(sql: str, *, database: str = "london_bikes") -> list[list[str]]:
    cmd = _mysql_cmd("--batch", "--raw", database, "-e",
                     f"SET SESSION sql_mode = '{SQL_MODE}'; {sql}")
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    lines = [line for line in result.stdout.strip().splitlines() if line.strip()]
    return [line.split("\t") for line in lines[1:]]


def setup_database() -> int:
    if not _ping_mysql():
        _start_mysql()
    if not _ping_mysql():
        print("MySQL is not running. Install & start it:", file=sys.stderr)
        print("  brew install mysql && brew services start mysql", file=sys.stderr)
        sys.exit(1)

    create_sql = (ROOT / "create_table.sql").read_text()
    create_sql = create_sql.replace(
        "CREATE DATABASE london_bikes",
        "CREATE DATABASE IF NOT EXISTS london_bikes",
    ).replace(
        "CREATE TABLE bike_sharing",
        "CREATE TABLE IF NOT EXISTS bike_sharing",
    )
    subprocess.run(_mysql_cmd(), input=create_sql, text=True, capture_output=True, check=True, cwd=ROOT)

    try:
        count = int(run_mysql("SELECT COUNT(*) FROM bike_sharing;")[0][0])
        if count > 0:
            print(f"Database ready ({count:,} rows).")
            return count
    except RuntimeError:
        pass

    data_file = ROOT / "london_merged.xls"
    if not data_file.exists():
        print(f"Missing {data_file.name} — cannot load data.", file=sys.stderr)
        sys.exit(1)

    print("Loading data...")
    subprocess.run(_mysql_cmd("-e", "SET GLOBAL local_infile = 1;"), check=True, capture_output=True)
    load_sql = f"""
    USE london_bikes;
    TRUNCATE TABLE bike_sharing;
    LOAD DATA LOCAL INFILE '{data_file}'
    INTO TABLE bike_sharing
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\\n'
    IGNORE 1 LINES
    (timestamp, cnt, t1, t2, hum, wind_speed, weather_code, is_holiday, is_weekend, season);
    """
    subprocess.run(
        [str(MYSQL), "--local-infile=1", "-u", "root", "-h", "127.0.0.1"],
        input=load_sql, text=True, check=True, capture_output=True, cwd=ROOT,
    )
    count = int(run_mysql("SELECT COUNT(*) FROM bike_sharing;")[0][0])
    print(f"Loaded {count:,} rows.")
    return count


def plot_hourly(ax: plt.Axes, rows: list[list[str]]) -> None:
    hours = [int(r[0]) for r in rows]
    values = [float(r[1]) for r in rows]
    ax.bar(hours, values, color="#4c8bf5", edgecolor="#1a3a6e", linewidth=0.6)
    ax.set_xlabel("Hour of day")
    ax.set_ylabel("Avg rentals")
    ax.set_title("Hourly usage pattern")
    ax.set_xticks(range(0, 24, 2))


def plot_weather(ax: plt.Axes, rows: list[list[str]]) -> None:
    labels = [r[0] for r in rows]
    values = [float(r[1]) for r in rows]
    y_pos = range(len(labels))
    ax.barh(y_pos, values, color="#5ec269", edgecolor="#2a5c32", linewidth=0.6)
    ax.set_yticks(y_pos, labels=labels)
    ax.invert_yaxis()
    ax.set_xlabel("Avg rentals")
    ax.set_title("Rentals by weather")


def plot_weekend(ax: plt.Axes, rows: list[list[str]]) -> None:
    labels = [r[0] for r in rows]
    values = [float(r[1]) for r in rows]
    colors = ["#f0a04b", "#e85d5d"]
    ax.bar(labels, values, color=colors[: len(labels)], edgecolor="#333", linewidth=0.6)
    ax.set_ylabel("Avg hourly rentals")
    ax.set_title("Weekend vs weekday")


def plot_temperature(ax: plt.Axes, rows: list[list[str]]) -> None:
    labels = [f"{int(r[0])}–{int(r[0]) + 4}°C" for r in rows]
    values = [float(r[1]) for r in rows]
    ax.plot(labels, values, marker="o", color="#9b6dd7", linewidth=2, markersize=6)
    ax.set_xlabel("Temperature band")
    ax.set_ylabel("Avg rentals")
    ax.set_title("Temperature vs demand")
    ax.tick_params(axis="x", rotation=45)


def plot_season(ax: plt.Axes, rows: list[list[str]]) -> None:
    labels = [r[0] for r in rows]
    values = [float(r[1]) for r in rows]
    ax.bar(labels, values, color=["#7bc96f", "#f9d56e", "#e8874c", "#6baed6"], edgecolor="#333", linewidth=0.6)
    ax.set_ylabel("Avg rentals")
    ax.set_title("Seasonal patterns")


def main() -> int:
    setup_database()

    fig, axes = plt.subplots(2, 3, figsize=(15, 9))
    fig.suptitle("London Bike Sharing Analysis", fontsize=14, fontweight="bold")
    axes_flat = axes.flatten()

    plotters = [
        (plot_hourly, QUERIES["hourly"]),
        (plot_weather, QUERIES["weather"]),
        (plot_weekend, QUERIES["weekend"]),
        (plot_temperature, QUERIES["temperature"]),
        (plot_season, QUERIES["season"]),
    ]

    print("Showing charts (close the window to exit)...")
    for ax, (plot_fn, sql) in zip(axes_flat, plotters):
        plot_fn(ax, run_mysql(sql))

    axes_flat[5].axis("off")
    plt.tight_layout()
    plt.show()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
