import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc, font_manager
import seaborn as sns
import datetime as dt
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

quotedata['date']=quotedata['date'].apply(lambda x: dt.datetime.strptime(x,"%Y-%m-%d"))
quotedata=quotedata.set_index(['externalSymbol','date'])
#quotedata['priority_levels']=quotedata.groupby(['externalSymbol','datetime','side'])['priority'].transform('max')
quotedata['datetime']=quotedata['datetime'].apply(lambda x: dt.datetime.strptime(x,"%Y-%m-%d %H:%M:%S"))
quotedata['Hour']=quotedata['datetime'].apply(lambda x: x.hour)
quotedata['dside']=np.where(quotedata['side']=='ask',1,-1)



# apply controls
reg1=PanelOLS.from_formula('quantity~1+MarginalQuote_Inventory+Depth_Total_Side+'
                           'priority_levels+Depth_BeforeQuote_Side_Own+OrderImbalance+QSpread_bps+'
                           'EntityEffects+TimeEffects',
                          data=quotedata).fit()
quotedata['quantity_resid_1']=reg1.resids

reg2=PanelOLS.from_formula('quantity~1+EntityEffects+TimeEffects',
                          data=quotedata).fit()
quotedata['quantity_resid_2']=reg2.resids

reg3=PanelOLS.from_formula('quantity~1+Depth_Total_Side+EntityEffects+TimeEffects',
                          data=quotedata).fit()
quotedata['quantity_resid_3']=reg3.resids

reg4=PanelOLS.from_formula('quantity~1+MarginalQuote_Inventory+Depth_Total_Side+'
                           'priority_levels+'
                           'EntityEffects+TimeEffects',
                          data=quotedata).fit()
quotedata['quantity_resid_4']=reg4.resids

reg5=PanelOLS.from_formula('quantity~1+MarginalQuote_Inventory+'
                           'EntityEffects+TimeEffects',
                          data=quotedata).fit()
quotedata['quantity_resid_5']=reg5.resids

reg6=PanelOLS.from_formula('quantity~1+priority_levels+'
                           'EntityEffects+TimeEffects',
                          data=quotedata).fit()
quotedata['quantity_resid_6']=reg6.resids



sizefigs_L=(16,8)
gs = gridspec.GridSpec(1, 2)

# Figure Quantity

fig=plt.figure(facecolor='white',figsize=sizefigs_L)
ax=fig.add_subplot(gs[0, 0])
ax=settings_plot(ax)

keep_top=30
sns.barplot(x="priority", y="quantity", hue="side", palette='Paired',
            data=quotedata[quotedata.priority<=keep_top])

plt.xlabel('Queue position at best price', fontsize=20)
plt.ylabel('Marginal quote quantity',fontsize=20)

plt.title('No controls', fontsize=20)
plt.xticks(rotation=60)

plt.legend(loc='best',frameon=False,fontsize=20)


ax=fig.add_subplot(gs[0, 1])
ax=settings_plot(ax)

sns.barplot(x="priority", y="quantity_resid_6", hue="side", palette='Paired',
            data=quotedata[quotedata.priority<=keep_top])

plt.xlabel('Queue position at best price', fontsize=20)
plt.ylabel('Residual marginal quote quantity',fontsize=20)

plt.title('Controls: queue length, symbol and date FE', fontsize=20)
plt.xticks(rotation=45)

plt.legend(loc='best',frameon=False,fontsize=20)


plt.tight_layout(pad=5.0)

plt.savefig('../Output/queue_quantities.png',bbox_inches='tight')

#
#
# ###########################
#
regI=PanelOLS.from_formula('quantity~1+Depth_BeforeQuote_Side+Depth_Total_Side+'
                           'priority_levels+'
                           'EntityEffects+TimeEffects',
                          data=quotedata).fit()
quotedata['quantity_resid_inv']=regI.resids

reg_inv=PanelOLS.from_formula('MarginalQuote_Inventory~1+Depth_BeforeQuote_Side+Depth_Total_Side+'
                           'priority_levels+EntityEffects+TimeEffects',
                          data=quotedata).fit()
quotedata['inv_resid_1']=reg_inv.resids


quotedata['quantile_inventory'] = pd.qcut(quotedata['inv_resid_1'],
                            q=[0, 0.2, 0.4, 0.6, 0.8, 1],
                            labels=False,
                            precision=0)

quotedata=quotedata.reset_index()
size_diff=quotedata.pivot(index=['externalSymbol','datetime',
                                 'account','quantile_inventory'],columns='side',
                          values='quantity_resid_inv').reset_index()
size_diff['qdiff']=size_diff['ask']-size_diff['bid']


# no controls



quotedata['quantile_inventory_nc'] = pd.qcut(quotedata['MarginalQuote_Inventory'],
                            q=[0, 0.2, 0.4, 0.6, 0.8, 1],
                            labels=False,
                            precision=0)

quotedata=quotedata.reset_index()
size_diff_nc=quotedata.pivot(index=['externalSymbol','datetime',
                                 'account','quantile_inventory_nc'],columns='side',
                          values='quantity').reset_index()
size_diff_nc['qdiff']=size_diff_nc['ask']-size_diff_nc['bid']

gs = gridspec.GridSpec(1, 2)
fig=plt.figure(facecolor='white',figsize=sizefigs_L)


ax=fig.add_subplot(gs[0, 0])
ax=settings_plot(ax)
sns.barplot(x="quantile_inventory_nc", y="qdiff",
            data=size_diff_nc,palette='mako')
plt.xlabel('Inventory quantile', fontsize=20)
plt.ylabel('Ask-bid order size (marginal quote)',fontsize=20)
plt.title('No controls', fontsize=20)
ax.set_xticklabels(['Low','2','3','4','High'])


ax=fig.add_subplot(gs[0, 1])
ax=settings_plot(ax)
sns.barplot(x="quantile_inventory", y="qdiff",
            data=size_diff,palette='mako')
plt.xlabel('Inventory quantile', fontsize=20)
plt.ylabel('Ask-bid order size (marginal quote)',fontsize=20)
plt.title('Controls: Queue ahead, queue length, depth, \n entity and date fixed effects', fontsize=20)
ax.set_xticklabels(['Low','2','3','4','High'])

plt.tight_layout(pad=5.0)

plt.savefig('../Output/inventory_concerns.png',bbox_inches='tight')

# size_diff_nc=size_diff_nc.fillna(0)
# size_diff_nc['quote_side']=np.where(((size_diff_nc['ask']==0) & (size_diff_nc['bid']>0)),"bid only",
#                                     np.where(((size_diff_nc['ask']>0) & (size_diff_nc['bid']==0)),
#                                              'ask only','both'))
# counts=size_diff_nc.groupby(['quantile_inventory_nc','quote_side']).count()['externalSymbol']