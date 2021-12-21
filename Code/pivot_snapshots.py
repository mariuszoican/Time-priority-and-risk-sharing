import pandas as pd

quotedata=pd.read_csv('../ProcessedData/mquotes_mm.csv', index_col=0)
print("Read")

# rank orders across MMs
quotedata['priority_MM']=quotedata.groupby(['externalSymbol','datetime','side'])['priority'].rank(method='max')
quotedata['no_MM_quotes']=quotedata.groupby(['externalSymbol','datetime','side'])['priority_MM'].transform('max')
quotedata['Depth_MM']=quotedata.groupby(['externalSymbol','datetime','side'])['quantity'].transform('sum')
quotedata['MarginalQuote_Inventory_Std']=quotedata.groupby(['externalSymbol',
                                              'account'])['MarginalQuote_Inventory'].transform(lambda x: (x - x.mean()) / x.std())

print("Processing done!")
# pivot table to get inventories
pivot_quote=quotedata.pivot(index=['externalSymbol','datetime','side'],columns='priority_MM',
                            values='MarginalQuote_Inventory_Std')
pivot_quote=pivot_quote.reset_index()
print("Pivoting done")

# add controls from quotedata
pivot_quote=pivot_quote.merge(quotedata[['externalSymbol','datetime','side','Depth_MM','no_MM_quotes','QSpread_bps',
                                         'OrderImbalance','OrderImbalance_pct','Depth_Total_Side','date']],
                              on=['externalSymbol','datetime','side'],how='left')
pivot_quote=pivot_quote.drop_duplicates().reset_index(drop=True)
print("Merging controls done!")

pivot_quote.to_csv('../ProcessedData/pivot_quotes_inventories.csv')