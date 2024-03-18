import subprocess
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
from talib import RSI, MACD
import pytz
import time

def get_top_increase_stocks(symbols):
    top_stocks = {}
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist_data = stock.history(period='1d')

            if not hist_data.empty:
                opening_price = hist_data['Open'].iloc[0]
                closing_price = hist_data['Close'].iloc[-1]
                price_increase = (closing_price - opening_price) / opening_price
                top_stocks[symbol] = price_increase
        except Exception as e:
            print(f"Error retrieving data for {symbol}: {e}")

        time.sleep(1)
    return dict(sorted(top_stocks.items(), key=lambda item: item[1], reverse=True))

def print_top_stocks(top_stocks):
    rank = 1
    for symbol, price_increase in top_stocks.items():
        try:
            stock = yf.Ticker(symbol)
            current_price = stock.history(period='1d')['Close'].iloc[-1]
            percent_change = price_increase * 100
            change_symbol = '+' if percent_change > 0 else '-'
            print(
                f"{rank}. {symbol}: ${current_price:.2f}, Open: ${stock.history(period='1d')['Open'].iloc[0]:.2f}, {change_symbol}{abs(percent_change):.2f}%")
            rank += 1
            time.sleep(1)
        except Exception as e:
            print(f"Error printing data for {symbol}: {e}")


def analyze_stock(symbol):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date_7_days_ago = (datetime.today() - timedelta(days=7)).strftime('%Y-%m-%d')
    start_date_1_day_ago = (datetime.today() - timedelta(days=1)).strftime('%Y-%m-%d')

    symbols = [symbol]
    top_stocks = get_top_increase_stocks(symbols)
    if symbol not in top_stocks:
        return None, None, None, None, None, None, None, None

    stock = yf.Ticker(symbol)
    data_7_days = stock.history(start=start_date_7_days_ago, end=end_date)
    data_1_day = stock.history(start=start_date_1_day_ago, end=end_date)

    if data_1_day.shape[0] > 1:
        historical_data = data_7_days
    else:
        historical_data = data_1_day

    if historical_data.empty:
        return None, None, None, None, None, None, None, None

    current_close_price = historical_data.iloc[-1]['Close']
    current_open_price = historical_data.iloc[0]['Open']
    current_price = stock.history(period='1d')['Close'].iloc[-1]
    current_volume = historical_data.iloc[-1]['Volume']
    average_volume = np.mean(historical_data['Volume'])

    rsi_7_days, macd_7_days, _ = calculate_indicators(data_7_days)
    rsi_1_day, macd_1_day, macd_signal_1_day = calculate_indicators(data_1_day)

    if current_open_price is not None and current_price is not None:
        if (current_open_price > current_close_price) and \
                ((current_volume > average_volume) or (current_volume >= 0.9 * average_volume)) and \
                (rsi_1_day[-1] > 55) and \
                (macd_1_day[-1] > macd_signal_1_day[-1]):
            return True, round(current_close_price, 2), round(current_open_price, 2), round(current_price, 2), current_volume, average_volume, round(rsi_1_day[-1], 2), round(macd_1_day[-1], 2)
    else:
        return None, None, None, None, None, None, None, None


def calculate_indicators(data):
    close_prices = data['Close']
    rsi = RSI(close_prices, timeperiod=14)
    macd, macd_signal, _ = MACD(close_prices, fastperiod=12, slowperiod=26, signalperiod=9)
    return rsi, macd, macd_signal

def get_next_run_time():
    eastern = pytz.timezone('US/Eastern')
    now = datetime.now()
    next_run_time = now.replace(hour=10, minute=15, second=0, microsecond=0)

    if now.hour >= 16:
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

                    if recommended is not None:
                        print(f"\nAnalysis for {etf}:")
                        if close_price is not None:
                            print(f"Yesterday's Close Price: {close_price:.2f}")
                        if open_price is not None:
                            print(f"Open Price for Today: {open_price:.2f}")
                        if current_price is not None:
                            print(f"Current Price: {current_price:.2f}")
                        if current_volume is not None:
                            print(f"Current Volume: {current_volume:.2f}")
                        if average_volume is not None:
                            print(f"Average Volume: {average_volume:.2f}")
                        if rsi is not None:
                            print(f"RSI: {rsi}")
                        if macd is not None:
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
