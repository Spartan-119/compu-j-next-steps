# Bund Futures Data Analysis

## Description
This project analyzes tick-level time-and-sales data for the December 2012 contract of the 10-year Bund Futures traded on EUREX. It processes data from a SQLite database and generates a CSV file with specific daily statistics.

## Features
- Reads tick data from a SQLite database
- Calculates daily statistics including:
  - First price of the day
  - Volume-weighted average price between 17:14:00 and 17:15:00
  - Flag for first price traded after 17:15:00
  - Time of first trade after 17:15:00 (if applicable)
- Outputs results to a CSV file

## Requirements
`pip install -r requirements.txt`
