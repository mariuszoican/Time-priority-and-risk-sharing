import pandas as pd
import datetime as dt
import numpy as np
from sklearn.preprocessing import StandardScaler


prod_list=['TYG','STF','FYG'] # list of products to be tested
cols_df = ['Frequency','Product','Date','AvgPairwiseCorr']

df_corr = pd.DataFrame(columns=cols_df)  # data frame for variances

frq_list=['30s','30T','1H', '2H']
mm_share=pd.read_csv('../ProcessedData/BBO_presence_MM.csv')

corr_df=pd.DataFrame()

for frq in frq_list:

    print(frq)

    # load data & get dates
    data=pd.read_csv('../ProcessedData/Inventories/inventory_panel_%s.csv'%frq)
    # select only top MMs
    data=data[data.account.isin(mm_share[mm_share.BBO_share>0.2]['account'].tolist())]


    data['date']=data['datetime'].apply(lambda x: x[0:10])
    list_dates=data['date'].drop_duplicates().tolist()

    # get inventory by product
    data['Product'] = data['externalSymbol'].map(lambda x: x[0:3])
    data_product = data.groupby(['datetime', 'date',
                                 'account', 'Product'])['signed_quantity'].sum().reset_index()
    data_product['Inventory']=data_product.groupby(['account','Product']).cumsum()


    for p in prod_list:

            print(p)
            for d in list_dates:
                print (d)

                temp=data_product[(data_product.Product==p) & (data_product.date==d)] # select the day
                temp=temp.pivot(index='datetime',columns='account',
                                values='Inventory').fillna(method='ffill').fillna(method='bfill')

                # Raw cost estimation
                correlation=np.triu(temp.corr(),1).sum()/(0.5*len(temp.corr())*(len(temp.corr())-1))

                new_row = [frq, p, d, correlation]
                df_corr.loc[df_corr.shape[0]] = new_row

print("Saving for frequency...")
df_corr.to_csv('../ProcessedData/Inventories/InvCorrelations.csv')