import pandas as pd
import os
import warnings
from matplotlib import font_manager
import datetime as dt

warnings.filterwarnings("ignore")


def settings_plot(ax):
    for label in ax.get_xticklabels():
        label.set_fontproperties(ticks_font)
    for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    return ax


sizeOfFont = 18
ticks_font = font_manager.FontProperties(size=sizeOfFont)


def select_files(lst):
    lst2 = []
    for i in lst:
        if i[0:2] != 'TC': # exclude 3 month CAD bankers' acceptance futures
            lst2.append(i)
    return lst2


path_OB = '../TMXData/topOfBook/'
list_dates = os.listdir(path_OB)  # list of dates

# list_mms=pd.read_csv('../ProcessedData/mm_hft_labels.csv')

# get list of market-makers
# mms=list_mms[list_mms['mmlabel']==1]['account'].drop_duplicates().tolist()

presenceDB = pd.DataFrame()

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

    #     print(date)
    #     try:
    #         temp=pd.read_csv('../ProcessedData/MarginalQuotePanels/marginal_quotes_%s.csv.gz'%date,index_col=0)
    #     except:
    #         print("no date")
    #         continue

    # keep only one quote per side-snapshot-account
    ob_temp = ob_temp.drop_duplicates(subset=['externalSymbol', 'datetime', 'side', 'account'])

    #    temp['mm']=1.0*(temp['account'].isin(mms))

    count_side = ob_temp.groupby(['externalSymbol', 'account', 'side']).count()['datetime'].reset_index()
    count_side = count_side.rename(columns={'datetime': 'no_snapshots'})
    count_side = count_side.pivot(index=['externalSymbol', 'account'], columns='side').fillna(0).reset_index()
    count_side.columns = ['externalSymbol', 'account', 'ask', 'bid']

    count_both = ob_temp.groupby(['account', 'externalSymbol'])['datetime'].unique().reset_index()
    count_both['snapshots_account'] = count_both['datetime'].apply(lambda x: len(x))
    del count_both['datetime']

    count_all = count_side.merge(count_both, on=['externalSymbol', 'account'], how='left')
    count_all['both'] = (count_all['ask'] + count_all['bid']) - count_all['snapshots_account']

    total_snapshots = ob_temp.drop_duplicates(subset=['externalSymbol', 'datetime']).groupby('externalSymbol').count()[
        'datetime'].reset_index()
    total_snapshots = total_snapshots.rename(columns={'datetime': 'total_snapshots'})

    count_all = count_all.merge(total_snapshots, on='externalSymbol', how='left')
    count_all['date'] = date

    count_all['share_bid'] = count_all['bid'] / count_all['total_snapshots']
    count_all['share_ask'] = count_all['ask'] / count_all['total_snapshots']
    count_all['share_both'] = count_all['both'] / count_all['total_snapshots']
    count_all['share_presence'] = count_all['snapshots_account'] / count_all['total_snapshots']

    presenceDB = presenceDB.append(count_all, ignore_index=True)

# presenceDB.to_csv('../ProcessedData/BBO_presence.csv')

p_account = presenceDB.groupby(['account']).sum()[['ask', 'bid', 'snapshots_account',
                                                      'both', 'total_snapshots']].reset_index()
p_account['ask_share'] = p_account['ask'] / p_account['total_snapshots']
p_account['bid_share'] = p_account['bid'] / p_account['total_snapshots']
p_account['BBO_share'] = p_account['snapshots_account'] / p_account['total_snapshots']
p_account['both_share'] = p_account['both'] / p_account['total_snapshots']

mm_share = p_account[['account', 'ask_share',
                      'bid_share', 'BBO_share', 'both_share']]

mm_share.to_csv('../ProcessedData/BBO_presence_MM.csv')
