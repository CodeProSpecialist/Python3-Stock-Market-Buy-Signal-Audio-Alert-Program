import yfinance as yf
from datetime import datetime, timedelta
import numpy as np
from talib import RSI, MACD

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

def main():
    etfs = ['SPY', 'QQQ', 'SPXL', 'VTI', 'VGT']
    
    print("Date and Time:", datetime.now())
    print("Recommended Stocks to Buy Today:")
    
    for etf in etfs:
        recommended, close_price, volume = analyze_stock(etf)
        print(f"\nAnalysis for {etf}:")
        print(f"Close Price: {close_price}")
        print(f"Volume: {volume}")
        
        if recommended:
            print(f"{etf} is recommended to buy today.")
        else:
            print(f"{etf} is not recommended to buy today.")

if __name__ == "__main__":
    main()
