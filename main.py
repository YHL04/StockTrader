import alpaca_trade_api as tradeapi
import threading
import time
from datetime import datetime

import config
from test import *


# initially had 18 shares
api_key = config.API_KEY
api_secret = config.SECRET_KEY
base_url = config.BASE_URL
ws_url = config.WS_URL


stock = "TSM"
margin = 0.2

trades_log = open('log/trades.txt', 'a')
minute_bar_log = open('log/minute_bar.txt', 'a')


api = tradeapi.REST(api_key,
                    api_secret,
                    base_url=base_url,
                    api_version='v2')


def trade_market(direction, qty=1):
    order = api.submit_order(
                        symbol=stock,
                        qty=str(qty),
                        side=direction,
                        type='market',
                        time_in_force='day',
                        )

def trade_limit(direction, price, qty=1):
    order = api.submit_order(
        symbol=stock,
        qty=str(qty),
        side=direction,
        type='limit',
        time_in_force='day',
        limit_price=str(price)
    )


conn = tradeapi.stream2.StreamConn(
    api_key, api_secret, base_url=base_url, data_url=ws_url
)

@conn.on(r'^trade_updates$')
async def on_trade_updates(conn, channel, trade):
    global trades
    if 'fill' in trade.event:
        log = trade.order['side'] + "," + trade.order['filled_avg_price'] + "," + trade.order['qty']
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        print("{} {}".format(current_time, log))

        for i in range(int(trade.order['qty'])):
            if trade.order['side'] == 'buy':
                trades.append(float(trade.order['filled_avg_price']))
            elif trade.order['side'] == 'sell':
                trades.remove(min(trades))
            else:
                print(trade.order['side'])

        trades_log.write("{}, {}\n".format(datetime.now(), log))
        trades_log.flush()

        with open('log/stocks.txt', 'w') as f:
            f.write(str(trades))


# algorithm starts here

try:
    with open('log/stocks.txt', 'r') as f:
        trades = f.read().strip('][').split(', ')
    trades = [float(x) for x in trades]
except:
    print("No previous record of stocks.")
    trades = []

print('stocks', trades)
last_trade_price = 0


@conn.on('AM.TSM')
async def on_minute_bars(conn, channel, bar):
    api.cancel_all_orders()
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print(current_time, " ", bar.close)

    if check_portfolio_sync(len(trades)):

        if bar.close <= 140:

            if (len(trades) == 0):
                if bar.close <= 130:
                    trade_market('buy', qty=4)
                else:
                    trade_market('buy', qty=2)

            elif bar.close <= 130:
                min_trades = min(trades)
                if trades.count(min_trades) >= 4:
                    trade_limit('sell', min_trades+margin, qty=4)
                else:
                    trade_limit('sell', min_trades+margin, qty=trades.count(min_trades))
                trade_limit('buy', min_trades-margin, qty=4)

            else:
                min_trades = min(trades)
                trade_limit('sell', min_trades+margin, qty=trades.count(min_trades))
                trade_limit('buy', min_trades-margin, qty=2)

            minute_bar_log.write("{}, {}\n".format(datetime.now(), str(bar.close)))
            minute_bar_log.flush()


def ws_start():
    conn.run(['AM.TSM', 'trade_updates'])

ws_thread = threading.Thread(target=ws_start, daemon=True)


if __name__ == "__main__":

    clock = api.get_clock()
    print('The market is {}'.format('open.' if clock.is_open else 'closed.'))
    print('Waiting to open...')

    while not clock.is_open:
        clock = api.get_clock()
        time.sleep(100)

    print('ITS OPEN!')
    ws_thread.start()
    #ws_start()
    while True:
        time.sleep(1)
