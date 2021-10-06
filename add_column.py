import pandas as pd

file = pd.read_csv("log/trades.txt", header=None)
file.columns = ['date', 'direction', 'price']
print(file)

file['qty'] = 1

print(file)
file.to_csv('log/trades.txt')
