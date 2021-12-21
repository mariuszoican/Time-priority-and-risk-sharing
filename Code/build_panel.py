import os
import warnings
import numpy as np
import pandas as pd
import functions_tmxdata as tmx
import datetime as dt


def inventory_to_time(symbol_account_time):
    symbol, account, time = symbol_account_time

    select_trades = trades[(trades.account == account) &
                           (trades.externalSymbol == symbol) & (trades.datetime <= time)]
    select_trades['side_num'] = np.where(select_trades['side'] == 'Buy', 1, -1)  # Dummy: +1 for buy, -1 for sells
    select_trades['signed_quantity'] = select_trades['quantity'].map(float) * select_trades[
        'side_num']  # compute signed quantity

    return select_trades.signed_quantity.sum()


def side_dummy(x):
    import numpy as np
    if x == 'ask':
        return 1
    elif x == 'bid':
        return -1
    else:
        return np.nan


def select_files(lst):
    lst2 = []
    for i in lst:
        if i[0:2] != 'TC': # exclude 3 month CAD bankers' acceptance futures
            lst2.append(i)
    return lst2


warnings.filterwarnings("ignore")

path_OB = '../TMXData/topOfBook/'
list_dates = os.listdir(path_OB)  # list of dates


for date in list_dates:

    if dt.datetime.strptime(date, '%Y%m%d').isoweekday() >= 6:
        print(date, "is weekend!")
        continue

    print(date)

    path_OB_date = path_OB + date + "/"
    list_files = select_files(os.listdir(path_OB_date))
    ob_temp = pd.DataFrame()

    for f in list_files:
        ob_temp = ob_temp.append(pd.read_csv(path_OB_date + f))

    # get marginal quotes panel
    mquotes = tmx.process_ob(ob_temp)
    mquotes['symbol_account_time'] = list(zip(mquotes.externalSymbol, mquotes.account, mquotes.datetime))

    # get cumulative inventory up-to-date
    path_trades = '../TMXData/trades/'
    temp_trades = pd.read_csv(path_trades + date + '.csv.gz')
    if len(temp_trades) == 0:
        continue
    trades = tmx.prep_trades(temp_trades)

    if len(trades) == 0:
        mquotes_new = mquotes.copy()

        mquotes_new['cum_inventory'] = 0
        mquotes_new['mod_inventory'] = 0

        cols_to_keep = ['externalSymbol', 'datetime', 'account', 'side', 'priority', 'quantity',
                        'cum_inventory', 'mod_inventory', 'QSpread_bps',
                        'cum_depth', 'depth_side', 'depth_twoside', 'depth_ahead', 'own_cum_depth', 'own_depth_ahead',
                        'OrderImbalance', 'OrderImbalance_pct'
                        ]
        mquotes_new = mquotes_new[cols_to_keep]

        mquotes_new = mquotes_new.rename(columns={'cum_inventory': 'Cumulative_Inventory',
                                                  'mod_inventory': 'MarginalQuote_Inventory',
                                                  'cum_depth': 'Depth_AtQuote_Side',
                                                  'depth_side': 'Depth_Total_Side',
                                                  'depth_twoside': 'Depth_Total_Both',
                                                  'depth_ahead': 'Depth_BeforeQuote_Side',
                                                  'own_cum_depth': 'Depth_AtQuote_Side_Own',
                                                  'own_depth_ahead': 'Depth_BeforeQuote_Side_Own'})

        mquotes_new.to_csv('../ProcessedData/MarginalQuotePanels/marginal_quotes_%s.csv.gz' % date, compression='gzip')
    else:

        trades_inv = tmx.build_inv(trades).reset_index()

        print("Start matching:")
        mquotes_new = pd.merge_asof(mquotes.sort_values('datetime'),
                                    trades_inv[
                                        ['externalSymbol', 'account', 'datetime', 'cum_inventory']].sort_values(
                                        'datetime'),
                                    on=['datetime'], by=['externalSymbol', 'account'])
        mquotes_new['cum_inventory'] = mquotes_new['cum_inventory'].fillna(0)
        mquotes_new = mquotes_new.sort_values(by=['externalSymbol', 'datetime', 'side', 'priority'])
        mquotes_new['mod_inventory'] = mquotes_new['cum_inventory'] + mquotes_new['own_depth_ahead'] * mquotes_new[
            'side'].apply(
            lambda x: -side_dummy(x))

        cols_to_keep = ['externalSymbol', 'datetime', 'account', 'side', 'priority', 'quantity',
                        'cum_inventory', 'mod_inventory', 'QSpread_bps',
                        'cum_depth', 'depth_side', 'depth_twoside', 'depth_ahead', 'own_cum_depth', 'own_depth_ahead',
                        'OrderImbalance', 'OrderImbalance_pct'
                        ]
        mquotes_new = mquotes_new[cols_to_keep]

        mquotes_new = mquotes_new.rename(columns={'cum_inventory': 'Cumulative_Inventory',
                                                  'mod_inventory': 'MarginalQuote_Inventory',
                                                  'cum_depth': 'Depth_AtQuote_Side',
                                                  'depth_side': 'Depth_Total_Side',
                                                  'depth_twoside': 'Depth_Total_Both',
                                                  'depth_ahead': 'Depth_BeforeQuote_Side',
                                                  'own_cum_depth': 'Depth_AtQuote_Side_Own',
                                                  'own_depth_ahead': 'Depth_BeforeQuote_Side_Own'})

        mquotes_new.to_csv('../ProcessedData/MarginalQuotePanels/marginal_quotes_%s.csv.gz' % date, compression='gzip')
