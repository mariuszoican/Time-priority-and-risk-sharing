import os
import warnings
import pandas as pd
import datetime as dt

warnings.filterwarnings("ignore")

# read MM labels
mm_labels = pd.read_csv('../ProcessedData/mm_hft_labels.csv')

path = '../ProcessedData/MarginalQuotePanels/'
pathzf = '../ProcessedData/MarginalQuotePanels_ZeroFilled/'
list_files = os.listdir(path)
subsets = ['mm', 'hft']

toselect = subsets[0]

for f in list_files:

    print(f)

    temp = pd.read_csv(path + f, index_col=0)
    temp = temp.merge(mm_labels[['account', '%slabel' % toselect]])
    temp['datetime'] = temp['datetime'].apply(lambda x: dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
    temp['priority_levels'] = temp.groupby(['externalSymbol', 'datetime', 'side'])['priority'].transform('max')

    start = dt.datetime(temp['datetime'][0].date().year, temp['datetime'][0].date().month,
                        temp['datetime'][0].date().day, 2, 0, 0)
    end = dt.datetime(temp['datetime'][0].date().year, temp['datetime'][0].date().month, temp['datetime'][0].date().day,
                      18, 0, 0)
    list_timestamps = pd.date_range(start=start, end=end, freq='30s')
    temp = temp[temp['datetime'].isin(list_timestamps)]

    # symbol timestamp snapshots
    temp['symbol_timestamp'] = list(zip(temp.externalSymbol, temp.datetime))
    list_ss = temp['symbol_timestamp'].drop_duplicates().to_list()

    print("----Preliminaries done. Looping over %s snapshots!" % str(len(list_ss)))

    ss_dataframes = []

    for ss in list_ss:
        temp_ss = temp[temp.symbol_timestamp == ss]

        # get active traders
        set_ask = set(temp_ss[temp_ss.side == 'ask']['account'])
        set_bid = set(temp_ss[temp_ss.side == 'bid']['account'])

        not_bid_ID = set_ask - set_bid
        not_ask_ID = set_bid - set_ask

        tb = temp_ss[(temp_ss.side == 'ask') & (temp_ss['account'].isin(not_bid_ID))]
        ta = temp_ss[(temp_ss.side == 'bid') & (temp_ss['account'].isin(not_ask_ID))]

        # Update columns
        tb['side'] = 'bid'
        tb['quantity'] = 0
        tb['MarginalQuote_Inventory'] = tb['Cumulative_Inventory']
        tb['Depth_Total_Side'] = tb['Depth_Total_Both'] - tb['Depth_Total_Side']
        tb['Depth_AtQuote_Side'] = tb['Depth_Total_Side']
        tb['Depth_AtQuote_Side_Own'] = 0
        tb['Depth_BeforeQuote_Side'] = tb['Depth_Total_Side']
        tb['Depth_BeforeQuote_Side_Own'] = 0
        tb['priority'] = temp_ss[(temp_ss.side == 'bid')].priority.max() + 1
        tb['priority_levels'] = temp_ss[(temp_ss.side == 'bid')].priority.max()

        # Update columns
        ta['side'] = 'ask'
        ta['quantity'] = 0
        ta['MarginalQuote_Inventory'] = ta['Cumulative_Inventory']
        ta['Depth_Total_Side'] = ta['Depth_Total_Both'] - ta['Depth_Total_Side']
        ta['Depth_AtQuote_Side'] = ta['Depth_Total_Side']
        ta['Depth_AtQuote_Side_Own'] = 0
        ta['Depth_BeforeQuote_Side'] = ta['Depth_Total_Side']
        ta['Depth_BeforeQuote_Side_Own'] = 0
        ta['priority'] = temp_ss[(temp_ss.side == 'ask')].priority.max() + 1
        ta['priority_levels'] = temp_ss[(temp_ss.side == 'ask')].priority.max()

        # put things together
        temp_ss2 = temp_ss.append(ta.append(tb))
        ss_dataframes.append(temp_ss2)

    print("----Loop is done, merging!")
    temp2 = ss_dataframes[0].append(ss_dataframes[1:])
    temp2 = temp2.reset_index(drop=True)

    temp2.to_csv(pathzf + f.split(".")[0] + "_ZF" + ".csv.gz", compression='gzip')