from datetime import datetime, date, timedelta
import math
import numpy as np
import time
import sys
import requests
import yfinance as yf

class Program:
    def __init__(self, symbols, window_size, result_file):
        self.symbols = symbols
        self.window_size = window_size
        self.result_file = result_file

        self.num_trading_days_per_year = 252
        self.date_format = "%Y-%m-%d"
        self.end_date = datetime.today().strftime(self.date_format)
        self.start_date = (datetime.today() - timedelta(days=(self.window_size + 1)*2)).strftime(self.date_format)

    def get_stock_data(self, ticker, start_date, end_date):
        info = yf.Ticker(ticker)
        stock_data = info.history(start=start_date, end=end_date, interval="1d");
        # stock_data.to_csv("{} stock_prices.csv".format(ticker))
        return stock_data

    def get_volatility_and_performance(self, symbol):
        datas = self.get_stock_data(symbol,  self.start_date, self.end_date)
        close_datas = datas["Close"]
        prices = []

        for close_data in close_datas:
            prices.append(float(close_data))

        prices.reverse()
        volatilities_in_window = []

        for i in range(self.window_size):
            volatilities_in_window.append(math.log(prices[i] / prices[i+1]))

        return np.std(volatilities_in_window, ddof = 1) * np.sqrt(self.num_trading_days_per_year), prices[0] / prices[self.window_size] - 1.0

    def process(self):
        volatilities = []
        performances = []
        sum_inverse_volatility = 0.0
        for symbol in self.symbols:
            volatility, performance = self.get_volatility_and_performance(symbol)
            sum_inverse_volatility += 1 / volatility
            volatilities.append(volatility)
            performances.append(performance)

        f = open(self.result_file, 'w')

        print("Portfolio: {}, as of {} (window size is {} days)".format(str(self.symbols), date.today().strftime('%Y-%m-%d'), self.window_size), file=f)
        for i in range(len(self.symbols)):
            print('{} allocation ratio: {:.2f}% (anualized volatility: {:.2f}%, performance: {:.2f}%)'.format(self.symbols[i], float(100 / (volatilities[i] * sum_inverse_volatility)), float(volatilities[i] * 100), float(performances[i] * 100)), file=f)

        f.close()        

if __name__ == '__main__':
    if len(sys.argv) <= 3:
        symbols = ["QLD", "UBT"]
        window_size = 20
        result_file = "result.txt"
    else:
        symbols = sys.argv[1].split(',')
        for i in range(len(symbols)):
            symbols[i] = symbols[i].strip().upper()
        window_size = int(sys.argv[2])
        result_file = sys.argv[3]

    program = Program(symbols, window_size, result_file)
    program.process()