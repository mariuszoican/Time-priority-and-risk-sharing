import os
import warnings
import numpy as np
import pandas as pd
import functions_tmxdata as tmx

warnings.filterwarnings("ignore")

path_OB = '../TMXData/topOfBook/'
list_dates = os.listdir(path_OB)  # list of dates
path_trades = '../TMXData/trades/'
avg_trade=pd.DataFrame(columns=['Date','AverageTrade'])

for date in list_dates:

    temp_trades = pd.read_csv(path_trades + date +'.csv.gz')

    if len(temp_trades) == 0:
        continue

    trades_data = tmx.prep_trades(temp_trades)  # process trades

    if len(trades_data) == 0:
        continue

    trades_data['quantity']=trades_data['quantity'].map(float)
    avg=trades_data.groupby(['externalSymbol','account','side','time'])['quantity'].sum().mean()
    print(date,avg)
    avg_trade=avg_trade.append({'Date':date,'AverageTrade':avg},ignore_index=True)
    print(avg_trade.head())


print("Final average:",avg_trade['AverageTrade'].mean())
