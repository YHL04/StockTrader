import alpaca_trade_api as tradeapi
from config import *
from datetime import datetime

api = tradeapi.REST(
    API_KEY,
    SECRET_KEY,
    BASE_URL
)

def check_portfolio_sync(qty):
    position = api.get_position("TSM")
    if abs(int(qty) - int(position.qty)) < 9:
        return True
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time)
    print("Program portfolio: ", qty)
    print("Alpaca portfolio: ", position.qty)
    return False
