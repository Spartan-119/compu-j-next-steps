import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, time
import os

def calculate_vwap(data):
    """Method to calculate the volume-weighted average price (VWAP)."""
    total_value = (data['Price'] * data['LotsTraded']).sum()
    total_volume = data['LotsTraded'].sum()
    if total_volume == 0:
        return None
    return total_value / total_volume

def process_bund_futures_data(db_path, start_date, end_date):
    # connecting to the sqlite database adn then closing it
    db = sqlite3.connect(db_path)
    df = pd.read_sql_query('SELECT * FROM tickdata', db)
    db.close()

    # Convert the DateTime column to pandas datetime
    df['DateTime'] = pd.to_datetime(df['DateTime'], format = 'mixed')

    # just filtering the rows in which we are interested in
    df = df[(df['DateTime'] >= start_date) & (df['DateTime'] <= end_date)]

    # creating a list where we will store all the results
    results = []

    # will loop from the start date to the end data via current date
    current_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date)

    while current_date <= end_date:
        # extract today's date
        todays_date = df[df['DateTime'].dt.date == current_date.date()]

        if not todays_date.empty: 
            first_price = todays_date.iloc[0]['Price']

            # logic to calculate the volume-weighted price in the 1 minute
            # between 17:14:00 and 17:15:00 inclusive
            start_time = datetime.combine(current_date.date(), time(17, 14))
            end_time = datetime.combine(current_date.date(), time(17, 15))
            volume_weighted_data = todays_date[(todays_date['DateTime'] >= start_time) & (todays_date['DateTime'] < end_time)]
            
            # Calculate the VWAP using the helper function
            volume_weighed_avg_price = calculate_vwap(volume_weighted_data)
            
            # Checking if the first price of the day is traded after 17:15:00
            after_time = datetime.combine(current_date.date(), time(17, 15))
            after_data = todays_date[todays_date['DateTime'] >= after_time]
            
            if not after_data.empty and first_price in after_data['Price'].values:
                flag = True
                first_trade_time = after_data[after_data['Price'] == first_price].iloc[0]['DateTime']
            else:
                flag = False
                first_trade_time = None
            
            # Appending the results for the current day
            results.append({
                'day': current_date.strftime('%Y-%m-%d'),
                'first_price': first_price,
                'volume_weighed_avg_price': volume_weighed_avg_price,
                'flag': flag,
                'first_trade_time': first_trade_time.strftime('%H:%M:%S.%f') if first_trade_time else None
            })
        
        # Move to the next day
        current_date += pd.Timedelta(days=1)

    # Convert the results to a DataFrame
    results_df = pd.DataFrame(results)
    
    return results_df

###############
# some additional code to visualise a few stufff

# time series plot of VWAP and First Price
def plot_vwap_vs_first_price(results_df):
    plt.figure(figsize=(14, 7))
    plt.plot(results_df['day'], results_df['volume_weighed_avg_price'], label='VWAP', marker='o')
    plt.plot(results_df['day'], results_df['first_price'], label='First Price', marker='x')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.title('VWAP vs First Price Over Time')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('output\plot_vwap_vs_first_price.png')

# Histogram of VWAP
def plot_vwap_histogram(results_df):
    plt.figure(figsize=(10, 6))
    plt.hist(results_df['volume_weighed_avg_price'].dropna(), bins=20, edgecolor='k')
    plt.xlabel('VWAP')
    plt.ylabel('Frequency')
    plt.title('Distribution of VWAP')
    plt.savefig("output\VWAP_histogram.png")

# Scatter Plot of VWAP vs First Price
def plot_vwap_vs_first_price_scatter(results_df):
    plt.figure(figsize=(10, 6))
    plt.scatter(results_df['first_price'], results_df['volume_weighed_avg_price'], alpha=0.6)
    plt.xlabel('First Price')
    plt.ylabel('VWAP')
    plt.title('VWAP vs First Price')
    plt.savefig("output\VWAP_vs_first_price.png")

# Flagged Days Plot
def plot_flagged_days(results_df):
    flag_counts = results_df['flag'].value_counts()
    plt.figure(figsize=(8, 6))
    flag_counts.plot(kind='bar', color=['blue', 'orange'])
    plt.xlabel('Flag')
    plt.ylabel('Number of Days')
    plt.title('Number of Days with Flag True/False')
    plt.xticks([0, 1], ['False', 'True'], rotation=0)
    plt.savefig('output\Flagged_days_plot.png')

def main():
    # doign some necessary stuff
    db_path = 'data/BNZ12.sqlite'
    start_date, end_date = '2012-09-05', '2012-12-04'
    results_df = process_bund_futures_data(db_path, start_date, end_date)
    plot_vwap_vs_first_price(results_df)
    plot_vwap_histogram(results_df)
    plot_vwap_vs_first_price_scatter(results_df)
    plot_flagged_days(results_df)

    # # Create 'output' directory if it doesn't exist
    # os.makedirs('output', exist_ok = True)
    
    # # Save the results to a CSV file in the 'output' folder
    # results_df.to_csv('output/results.csv', index = False)
    
    # print("Processing complete. Results saved to 'output/results.csv'.")

if __name__ == "__main__":
    main()