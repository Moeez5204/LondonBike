-- ============================================
-- LONDON BIKE SHARING - COMPLETE ANALYSIS
-- Skills: Aggregations, Window Functions, CTEs, Date Functions
-- ============================================

-- 1. Hourly usage pattern (peak hours)
SELECT
    HOUR(timestamp) AS hour,
    AVG(cnt) AS avg_rentals,
    SUM(cnt) AS total_rentals,
    COUNT(*) AS days_recorded
FROM bike_sharing
GROUP BY HOUR(timestamp)
ORDER BY avg_rentals DESC;

-- 2. Weather impact analysis
SELECT
    CASE weather_code
        WHEN 1 THEN 'Clear/Few clouds'
        WHEN 2 THEN 'Mist/Cloudy'
        WHEN 3 THEN 'Light rain/Snow'
        WHEN 4 THEN 'Heavy rain/Snow'
        WHEN 7 THEN 'Fog'
        WHEN 10 THEN 'Thunderstorm'
        WHEN 26 THEN 'Snow'
        ELSE 'Other'
    END AS weather_condition,
    AVG(cnt) AS avg_rentals,
    COUNT(*) AS hours_observed
FROM bike_sharing
GROUP BY weather_code
ORDER BY avg_rentals DESC;

-- 3. Weekend vs Weekday comparison
SELECT
    CASE WHEN is_weekend = 1 THEN 'Weekend' ELSE 'Weekday' END AS day_type,
    AVG(cnt) AS avg_hourly_rentals,
    MAX(cnt) AS peak_hour_rentals,
    SUM(cnt) AS total_rentals
FROM bike_sharing
GROUP BY is_weekend;

-- 4. Temperature sweet spot (by 5-degree bands)
SELECT
    CONCAT(FLOOR(t1/5)*5, '-', FLOOR(t1/5)*5+4, '°C') AS temp_range,
    AVG(cnt) AS avg_rentals,
    COUNT(*) AS hours_in_range,
    AVG(hum) AS avg_humidity
FROM bike_sharing
GROUP BY FLOOR(t1/5)
ORDER BY FLOOR(t1/5);

-- 5. Seasonal patterns
SELECT
    CASE season
        WHEN 0 THEN 'Spring'
        WHEN 1 THEN 'Summer'
        WHEN 2 THEN 'Autumn'
        WHEN 3 THEN 'Winter'
    END AS season_name,
    AVG(cnt) AS avg_rentals,
    SUM(cnt) AS total_rentals,
    AVG(t1) AS avg_temp,
    AVG(hum) AS avg_humidity
FROM bike_sharing
GROUP BY season
ORDER BY avg_rentals DESC;

-- 6. Top 10 busiest days (by total daily rentals)
SELECT
    DATE(timestamp) AS date,
    SUM(cnt) AS daily_total,
    ROUND(AVG(t1), 1) AS avg_temp,
    MAX(weather_code) AS weather_condition
FROM bike_sharing
GROUP BY DATE(timestamp)
ORDER BY daily_total DESC
LIMIT 10;

-- 7. 7-day moving average (window function)
SELECT
    DATE(timestamp) AS date,
    SUM(cnt) AS daily_rentals,
    AVG(SUM(cnt)) OVER (ORDER BY DATE(timestamp) ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7day
FROM bike_sharing
GROUP BY DATE(timestamp)
ORDER BY date;

-- 8. Most common weather during high-demand periods (>100 rentals/hour)
SELECT
    CASE weather_code
        WHEN 1 THEN 'Clear'
        WHEN 2 THEN 'Cloudy'
        WHEN 3 THEN 'Light rain'
        WHEN 4 THEN 'Heavy rain'
        ELSE 'Other'
    END AS weather,
    COUNT(*) AS high_demand_hours
FROM bike_sharing
WHERE cnt > 100
GROUP BY weather_code
ORDER BY high_demand_hours DESC;

-- 9. Holiday vs Normal day comparison
SELECT
    CASE WHEN is_holiday = 1 THEN 'Holiday' ELSE 'Normal' END AS day_type,
    AVG(cnt) AS avg_rentals,
    AVG(t1) AS avg_temp
FROM bike_sharing
GROUP BY is_holiday;

-- 10. Best conditions for biking (temperature + weather combination)
SELECT
    ROUND(t1, 0) AS temp_celsius,
    weather_code,
    AVG(cnt) AS avg_rentals,
    COUNT(*) AS sample_size
FROM bike_sharing
WHERE weather_code IN (1, 2)  -- Clear or cloudy only
GROUP BY ROUND(t1, 0), weather_code
HAVING sample_size > 50
ORDER BY avg_rentals DESC
LIMIT 10;