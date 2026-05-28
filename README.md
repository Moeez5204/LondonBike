# London Bike Sharing Analysis

SQL portfolio project analyzing hourly London bike-sharing rentals (2015–2017), combined with weather and calendar features. Includes 10 analytical queries and an optional Python script that loads the data and displays five charts.

# Data analysed 

<img width="1492" height="905" alt="Screenshot 2026-05-28 at 4 53 41 PM" src="https://github.com/user-attachments/assets/fe1c0754-346b-4182-a72c-7087182254cd" />


## Features

- **MySQL schema** for hourly rental and weather data
- **10 analysis queries** — aggregations, window functions, date functions, and conditional logic
- **One-command visualization** — `plot_analysis.py` sets up the database, loads data, and opens charts automatically

## Dataset

`london_merged.xls` is a CSV file (~17,400 hourly rows) with:

| Column | Description |
|--------|-------------|
| `timestamp` | Hour of observation |
| `cnt` | Number of bike rentals |
| `t1`, `t2` | Temperature (°C) |
| `hum` | Humidity (%) |
| `wind_speed` | Wind speed |
| `weather_code` | Weather category |
| `is_holiday` | 1 = holiday, 0 = normal day |
| `is_weekend` | 1 = weekend, 0 = weekday |
| `season` | 0 Spring, 1 Summer, 2 Autumn, 3 Winter |

## Project structure

```
LondonBike/
├── create_table.sql      # Database and table schema
├── insert_data.sql       # Sample INSERTs (10 rows)
├── analysis_queries.sql  # 10 analytical queries
├── london_merged.xls     # Full dataset
├── plot_analysis.py      # Auto setup + 5 charts
└── README.md
```

## Prerequisites

- **Python 3.10+**
- **MySQL 8+** (macOS: `brew install mysql`)

## Quick start (charts)

1. Clone the repository and open the project folder.

2. Install MySQL (one time):

   ```bash
   brew install mysql
   ```

3. Run the analysis script:

   ```bash
   python plot_analysis.py
   ```

   The script will:

   - Start MySQL if it is not running
   - Create the `london_bikes` database and `bike_sharing` table
   - Load data from `london_merged.xls`
   - Install `matplotlib` on first run if needed
   - Display five charts (hourly usage, weather, weekend vs weekday, temperature, seasons)

   Close the chart window to exit.

## Manual SQL workflow

If you prefer running the SQL files yourself:

```bash
# 1. Start MySQL
brew services start mysql

# 2. Create schema
mysql -u root < create_table.sql

# 3. Load full data (from project folder)
mysql --local-infile=1 -u root -e "
  SET GLOBAL local_infile = 1;
  USE london_bikes;
  LOAD DATA LOCAL INFILE '$(pwd)/london_merged.xls'
  INTO TABLE bike_sharing
  FIELDS TERMINATED BY ','
  LINES TERMINATED BY '\n'
  IGNORE 1 LINES;
"

# 4. Run analysis queries
mysql -u root london_bikes < analysis_queries.sql
```

> On MySQL 8+, queries 4 and 10 may require relaxing `ONLY_FULL_GROUP_BY` for the session.

## Analysis queries

`analysis_queries.sql` includes:

1. Hourly usage pattern (peak hours)
2. Weather impact on rentals
3. Weekend vs weekday comparison
4. Temperature bands (5°C)
5. Seasonal patterns
6. Top 10 busiest days
7. 7-day moving average (window function)
8. Weather during high-demand periods
9. Holiday vs normal days
10. Best conditions for biking (clear/cloudy, warm temps)

## Charts (`plot_analysis.py`)

| Chart | Insight |
|-------|---------|
| Hourly usage | Rush hours (typically 8 AM and 5 PM) |
| Weather | Average rentals by weather type |
| Weekend vs weekday | Weekday demand vs weekends |
| Temperature | Demand across temperature bands |
| Seasons | Spring through winter comparison |

## Tech stack

- MySQL
- Python 3
- Matplotlib

## License

This project is for educational and portfolio use. Dataset subject to its original source terms.
