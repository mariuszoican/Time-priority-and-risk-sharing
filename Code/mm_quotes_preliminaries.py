import os
import warnings
import pandas as pd
import datetime as dt

warnings.filterwarnings("ignore")

# read MM labels
mm_labels = pd.read_csv('../ProcessedData/mm_hft_labels.csv')

path = '../ProcessedData/MarginalQuotePanels/'
list_files = os.listdir(path)
subsets = ['mm', 'hft']

toselect = subsets[0]

list_dfs = []

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
    temp = temp[temp['%slabel' % toselect] == 1]
    list_dfs.append(temp)

data_full = list_dfs[0].append(list_dfs[1:], ignore_index=True)

# extract dates
data_full['date'] = data_full['datetime'].dt.date


data_full.to_csv('../ProcessedData/mquotes_%s.csv'%toselect)
