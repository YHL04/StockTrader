import datetime
import threading
import alpaca_trade_api as tradeapi
import yfinance as yf
import time
import numpy as np

from render import render
from utils import load_history, save_history
import keys

from config import *


class TradeAgent(object):
    def __init__(self, render=True):
        self.alpaca = tradeapi.REST(keys.API_KEY,
                                    keys.SECRET_KEY,
                                    keys.BASE_URL,
                                    "v2")

        self.render = render
        self.ticker = "TSM"
        self.margin = 0.25
        self.price_ceiling = 140
        self.history = load_history()
        print(self.history)
        self.get_history()

    def run(self):
        if self.render: render(self.history, self.get_prices("3d"))

        # First, cancel any existing orders so they don't impact our buying power.
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            self.alpaca.cancel_order(order.id)

        # Wait for market to open.
        print("Waiting for market to open... Holding Positions: " + str(self.get_positions() - num_hold))
        tAMO = threading.Thread(target=self.await_market_open)
        tAMO.start()
        tAMO.join()
        print("Market opened.")


        while True:
            if self.render: render(self.history, self.get_prices("3d"))
            clock = self.alpaca.get_clock()
            closing_time = clock.next_close.replace(tzinfo=datetime.timezone.utc).timestamp()
            current_time = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            self.time_to_close = closing_time - current_time

            if (self.time_to_close < (60 * 1)):
                # Run script again after market close for next trading day.
                self.clear_orders()
                print("Sleeping until market close (1 minutes).")
                time.sleep(60 * 1)

            if not clock.is_open:
                tAMO = threading.Thread(target=self.await_market_open)
                tAMO.start()
                tAMO.join()
                print("Market opened again.")

            else:
                # Market is open, run step
                step = threading.Thread(target=self.step)
                step.start()
                step.join()
                time.sleep(60)

    def await_market_open(self):
        is_open = self.alpaca.get_clock().is_open
        while (not is_open):
            clock = self.alpaca.get_clock()
            opening_time = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
            current_time = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
            time_to_open = int((opening_time - current_time) / 60)
            print(str(time_to_open) + " minutes til market open.")
            time.sleep(60)
            is_open = self.alpaca.get_clock().is_open


    """can't use REST api without subscription, use yfinance to retrieve real time data"""
    def get_prices(self, period):
        data = yf.download(tickers=self.ticker, period=period, interval="1m", progress=False).dropna()
        return data

    def submit_buy_order(self, price, qty):
        try:
            self.alpaca.submit_order(symbol=self.ticker,
                                     qty=str(qty),
                                     side="buy",
                                     type="limit",
                                     time_in_force="day",
                                     limit_price=str(round(price, 2)))
            print("{} \t {} \t Qty: {}".format("buy", price, qty))
        except Exception as e:
            print("Error:")
            print(e)
            print("Trying again...")
            time.sleep(0.5)
            self.submit_buy_order(price, qty)

    def submit_sell_order(self, price, qty):
        try:
            self.alpaca.submit_order(symbol=self.ticker,
                                     qty=str(qty),
                                     side="sell",
                                     type="limit",
                                     time_in_force="day",
                                     limit_price=str(round(price, 2)))
            print("{} \t {} \t Qty: {}".format("sell", price, qty))
        except Exception as e:
            print("Error:")
            print(e)
            print("Trying again...")
            time.sleep(0.5)
            self.submit_sell_order(price, qty)

    def clear_orders(self):
        # Clear existing orders again.
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
            self.alpaca.cancel_order(order.id)

    def get_positions(self):
        qty = 0
        positions = self.alpaca.list_positions()
        for position in positions:
            if position.symbol == self.ticker:
                qty += int(position.qty)
        return qty

    def sort_history(self, after=start_date):
        dates = []
        for hist in self.history:
            if hist["submitted_at"] > after:
                dates.append(hist["submitted_at"])
        dates = np.array(dates)
        index = np.argsort(dates)

        temp = []
        for i in index:
            temp.append(self.history[i])

        self.history = temp


    def get_history(self, limit=1000):
        orders = self.alpaca.list_orders(status="all", limit=limit)
        for order in orders:
            if order.symbol == self.ticker and \
               order.status == "filled" and \
               order.__dict__["_raw"] not in self.history:
                self.history.append(order.__dict__["_raw"])

        self.sort_history()


    def get_trade_prices(self):
        self.get_history()

        trade_prices = []
        for order in self.history:
            if order["side"] == "buy":
                for i in range(int(order["qty"])):
                    trade_prices.append(float(order["filled_avg_price"]))
            if order["side"] == "sell":
                for i in range(int(order["qty"])):
                    trade_prices.remove(min(trade_prices))
        return trade_prices

    def step(self):
        self.clear_orders()

        bars = self.get_prices(period="5m")
        current_price = bars["Close"].iloc[-1]

        self.trade_prices = self.get_trade_prices()
        position = self.get_positions()
        qty = position - num_hold


        # Logging
        dt_string = datetime.datetime.now()
        try:
            print("{} \t {} \t Qty: {} \t Min: {} \t List: {}".format(dt_string, current_price, qty, min(self.trade_prices), self.trade_prices))
        except:
            print("{} \t {} \t Qty: {} \t Min: {} \t List: {}".format(dt_string, current_price, qty, "not available", self.trade_prices))
        assert qty == len(self.trade_prices), f"qty: {qty} len(self.trade_prices): {len(self.trade_prices)}"

        # Execute Strategy
        if current_price <= 140:
            if qty == 0:
                self.submit_buy_order(price=current_price, qty=4)

            elif current_price <= 130:
                min_price = min(self.trade_prices)
                if self.trade_prices.count(min_price) >= 4:
                    self.submit_sell_order(min_price+self.margin, qty=4)
                else:
                    self.submit_sell_order(min_price+self.margin, qty=self.trade_prices.count(min_price))
                self.submit_buy_order(min_price-self.margin, qty=4)

            else:
                min_price = min(self.trade_prices)
                self.submit_sell_order(min_price+self.margin, qty=self.trade_prices.count(min_price))
                self.submit_buy_order(min_price-self.margin, qty=2)

        save_history(self.history)

if __name__ == "__main__":
    main = TradeAgent()
    main.run()
