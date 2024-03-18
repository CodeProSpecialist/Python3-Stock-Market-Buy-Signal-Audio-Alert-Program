import subprocess
import yfinance as yf
import numpy as np
import pytz
import time
import talib

def get_opening_price(symbol):
    stock_data = yf.Ticker(symbol)
    return round(stock_data.history(period="1d")["Open"].iloc[0], 4)

def get_current_price(symbol):
    stock_data = yf.Ticker(symbol)
    return round(stock_data.history(period='1d')['Close'].iloc[0], 4)

def get_yesterday_close_price(symbol):
    stock_data = yf.Ticker(symbol)
    return round(stock_data.history(period="2d")["Close"].iloc[0], 4)

def calculate_technical_indicators(symbol, lookback_days=90):
    stock_data = yf.Ticker(symbol)
    historical_data = stock_data.history(period=f'{lookback_days}d')

    short_window = 12
    long_window = 26
    signal_window = 9
    historical_data['macd'], historical_data['signal'], _ = talib.MACD(historical_data['Close'],
                                                                       fastperiod=short_window,
                                                                       slowperiod=long_window,
                                                                       signalperiod=signal_window)

    rsi_period = 14
    historical_data['rsi'] = talib.RSI(historical_data['Close'], timeperiod=rsi_period)

    historical_data['volume'] = historical_data['Volume']

    return historical_data

def print_technical_indicators(symbol, historical_data):
    print("")
    print(f"\nTechnical Indicators for {symbol}:\n")
    print(historical_data[['Close', 'macd', 'signal', 'rsi', 'volume']].tail())
    print("")

def get_data(symbol, start_date, end_date):
    data = yf.download(symbol, start=start_date, end=end_date)
    return data

def analyze_stock(symbol):
    end_date = datetime.today().strftime('%Y-%m-%d')
    start_date_6_months_ago = (datetime.today() - timedelta(days=180)).strftime('%Y-%m-%d')

    data_6_months = get_data(symbol, start_date_6_months_ago, end_date).values

    current_close_price = data_6_months[-1, 3]
    current_open_price = data_6_months[-1, 0]
    current_price = get_current_price(symbol)
    yesterday_close_price = get_yesterday_close_price(symbol)
    current_volume = data_6_months[-1, 5]
    average_volume = np.mean(data_6_months[:, 5])

    rsi_6_months, macd_6_months, _ = calculate_technical_indicators(symbol)

    if (current_price > current_open_price) and \
            (current_price > yesterday_close_price) and \
            ((current_volume > average_volume) or (current_volume >= 0.9 * average_volume)) and \
            (rsi_6_months[-1] > 55):
        return True, round(current_close_price, 2), round(current_open_price, 2), round(current_price, 2), round(yesterday_close_price, 2), current_volume, average_volume, round(rsi_6_months[-1], 2), round(macd_6_months[-1], 2)
    else:
        return False, round(current_close_price, 2), round(current_open_price, 2), round(current_price, 2), round(yesterday_close_price, 2), current_volume, average_volume, round(rsi_6_months[-1], 2), round(macd_6_months[-1], 2)

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
                    recommended, close_price, open_price, current_price, yesterday_close_price, current_volume, average_volume, rsi, macd = analyze_stock(etf)
                    print(f"\nAnalysis for {etf}:")
                    print(f"Yesterday's Close Price: {yesterday_close_price:.2f}")
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
