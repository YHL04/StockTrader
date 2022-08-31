import json
import os


def save_history(history):
    for order in history:
        with open(f"data/{order['submitted_at']}.json", "w") as f:
            json.dump(order, f, sort_keys=True, indent=4)


def load_history():
    order_list = os.listdir("data")
    history = []
    for order in order_list:
        with open(f"data/{order}", "rb") as f:
            history.append(json.load(f))
    return history


def calculate_balance(history):
    balances = []
    cash = 0
    qty = 0

    for order in history:
        if order["side"] == "buy":
            qty += int(order["qty"])
            cash -= int(order["qty"]) * float(order["filled_avg_price"])
        if order["side"] == "sell":
            qty -= int(order["qty"])
            cash += int(order["qty"]) * float(order["filled_avg_price"])

        balance = cash + qty * float(order["filled_avg_price"])
        balances.append(balance)

    return balances


if __name__ == "__main__":
    import matplotlib.pyplot as plt
    from datetime import datetime

    history = load_history()
    date = [datetime.strptime(hist["submitted_at"][:19], "%Y-%m-%dT%H:%M:%S") for hist in history]
    balance = calculate_balance(history)
    plt.plot(balance)
    plt.show()
