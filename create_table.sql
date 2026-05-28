-- LONDON BIKE SHARING ANALYSIS
-- Complete Portfolio Project

CREATE DATABASE london_bikes;
USE london_bikes;

CREATE TABLE bike_sharing (
    timestamp DATETIME PRIMARY KEY,
    cnt INT,
    t1 FLOAT,
    t2 FLOAT,
    hum FLOAT,
    wind_speed FLOAT,
    weather_code INT,
    is_holiday INT,
    is_weekend INT,
    season INT
);