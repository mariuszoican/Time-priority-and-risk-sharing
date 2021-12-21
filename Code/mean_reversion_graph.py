import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import rc, font_manager
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

data_MR=pd.read_csv('../ProcessedData/inventory_halflife.csv',index_col=0)
mm_share=pd.read_csv('../ProcessedData/BBO_presence_MM.csv',index_col=0)

hls=data_MR[(data_MR.inv_halflife_min>0) &
(data_MR.inv_halflife_min<960)].groupby('account').inv_halflife_min.mean().reset_index()

mm_share=mm_share.merge(hls,on='account',how='left')

gs = gridspec.GridSpec(1, 2)

mm_share['single_share']=mm_share['BBO_share']-mm_share['both_share']

fig=plt.figure(figsize=(18,10),facecolor='white')

ax=fig.add_subplot(gs[0, 0])
ax=settings_plot(ax)
plt.scatter(100*mm_share[mm_share.account.isin(hls['account'].to_list())]['single_share'],
            100*mm_share[mm_share.account.isin(hls['account'].to_list())]['both_share'],s=200, alpha=1)
# plt.ylim(0,80)
# plt.xlim(0,90)

fudge_x=0.6
coordinates = [('MM 1',33.17-14.12+fudge_x,14.12), ('MM 2',49.60-17.2+fudge_x,17.2), ('MM 3',23.24-3.23+fudge_x,3.23),
               ('MM 4',29.91-9.29+fudge_x,9.29), ('MM 12',28.78-6.19+fudge_x,6.19), ('MM 5',74.09-42.02+fudge_x,42.02),
               ('MM 6',69.31-37.85+fudge_x,37.85), ('MM 7',49.55-25.30+fudge_x,25.30), ('MM 8',51.57-22.49+fudge_x,22.49),
               ('MM 9',80.94-45.80+fudge_x,45.80), ('MM 10',54.07-32.38+fudge_x,32.38), ('MM 11',81.11-48.92+fudge_x,48.92)]
for x in coordinates: plt.annotate(x[0], (x[1], x[2]),fontsize=16)

plt.xlabel('Time with one-sided quotes at best price (%)', fontsize=18)
plt.ylabel('Time with two-sided quotes at best price (%)', fontsize=18)



ax=fig.add_subplot(gs[0, 1])
ax=settings_plot(ax)

sns.boxplot(y='account',x='inv_halflife_min',data=data_MR[(data_MR.inv_halflife_min>0) &
(data_MR.inv_halflife_min<960)],fliersize=0)

plt.xlabel('Inventory half-life (minutes)', fontsize=18)
plt.ylabel('Market-maker', fontsize=18)

ax.set_yticklabels(['MM %i'%x for x in range(1,9)])

#plt.xlim(0,100)

plt.tight_layout(pad=5.0)

#plt.show()
plt.savefig('../Output/BBOshares_HalfLife_MM.png',bbox_inches='tight')