import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc, font_manager
import seaborn as sns
import datetime as dt
import statsmodels.api as sm

from linearmodels.panel import PanelOLS
import matplotlib.gridspec as gridspec


def settings_plot(ax):
    for label in ax.get_xticklabels():
        label.set_fontproperties(ticks_font)
    for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    return ax

sizeOfFont=18
ticks_font = font_manager.FontProperties(size=sizeOfFont)

quotedata=pd.read_csv('../ProcessedData/mquotes_ZF_mm.csv', index_col=0)
quotedata=quotedata.dropna()
quotedata['priority']=quotedata['priority'].map(int)
quotedata['symbolClass']=quotedata['externalSymbol'].apply(lambda x: x[0:3])

quotedata=quotedata[quotedata['symbolClass'].isin(['TYG','FYG','STF'])]

quotedata['date']=quotedata['date'].apply(lambda x: dt.datetime.strptime(x,"%Y-%m-%d"))
quotedata['priority_levels']=quotedata.groupby(['externalSymbol','datetime','side'])['priority'].transform('max')
quotedata['mm_active']=quotedata.groupby(['externalSymbol','datetime','side'])['priority'].transform('count')
quotedata['datetime']=quotedata['datetime'].apply(lambda x: dt.datetime.strptime(x,"%Y-%m-%d %H:%M:%S"))
quotedata['dside']=np.where(quotedata['side']=='ask',1,-1)
quotedata['Depth_Side_MM']=quotedata.groupby(['externalSymbol','datetime','side'])['Depth_AtQuote_Side_Own'].transform('sum')

quotedata['Inventory_Std']=quotedata.groupby(['externalSymbol',
                                              'date', 'account'])['MarginalQuote_Inventory'].transform(lambda x: (x - x.mean()) / x.std())
quotedata['AggInventory']=quotedata.groupby(['externalSymbol','datetime','side'])['MarginalQuote_Inventory'].transform('sum')

min_obs=quotedata['mm_active'].max()*0.75
regdata=quotedata[quotedata['mm_active']>=min_obs]
regdata['snapshot']=list(zip(regdata['externalSymbol'],regdata['datetime'],regdata['side']))

list_snapshots=regdata['snapshot'].drop_duplicates().to_list()
print(len(list_snapshots))


quote_dfs=[]

for snp in list_snapshots:
    print(snp)
    temp=regdata[regdata.snapshot==snp]


    # get ranks
    temp['priority_r']=temp['priority'].rank()
    temp['Inventory_rank']=temp['MarginalQuote_Inventory'].rank()
    temp['Inventory_std_rank'] = temp['Inventory_Std'].rank()

    temp['rho_corrcoef']=np.corrcoef(temp['MarginalQuote_Inventory'],temp['priority'])[1,0]
    temp['rho_corrcoef_std'] = np.corrcoef(temp['Inventory_Std'], temp['priority'])[1, 0]
    temp['rho_corrcoef_spearman']=np.corrcoef(temp['Inventory_rank'],temp['priority_r'])[1,0]
    temp['rho_corrcoef_spearman_std'] = np.corrcoef(temp['Inventory_std_rank'], temp['priority_r'])[1, 0]

    quote_dfs.append(temp)

regdata_rho=quote_dfs[0].append(quote_dfs[1:],ignore_index=True)
regdata_ss=regdata_rho.drop_duplicates(subset='snapshot')


regdata_ss.to_csv('../ProcessedData/depth_snapshots.csv')
regdata_ss=regdata_ss.set_index(['externalSymbol','date'])
regdata_ss['rho_dside']=regdata_ss['rho_corrcoef_spearman']*regdata_ss['dside']

model=PanelOLS.from_formula('Depth_Side_MM~1+rho_dside+'
                           'priority_levels+OrderImbalance+QSpread_bps+'
                           'EntityEffects+TimeEffects',
                          data=regdata_ss).fit(cov_type='clustered',clustered_entity=False,clustered_time=False)


reg=PanelOLS.from_formula('Depth_Side_MM~1+'
                           'priority_levels+OrderImbalance+QSpread_bps+'
                           'EntityEffects+TimeEffects',
                          data=regdata_ss).fit(cov_type='clustered',clustered_entity=False,clustered_time=False)
regdata_ss['depth_resid']=reg.resids


sizefigs_L=(16,16)
gs = gridspec.GridSpec(2, 2)

# Figure Quantity

fig=plt.figure(facecolor='white',figsize=sizefigs_L)

ax=fig.add_subplot(gs[0, :])
ax=settings_plot(ax)

sns.histplot(x='rho_corrcoef_spearman',data=regdata_ss,stat='probability',element='step',fill=True,hue='side',
             shrink=True)
plt.xlabel("Correlation between inventory and queue position",fontsize=18)
plt.ylabel("Probability",fontsize=18)

legend = ax.get_legend()
handles = legend.legendHandles
legend.remove()
ax.legend(handles, ['ask','bid'], loc='best',fontsize=16,frameon=False)

plt.title("Distribution of queue-inventory correlations",fontsize=20)

ax=fig.add_subplot(gs[1, 0])
ax=settings_plot(ax)

sns.regplot(x='rho_dside',y='Depth_Side_MM',data=regdata_ss,x_bins=[-0.6,-0.4,-0.2,0,0.2,0.4,0.6],
            x_ci=95,scatter=True,ci=95,n_boot=100)
plt.xlabel("Correlation between inventory and queue position",fontsize=18)
plt.ylabel("Depth at best bid/ask (contracts)",fontsize=18)
plt.title("No controls",fontsize=20)

ax=fig.add_subplot(gs[1, 1])
ax=settings_plot(ax)

sns.regplot(x='rho_dside',y='depth_resid',data=regdata_ss,x_bins=[-0.6,-0.4,-0.2,0,0.2,0.4,0.6],
            x_ci=95,scatter=True,ci=95,n_boot=100)
plt.xlabel("Correlation between inventory and queue position",fontsize=18)
plt.ylabel("Depth at best bid/ask (contracts)",fontsize=18)
plt.title("Controls: queue size, spread, order imbalance, \n symbol and date FE",fontsize=20)

plt.tight_layout(pad=5.0)

plt.savefig('../Output/depth_correlation.png',bbox_inches='tight')

plt.clf()
sizefigs_L=(14,8)
gs = gridspec.GridSpec(1, 1)

# Figure Quantity

fig=plt.figure(facecolor='white',figsize=sizefigs_L)
ax=fig.add_subplot(gs[0, 0])
ax=settings_plot(ax)

sns.histplot(x='rho_corrcoef_spearman',data=regdata_ss,stat='probability',element='step',fill=True,hue='side',
             shrink=True)
plt.xlabel("Correlation between inventory and queue position",fontsize=18)
plt.ylabel("Probability",fontsize=18)

legend = ax.get_legend()
handles = legend.legendHandles
legend.remove()
ax.legend(handles, ['ask','bid'], loc='best',fontsize=16,frameon=False)

plt.title("Distribution of queue-inventory correlations",fontsize=20)
plt.savefig('../Output/rho_distribution.png',bbox_inches='tight')