import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rc, font_manager
import seaborn as sns
import datetime as dt
import matplotlib.gridspec as gridspec
import matplotlib.dates as mdates



def settings_plot(ax):
    for label in ax.get_xticklabels():
        label.set_fontproperties(ticks_font)
    for label in ax.get_yticklabels():
        label.set_fontproperties(ticks_font)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    return ax

def product_class(x):
    if x=='SXF':
        return "Equity index"
    else:
        return "Bonds"

sizeOfFont=18
ticks_font = font_manager.FontProperties(size=sizeOfFont)

avgcorrdf=pd.read_csv('../ProcessedData/Inventories/InvCorrelations.csv',index_col=0)
avgcorrdf=avgcorrdf[avgcorrdf.Frequency.isin(['30s','30T','2H'])]

data_inefficiency=pd.read_csv('../ProcessedData/Inventories/InvInefficiency_30s.csv',index_col=0)



gs = gridspec.GridSpec(1, 2)

fig=plt.figure(figsize=(14,8),facecolor='white')


ax=fig.add_subplot(gs[0, 1])
ax=settings_plot(ax)

dataineff_stack=data_inefficiency.set_index(['Product','Date']).stack().reset_index()
dataineff_stack=dataineff_stack.rename(columns={0:'Inefficiency','level_2':'Measure'})
dataineff_stack['ProductClass']=dataineff_stack['Product'].apply(lambda x: product_class(x))
dataineff_stack=dataineff_stack[(dataineff_stack['Measure']!='InefficiencyWeighted')]

sns.barplot(data=dataineff_stack,x='Measure',y='Inefficiency',hue='ProductClass',palette='Blues')
plt.axhline(y=1,c='k',ls='--')
# plt.legend(labels=['30 seconds','2 hours'],
#            fontsize=18, frameon=False,loc='best')
# plt.legend(
#            fontsize=18, frameon=False,loc='best')
# ax.set_xticklabels(['Equally \n weighted','Same \n exchange \n member','Risk-tolerance \n weighted '])
ax.set_xticklabels(['Equally \n weighted','Risk-tolerance \n weighted'])
#plt.xlabel(r'Risk-sharing inefficiency measures',fontsize=18)
#plt.xlabel(r'$\alpha$')
plt.xlabel("")
h, l = ax.get_legend_handles_labels()
ax.legend(h, l, frameon=False,fontsize=18)
plt.ylabel('Inefficiency measure',fontsize=18)
plt.title("Panel (c): Risk-sharing inefficiency",fontsize=18)
plt.tight_layout(pad=5.0)

ax=fig.add_subplot(gs[0, 0])
ax=settings_plot(ax)
sns.kdeplot(data=avgcorrdf,x='AvgPairwiseCorr',hue='Frequency',legend=True,common_norm=True)
plt.legend(labels=['2 hours','30 minutes','30 seconds'],
           fontsize=18, frameon=False,loc='best')
# plt.legend(
#            fontsize=18, frameon=False,loc='best')
plt.xlabel('Average pair-wise inventory correlation',fontsize=18)
plt.ylabel('Probability density',fontsize=18)
plt.title("Panel (b): Inventory correlation",fontsize=18)


plt.tight_layout(pad=5.0)

#plt.show()
plt.savefig("../Output/mm_risksharing.png",bbox_inches='tight')
