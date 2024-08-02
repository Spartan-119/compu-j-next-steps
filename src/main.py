import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, time
import os

def process_bund_futures_data(db_path, start_date, end_date):
    # connecting to the sqlite database
    db = sqlite3.connect(db_path)

    # reading the data from the sqlite db
    df = pd.read_sql_query('SELECT * FROM tickdata', db)

    # closing the connection to the db
    db.close()

    # Convert the DateTime column to pandas datetime
    df['DateTime'] = pd.to_datetime(df['DateTime'], format='mixed')

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
            vw_data = todays_date[(todays_date['DateTime'] >= start_time) & (todays_date['DateTime'] < end_time)]
            
            if not vw_data.empty:
                vw_avg_price = (vw_data['Price'] * vw_data['LotsTraded']).sum() / vw_data['LotsTraded'].sum()
            else:
                vw_avg_price = None
            
            # Check if the first price of the day is traded after 17:15:00
            after_time = datetime.combine(current_date.date(), time(17, 15))
            after_data = todays_date[todays_date['DateTime'] >= after_time]
            
            if not after_data.empty and first_price in after_data['Price'].values:
                flag = True
                first_trade_time = after_data[after_data['Price'] == first_price].iloc[0]['DateTime']
            else:
                flag = False
                first_trade_time = None
            
            # Append the results for the current day
            results.append({
                'day': current_date.strftime('%Y-%m-%d'),
                'first_price': first_price,
                'vw_avg_price': vw_avg_price,
                'flag': flag,
                'first_trade_time': first_trade_time.strftime('%H:%M:%S.%f') if first_trade_time else None
            })
        
        # Move to the next day
        current_date += pd.Timedelta(days=1)

    # Convert the results to a DataFrame
    results_df = pd.DataFrame(results)
    
    return results_df

def main():
    # Set the path to the SQLite database
    db_path = 'data/BNZ12.sqlite'
    
    # Set the date range
    start_date, end_date = '2012-09-05', '2012-12-04'
    
    # Process the data
    results_df = process_bund_futures_data(db_path, start_date, end_date)
    
    # Create 'output' directory if it doesn't exist
    os.makedirs('output', exist_ok=True)
    
    # Save the results to a CSV file in the 'output' folder
    results_df.to_csv('output/results.csv', index=False)
    
    print("Processing complete. Results saved to 'output/results.csv'.")

if __name__ == "__main__":
    main()