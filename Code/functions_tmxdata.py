## Collection of Python functions for data pre-processing
## ------------------------------------------------------

import datetime as dt
import numpy as np
import pandas as pd

def prep_trades(temp_trade):
    # convert dates
    temp_trade['datetime']=temp_trade['date'].astype(str)+"_"+temp_trade['time'].astype(str)+"."+temp_trade['milliseconds'].astype(str)
    temp_trade['datetime'] = temp_trade['datetime'].apply(lambda x: dt.datetime.strptime(x, "%Y%m%d_%H%M%S.%f"))
    return temp_trade

# def build_inv(trades,freq=5):
#     # function to build trader inventory, given a DataFrame of daily trades.
#     # second input "freq" is the frequency to sample cumulative inventory. Set by default at 5 seconds.
#
#     trades = trades.sort_values(by='number', ascending=True) # sort trades by number, in case they are not sorted
#     trades['side_num'] = np.where(trades['side'] == 'Buy', 1, -1)  # Dummmy: +1 for buy, -1 for sells
#     trades['signed_quantity'] = trades['quantity'].map(float) * trades['side_num']  # compute signed quantity
#
#     # compute cumulative inventory
#     trades['cum_inventory'] = trades.groupby(['externalSymbol', 'account']).cumsum()['signed_quantity']
#     trades['cum_inventory'] = trades['cum_inventory'].fillna(0)
#     trades=trades.set_index('datetime')
#     trades_new = trades.groupby(['externalSymbol', 'account']
#                 ).resample("%ss"%str(freq)).last()['cum_inventory'].fillna(method='ffill').reset_index()
#     trades_new['datetime']=trades_new['datetime'].apply(lambda x: x+dt.timedelta(seconds=freq))
#     return trades_new

def build_inv(trades):
    # function to build trader inventory, given a DataFrame of daily trades.
    # second input "freq" is the frequency to sample cumulative inventory. Set by default at 5 seconds.

    trades = trades.sort_values(by='number', ascending=True) # sort trades by number, in case they are not sorted
    trades['side_num'] = np.where(trades['side'] == 'Buy', 1, -1)  # Dummmy: +1 for buy, -1 for sells
    trades['signed_quantity'] = trades['quantity'].map(float) * trades['side_num']  # compute signed quantity

    # compute cumulative inventory
    trades['cum_inventory'] = trades.groupby(['externalSymbol', 'account']).cumsum()['signed_quantity']
    trades['cum_inventory'] = trades['cum_inventory'].fillna(0)
    trades=trades.set_index('datetime')
    return trades

def process_ob(temp_order):

    # dummy +1 for ask trades, -1 for bid trades
    def side_dummy(x):
        import numpy as np
        if x == 'ask':
            return 1
        elif x == 'bid':
            return -1
        else:
            return np.nan

    # convert dates to native format
    temp_order['datetime']=temp_order['datetime'].apply(lambda x: dt.datetime.strptime(x,'%Y-%m-%d %H:%M:%S'))



    # sort data by time-side-priority
    OBData = temp_order.sort_values(by=['externalSymbol', 'datetime', 'side', 'priority'], ascending=True)
    # cumulative depth by side, until current priority level
    OBData['quantity'] = OBData['quantity'].map(int)
    OBData['cum_depth'] = OBData.groupby(['externalSymbol', 'datetime', 'side']).cumsum()['quantity']
    # compute top depth on same side
    OBData['depth_side'] = OBData.groupby(['externalSymbol', 'datetime', 'side'])['quantity'].transform('sum')
    # compute depth on both sides
    OBData['depth_twoside'] = OBData.groupby(['externalSymbol', 'datetime'])['quantity'].transform('sum')


    # compute order imbalance measures
    temp_OI = OBData.groupby(['externalSymbol', 'datetime', 'side'])['quantity'].sum().reset_index().pivot(
        index=['externalSymbol', 'datetime'],
        columns='side', values='quantity').reset_index()
    temp_OI['OrderImbalance'] = temp_OI['ask'] - temp_OI['bid']
    temp_OI['OrderImbalance_pct'] = temp_OI['OrderImbalance'] / (temp_OI['ask'] + temp_OI['bid'])
    OBData = OBData.merge(temp_OI, on=['externalSymbol', 'datetime'], how='left')


    # compute marginal quotes at account level

    # cumulative quantity for given trader
    OBData['own_cum_depth'] = OBData.groupby(['externalSymbol', 'datetime',
                                                 'side', 'account']).cumsum()['quantity']

    # quantity ahead in the book (overall)
    OBData['depth_ahead'] = OBData['cum_depth'] - OBData['quantity']

    # quantity ahead in the book (for given trader)
    OBData['own_depth_ahead'] = OBData['own_cum_depth'] - OBData['quantity']


    # compute spreads
    spreads = temp_order.groupby(['externalSymbol', 'datetime', 'side']).mean()['price'].reset_index().pivot(
        index=['externalSymbol', 'datetime'], columns='side', values='price')
    spreads['midpoint'] = (spreads['ask'] + spreads['bid']) / 2
    spreads['QSpread_bps'] = (spreads['ask'] - spreads['bid']) / spreads['midpoint'] * 10000
    spreads = spreads.reset_index()

    OBData = OBData.merge(spreads[['externalSymbol', 'datetime', 'QSpread_bps']], on=['externalSymbol', 'datetime'],
                            how='left')

    # only keep marginal quotes (lowest priority)
    marginalquotes = OBData.groupby(['externalSymbol', 'datetime', 'side', 'account']).last().reset_index()
    marginalquotes=marginalquotes.sort_values(by=['externalSymbol', 'datetime', 'side', 'priority'], ascending=True)

    return marginalquotes