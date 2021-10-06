from matplotlib import pyplot as plt
import pandas as pd


def get_minute_bar():
    minute_bar = pd.read_csv("log/minute_bar.txt", names=["Time", "Price"])
    minute_bar["Time"] = pd.to_datetime(minute_bar["Time"])
    minute_bar.set_index("Time", inplace=True)

    return minute_bar


def get_trades_history():
    trades = pd.read_csv("log/trades.txt", names=["Time", "Direction", "Trade", "qty"])
    trades["Time"] = pd.to_datetime(trades["Time"])
    trades.set_index("Time", inplace=True)

    trades["Direction"].replace(" ", "", inplace=True)

    return trades



minute_bar = get_minute_bar()
trades = get_trades_history()
mask = ['red' if x == ' sell' else 'blue' for x in trades["Direction"].to_list()]
quantity = [x for x in trades["qty"].to_list()]

"""
First plot: Prices and direction of trades
"""
#plt.subplot(2, 1, 1)
plt.xticks(rotation=90)

plt.plot(minute_bar.index, minute_bar["Price"], c="lightskyblue")
plt.scatter(trades.index, trades.Trade, s=5, c=mask, zorder=5)


"""
Second plot: Pure profit history
"""
# plt.subplot(2, 1, 2)
# plt.xticks(rotation=90)
#
# direction = trades["Direction"].to_list()
# trade_price = trades["Trade"].to_list()
# quantity = trades["qty"].to_list()
#
# stock_count = 0
# stock_count_history = []
#
# for dr, p, qty in zip(direction, trade_price, quantity):
#     if dr == " buy":
#         stock_count += qty
#     if dr == " sell":
#         stock_count -= qty
#
#     stock_count_history.append(stock_count)
#
# plt.plot(stock_count_history)
plt.show()

# profit = 0
# buy_prices = []
# profit_list = []
# equity_list = []
#
# for dr, p in zip(direction, trade_price):
#     if dr == " buy":
#         buy_prices.append(p)
#     if dr == " sell":
#         profit += p - min(buy_prices)
#         buy_prices.remove(min(buy_prices))
#
#
#     change = profit + (len(buy_prices)*p) - (sum(buy_prices))
#     equity = change
#
#     profit_list.append(profit)
#     equity_list.append(equity)
# plt.plot(trades.index, profit_list)
#
# plt.subplot(4, 1, 3)
# stocks = 0
# stocks_list = []
# for dr in direction:
#     if dr == " buy":
#         stocks += 1
#     else:
#         stocks -= 1
#
#     stocks_list.append(stocks)
#
# plt.plot(trades.index, stocks_list)
#
# plt.subplot(4, 1, 4)
# plt.plot(trades.index, equity_list)
#
# plt.show()

