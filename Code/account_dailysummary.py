import os
import numpy as np
import pandas as pd
import functions_tmxdata as tmx
import warnings
import datetime as dt
warnings.filterwarnings("ignore")


def get_info(account,symbol):
    # get trading data of this account
    data = trades[(trades['account'] == account) & (trades['externalSymbol']==symbol)]

    # get num of trades and day volume
    num = len(data)
    day_vol = data['quantity'].sum()

    # convert to datetime and set it to be the index
    data['a'] = data['datetime'].map(pd.to_datetime)
    data = data.set_index(data['a'])

    # generate change in position
    data['signal'] = np.where(data['side'] == 'Buy', 1, -1)
    data['delta_position'] = data['signal'] * data['quantity']

    # resample the data and fill untraded minute with zero
    data = data['delta_position'].resample('min').sum()
    date = data.index[0].date().strftime("%Y-%m-%d")
    data = data.reindex(pd.date_range(date + " 01:59", date + " 16:29", freq="1min"), fill_value=0)

    # get eod inventory and net position
    eod = data.sum()
    net = abs(eod) / day_vol

    # get minute inventory
    data = data.cumsum()
    data.rename('net postition in every minute')

    # get StdInventory
    std = np.sqrt((((data - eod) / day_vol) ** 2).mean())

    return [num, net, std, eod, day_vol]

path_OB = '../TMXData/topOfBook/'
list_dates = os.listdir(path_OB)  # list of dates
path_trades = '../TMXData/trades/'

list_traderdf=[]

print("Range: ",list_dates[0],list_dates[-1])

for date in list_dates:
    print(date)
    temp_trades = pd.read_csv(path_trades + date +'.csv.gz')
    if len(temp_trades) == 0:
        continue
    trades = tmx.prep_trades(temp_trades)
    if len(trades)==0:
        continue

    trades['quantity']=trades['quantity'].map(int)

    list_symbols=trades['externalSymbol'].drop_duplicates().to_list()

    list_dfdate=[]
    for symbol in list_symbols:
        #print(symbol)
        df = pd.DataFrame(trades[trades['externalSymbol']==symbol]['account'].drop_duplicates())
        df = df.reset_index(drop=True)
        info = df['account'].apply(lambda x: get_info(x,symbol))
        df['externalSymbol'] = symbol
        df['date'] = date
        df[['num_trades','NetPosition','StdInventory', 'eod', 'quantity']] = info.tolist()
        list_dfdate.append(df)
    df_date=list_dfdate[0].append(list_dfdate[1:],ignore_index=True)
    list_traderdf.append(df_date)

trader_df=list_traderdf[0].append(list_traderdf[1:],ignore_index=True)
trader_df.to_csv('../ProcessedData/account_EODdata.csv')



