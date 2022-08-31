import matplotlib.pyplot as plt
from datetime import datetime


def render(history, prices, show=False):
    plt.clf()

    color = ['red' if hist["side"] == 'sell' else 'blue' for hist in history]
    date = [datetime.strptime(hist["submitted_at"][:19], "%Y-%m-%dT%H:%M:%S") for hist in history]
    price = [float(hist["filled_avg_price"]) for hist in history]

    plt.plot(prices.index,
             prices["Close"], c="lightblue")

    plt.scatter(x=date,
                y=price,
                c=color,
                s=20,
                zorder=2)

    plt.pause(0.001)
    if show: plt.show()


if __name__ == "__main__":
    import yfinance as yf
    from main import load_history

    render(load_history(), yf.download(tickers="TSM", period="7d", interval="1m", progress=False).dropna(), show=True)
