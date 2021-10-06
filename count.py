
with open('log/stocks.txt', 'r') as f:
    trades = f.read().strip('][').split(', ')
trades = [float(x) for x in trades]

print(len(trades))