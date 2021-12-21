import pandas as pd
import os

# make csv with all the accounts
account = pd.DataFrame()
path_Trades="../TMXData/trades"
list_trades=os.listdir(path_Trades) # trades

for trades in list_trades:
    print(trades)
    path_Trades = "../TMXData/trades/" + trades
    temp = pd.read_csv(path_Trades)
    if len(temp)==0:
        continue
    temp = temp[['account']]
    temp = temp.drop_duplicates()
    account = account.append(temp)

account = account.drop_duplicates()
account.to_csv("../ProcessedData/account.csv")