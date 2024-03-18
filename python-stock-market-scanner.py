import subprocess
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
from talib import RSI, MACD
import pytz
import time

def get_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data

def calculate_indicators(data):
    close_prices = data['Close'].values
    if len(close_prices) < 14:  # Ensure enough data points for RSI calculation
        return [], [], []
    rsi = RSI(close_prices, timeperiod=14)
    if len(close_prices) < 26:  # Ensure enough data points for MACD calculation
        return rsi, [], []
    macd, macd_signal, _ = MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    return rsi, macd, macd_signal

def analyze_stock(symbol):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date_7_days_ago = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    start_date_1_day_ago = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    data_7_days = get_data(symbol, start_date_7_days_ago, end_date)
    data_1_day = get_data(symbol, start_date_1_day_ago, end_date)

    if data_7_days.empty or data_1_day.empty:
        return False, 0, 0, 0, 0, 0, 0, 0

    current_close_price = data_1_day['Close'].iloc[-1]
    current_open_price = data_1_day['Open'].iloc[-1]
    current_price = data_1_day['Close'].iloc[-1]
    current_volume = data_1_day['Volume'].iloc[-1]
    average_volume = np.mean(data_7_days['Volume'].values)

    rsi, macd, macd_signal = calculate_indicators(data_7_days)

    if len(rsi) == 0 or len(macd) == 0 or len(macd_signal) == 0:
        return False, round(current_close_price, 2), round(current_open_price, 2), round(current_price, 2), current_volume, average_volume, 0, 0

    if (current_price > current_open_price) and \
            (current_price > current_close_price) and \
            ((current_volume > average_volume) or (current_volume >= 0.9 * average_volume)) and \
            (rsi[-1] > 55):
        return True, round(current_close_price, 2), round(current_open_price, 2), round(current_price, 2), current_volume, average_volume, round(rsi[-1], 2), round(macd[-1], 2)
    else:
        return False, round(current_close_price, 2), round(current_open_price, 2), round(current_price, 2), current_volume, average_volume, round(rsi[-1], 2), round(macd[-1], 2)

def get_next_run_time():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now()
    next_run_time = now.replace(hour=10, minute=15, second=0, microsecond=0)

    if now > next_run_time:
        next_run_time += timedelta(days=1)

    while next_run_time.weekday() >= 5:
        next_run_time += timedelta(days=1)

    return eastern.localize(next_run_time)

def main():
    eastern = pytz.timezone('US/Eastern')
    next_run_time = get_next_run_time()

    print("Date and Time: ", datetime.now(eastern).strftime("%Y-%m-%d %I:%M:%S %p"), "Eastern Time ")
    print("Next Run Time:", next_run_time.astimezone(eastern).strftime("%Y-%m-%d %I:%M:%S %p"), "Eastern Time ")

    while True:
        now = datetime.now(eastern)

        if now >= next_run_time and now.hour < 16:
            if now.weekday() < 5:
                print("Recommended Stocks to Buy Today:")
                etfs = ['SPY', 'QQQ', 'SPXL', 'VTI', 'VGT']

                for etf in etfs:
                    recommended, close_price, open_price, current_price, current_volume, average_volume, rsi, macd = analyze_stock(etf)
                    print(f"\nAnalysis for {etf}:")
                    print(f"Yesterday's Close Price: {close_price:.2f}")
                    print(f"Open Price for Today: {open_price:.2f}")
                    print(f"Current Price: {current_price:.2f}")
                    print(f"Current Volume: {current_volume:.2f}")
                    print(f"Average Volume: {average_volume:.2f}")
                    print(f"RSI: {rsi}")
                    print(f"MACD: {macd}")

                    if recommended:
                        print(f"{etf} is recommended to buy today.")
                        subprocess.run(["espeak", f"Time to buy {etf} right now."])
                    else:
                        print(f"{etf} is not recommended to buy today.")

                next_run_time += timedelta(seconds=30)
                print("\nNext Run Time:", next_run_time.astimezone(eastern).strftime("%Y-%m-%d %I:%M:%S %p"), "Eastern Time ")

        time.sleep(30)

if __name__ == "__main__":
    while True:
        try:
            main()
        except Exception as e:
            print("An error occurred:", e)
            print("Restarting the program in 5 seconds...")
            time.sleep(5)
