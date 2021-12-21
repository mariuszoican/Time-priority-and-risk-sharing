import pandas as pd
from statsmodels.tsa.ar_model import AutoReg
import numpy as np
import warnings

warnings.filterwarnings('ignore')

data=pd.read_csv('../ProcessedData/Inventories/inventory_panel_30s.csv',index_col=0)

data['date'] = data['datetime'].apply(lambda x: x[0:10])
list_dates = data['date'].drop_duplicates().tolist()

# get inventory by product
data['Product'] = data['externalSymbol'].map(lambda x: x[0:3])
data_product = data.groupby(['datetime', 'date',
                             'account', 'Product'])['signed_quantity'].sum().reset_index()
data_product['Inventory'] = data_product.groupby(['account', 'Product']).cumsum()

data_MR=pd.DataFrame(columns=['Product','Date','account','inv_halflife_min'])

for p in data_product['Product'].drop_duplicates().tolist():

    print(p)

    for d in list_dates:

        print(d)

        temp=data_product[(data_product.Product==p) & (data_product.date==d)]
        temp=temp.pivot(index='datetime',columns='account',
                                    values='Inventory').fillna(method='ffill').fillna(method='bfill').reset_index()

        list_mms=temp.columns[1:]

        for mm in list_mms:

            #print(mm)

            mod = AutoReg(temp[mm], lags=1)
            res = mod.fit()
            hl=-np.log(2)/np.log(res.params[1])

            data_MR=data_MR.append({'Product':p,'Date':d,'account':mm,'inv_halflife_min':hl/2},ignore_index=True)

data_MR.to_csv('../ProcessedData/inventory_halflife.csv')