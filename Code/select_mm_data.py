import pandas as pd
import os
import datetime as dt

# read MM labels
mm_labels = pd.read_csv('../ProcessedData/mm_hft_labels.csv')

path='../ProcessedData/MarginalQuotePanels_ZeroFilled/'

list_files = os.listdir(path)

subsets = ['mm', 'hft']

toselect = subsets[0]

list_dfs = []
for f in list_files:
    print(f)
    temp = pd.read_csv(path + f, index_col=0)
    # temp=temp.merge(mm_labels[['account','%slabel'%toselect]])
    # keep only MM quotes
    temp = temp[temp['%slabel' % toselect] == 1]
    list_dfs.append(temp)
    print()

data_full = list_dfs[0].append(list_dfs[1:], ignore_index=True)

# extract dates
data_full['datetime'] = data_full['datetime'].apply(lambda x: dt.datetime.strptime(x, "%Y-%m-%d %H:%M:%S"))
data_full['date'] = data_full['datetime'].dt.date

data_full.to_csv('../ProcessedData/mquotes_ZF_%s.csv'%toselect)



