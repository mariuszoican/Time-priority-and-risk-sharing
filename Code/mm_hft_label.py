import pandas as pd

# load trader data
traderEOD=pd.read_csv('../ProcessedData/account_EODdata.csv',index_col=0)


traderEOD['class']=traderEOD['externalSymbol'].apply(lambda x: x[0:3])
BBO_presence=pd.read_csv('../ProcessedData/BBO_presence_MM.csv')


# aggregate account data
accounts=traderEOD.groupby(['account']).mean()[[
    'num_trades','quantity','StdInventory','NetPosition']].reset_index()

accounts=accounts.merge(BBO_presence,on=['account'],how='left')

netpos=0.05
stdinv=0.05 # updated from 0.025 to 0.05 to generate more MM accounts on the scrambled data set.
notrades=50
quant=10

accounts['mmlabel']=1*((accounts.NetPosition<=netpos) &
                       (accounts.StdInventory<=stdinv) &
                       (accounts.num_trades>=notrades) &
                       (accounts.BBO_share>=0.2))



# HFT label construction
HFT=['042', '168','126'] # HFT labels

account=pd.read_csv('../ProcessedData/account.csv',index_col=0)


list_hft = account[account['account'].astype(str).str[:3].isin(HFT)]['account'].drop_duplicates().to_list()

accounts['hftlabel']=1*(accounts['account'].isin(list_hft))

accounts.to_csv('../ProcessedData/mm_hft_labels.csv')


traderEOD_2=traderEOD.merge(accounts[['account','mmlabel','hftlabel','BBO_share']],on='account',how='left')
traderEOD_2.to_csv('../ProcessedData/sumstats_EOD.csv')