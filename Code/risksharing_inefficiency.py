import pandas as pd
import datetime as dt
import numpy as np
from sklearn.preprocessing import StandardScaler


prod_list=['TYG','STF','FYG'] # list of products to be tested
cols_df = ['Product','Date','InefficiencyRaw','InefficiencyWeighted','InefficiencyWeightedOptimal']

df_inefficiency = pd.DataFrame(columns=cols_df)  # data frame for variances

frq='30s'
mm_share=pd.read_csv('../ProcessedData/BBO_presence_MM.csv')


divergence_df=pd.DataFrame()

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
            total_cost_raw = (temp ** 2).sum().sum()
            perfect_share_cost_raw = (temp.mean(axis=1) ** 2 * len(temp.columns)).sum()
            inefficiency_raw=total_cost_raw/perfect_share_cost_raw

            # Weighted average
            weights = 1 / temp.std()
            total_cost_weighted=((temp**2)*weights).sum().sum()
            perfect_share_cost_weighted = ((temp.mean(axis=1) ** 2)*np.sum(weights)).sum()
            inefficiency_weighted=total_cost_weighted / perfect_share_cost_weighted

            # Weighted optimal
            w2=temp.std()
            w2_adj=w2/(w2.sum())**2
            optimal_weighted_cost=(w2_adj.sum()*(temp.sum(axis=1)**2)).sum()
            if total_cost_weighted==0:
                inefficiency_weighted_opt=np.nan
            else:
                inefficiency_weighted_opt=total_cost_weighted/optimal_weighted_cost

            new_row = [p, d,inefficiency_raw,inefficiency_weighted,inefficiency_weighted_opt]
            df_inefficiency.loc[df_inefficiency.shape[0]] = new_row

print("Saving for frequency...")
df_inefficiency.to_csv('../ProcessedData/Inventories/InvInefficiency_%s.csv'%frq)