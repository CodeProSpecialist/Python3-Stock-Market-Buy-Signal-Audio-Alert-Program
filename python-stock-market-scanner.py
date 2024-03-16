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
    # Calculate RSI
    close_prices = data[:, 4]
    rsi = RSI(close_prices, timeperiod=14)

    # Calculate MACD
    macd, macd_signal, _ = MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)

    return rsi, macd, macd_signal


def analyze_stock(symbol):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date_90_days_ago = (datetime.today() - timedelta(days=90)).strftime('%Y-%m-%d')
    start_date_8_days_ago = (datetime.today() - timedelta(days=8)).strftime('%Y-%m-%d')

    data_90_days = get_data(symbol, start_date_90_days_ago, end_date).values
    data_8_days = get_data(symbol, start_date_8_days_ago, end_date).values

    rsi_90_days, macd_90_days, _ = calculate_indicators(data_90_days)
    rsi_8_days, macd_8_days, macd_signal_8_days = calculate_indicators(data_8_days)

    # Conditions for recommending a stock
    if (data_8_days[-1, 5] > np.mean(data_90_days[:, 5]) * 1.5) and \
            (rsi_8_days[-1] > 50) and \
            (macd_8_days[-1] > macd_signal_8_days[-1]) and \
            (data_8_days[-1, 4] > data_90_days[-1, 4]) and \
            (data_8_days[-1, 4] > data_8_days[-2, 4]):
        return True, data_8_days[-1, 4], data_8_days[-1, 5]
    else:
        return False, data_8_days[-1, 4], data_8_days[-1, 5]


def get_next_run_time():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now()
    next_run_time = now.replace(hour=10, minute=15, second=0, microsecond=0)

    if now > next_run_time:
        next_run_time += timedelta(days=1)

    return eastern.localize(next_run_time)


def main():
    eastern = pytz.timezone('US/Eastern')
    next_run_time = get_next_run_time()

    print("Date and Time: ", datetime.now(eastern), "Eastern Time ")
    print("Next Run Time:", next_run_time.astimezone(eastern), "Eastern Time ")

    while True:
        now = datetime.now(eastern)

        if now >= next_run_time and now.hour < 16:
            print("Recommended Stocks to Buy Today:")
            etfs = ['SPY', 'QQQ', 'SPXL', 'VTI', 'VGT']

            for etf in etfs:
                recommended, close_price, volume = analyze_stock(etf)
                print(f"\nAnalysis for {etf}:")
                print(f"Close Price: {close_price}")
                print(f"Volume: {volume}")

                if recommended:
                    print(f"{etf} is recommended to buy today.")
                else:
                    print(f"{etf} is not recommended to buy today.")

            next_run_time += timedelta(seconds=30)
            print("\nNext Run Time:", next_run_time.astimezone(eastern), "Eastern Time ")

        time.sleep(30)


if __name__ == "__main__":
    main()
