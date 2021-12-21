import os
import warnings
import numpy as np
import pandas as pd
import functions_tmxdata as tmx


def inventory_lo_panel(date, freq):
    temp_trades = pd.read_csv(path_trades + date +'.csv.gz')

    if len(temp_trades) == 0:
        return -1

    trades_data = tmx.prep_trades(temp_trades)  # process trades
    if len(trades_data) == 0:
        return -1

    trades_data = trades_data[trades_data['account'].isin(list_mm)]  # keep only MM

    trades_data['quantity'] = trades_data['quantity'].astype(int)  # convert quantity to int
    trades_data['hour'] = trades_data['datetime'].apply(lambda x: x.hour)

    trades_data['signed_quantity'] = np.where(trades_data['side'] == 'Buy',
                                              trades_data['quantity'], -trades_data['quantity'])

    # get inventory
    trades_panel_inv = trades_data.set_index('datetime').groupby(
        ['account', 'externalSymbol']).resample(freq)['signed_quantity'].sum().reset_index()


    # count share of trades as maker
    trades_data['maker'] = np.where(trades_data['initiation'] == 'Maker', 1, 0)
    trades_data['trade'] = 1

    trades_panel_maker = trades_data[trades_data.session == 'ContinuousTrading'].set_index('datetime').groupby(
        ['account', 'externalSymbol']).resample(freq)[['maker', 'trade']].sum().reset_index()
    trades_panel_maker['maker_ratio'] = trades_panel_maker['maker'] / trades_panel_maker['trade']

    trades_panel = trades_panel_inv.merge(trades_panel_maker,
                                          on=['account', 'externalSymbol', 'datetime'],
                                          how='outer')

    return trades_panel


warnings.filterwarnings("ignore")

path_OB = '../TMXData/topOfBook/'
list_dates = os.listdir(path_OB)  # list of dates
path_trades = '../TMXData/trades/'

print("Range: ", list_dates[0], list_dates[-1])

mm_labels = pd.read_csv('../ProcessedData/mm_hft_labels.csv')
list_mm = mm_labels[mm_labels['mmlabel'] == 1]['account'].tolist()

frq_list = ['30s', '1T', '2T', '5T', '10T', '30T', '1H', '2H', '4H']  # frequencies of sampling

for frq in frq_list:
    inv_data = pd.DataFrame()
    print(frq)
    for d in list_dates:
        print(d)
        temp = inventory_lo_panel(d, frq)

        if type(temp) == int:
            print('no trades')
        else:
            inv_data = inv_data.append(temp, ignore_index=True)

    inv_data.to_csv('../ProcessedData/Inventories/inventory_panel_%s.csv' % frq)
