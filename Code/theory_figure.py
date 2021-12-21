import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rc, font_manager
import seaborn as sns
import numpy.random as rnd
import datetime as dt
#from linearmodels.panel import PanelOLS
import matplotlib.gridspec as gridspec
from statsmodels.regression.linear_model import OLS

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


# set model parameters
s, phi, lmb, gamma = 0.01, 1, 1/900, 1/900

params=[s,phi,lmb,gamma]

J=4 # number of market makers
inventories=[0,0,0,4]

def depth(inventories,prm):

    def quant(j, inv, prm):
        s, phi, lmb, gamma = prm
        term1 = (s - lmb * phi) * (gamma ** j) / (gamma + lmb) ** (j + 1)
        frac = gamma / (gamma + lmb)
        ahead = np.array(inv[:j + 1])
        decay = np.array([frac ** (len(ahead) - k) for k in range(len(ahead))])
        ahead = ahead * decay * lmb / gamma
        return term1 - sum(ahead) + inv[j]

    return np.array([quant(k,inventories,prm) for k in range(len(inventories))]).sum()

def depth_indiv(inventories,prm):

    def quant(j, inv, prm):
        s, phi, lmb, gamma = prm
        term1 = (s - lmb * phi) * (gamma ** j) / (gamma + lmb) ** (j + 1)
        frac = gamma / (gamma + lmb)
        ahead = np.array(inv[:j + 1])
        decay = np.array([frac ** (len(ahead) - k) for k in range(len(ahead))])
        ahead = ahead * decay * lmb / gamma
        return term1 - sum(ahead) + inv[j]

    return np.array([quant(k,inventories,prm) for k in range(len(inventories))])


def depth_sims(prm,nosim=1000,J=4):
    temp = np.array(rnd.rand(nosim, J))
    sum_of_rows = temp.sum(axis=1)
    simulated_inventories = J * temp / sum_of_rows[:, np.newaxis]

    sim_corr = np.array([np.corrcoef(k, np.array([x for x in range(J)]))[0, 1]
                         for k in simulated_inventories])

    sim_depth = np.array([depth(k, prm) for k in simulated_inventories])

    sim_depth=(sim_depth-sim_depth.mean())/sim_depth.std()

    return sim_depth, sim_corr


# nosim=10000
# temp=np.array(rnd.rand(nosim,J))
# sum_of_rows=temp.sum(axis=1)
# simulated_inventories=J*temp/sum_of_rows[:,np.newaxis]
#
# sim_depth=np.array([depth(k,params) for k in simulated_inventories])
#
# sim_corr=np.array([np.corrcoef(k,np.array([x for x in range(J)]))[0,1]
#                    for k in simulated_inventories])
#
#
# sizefigs_L=(16,8)
# gs = gridspec.GridSpec(1, 2)
#
# fig=plt.figure(facecolor='white',figsize=sizefigs_L)
# ax=fig.add_subplot(gs[0, 0])
# ax=settings_plot(ax)
# sns.histplot(sim_depth,stat="probability")
# plt.xlabel(r'Cumulative depth at best ask',fontsize=18)
# plt.ylabel('Probability',fontsize=18)
#
# ax=fig.add_subplot(gs[0, 1])
# ax=settings_plot(ax)
# sns.regplot(x=sim_corr,y=sim_depth,x_bins=10)
# plt.ylabel(r'Cumulative depth at best ask',fontsize=18)
# plt.xlabel('Correlation between queue position and inventory',fontsize=18)
# plt.tight_layout(pad=5.0)
# plt.savefig('../Output/theory_correlation.png',bbox_inches='tight')
# #plt.show()
#
# # FIGURE 2
# # --------------
#
# space_length=50
# lmb_space=np.linspace(1/1200,1/300,space_length)
# gamma_space=np.linspace(1/1200,1/300,space_length)
#
# param_vlmb=[[s,phi,li,gamma] for li in lmb_space]
# param_vgamma=[[s,phi,lmb, gi] for gi in lmb_space]
#
# # get standardized depths and correlations
# depths_corrs_l =[depth_sims(pi,nosim=50000) for pi in param_vlmb]
# coeff_l=[OLS(depths_corrs_l[i][0],depths_corrs_l[i][1]).fit().params for i in range(space_length)]
#
#
# # get standardized depths and correlations
# depths_corrs_g =[depth_sims(pi,nosim=50000) for pi in param_vgamma]
# coeff_g=[OLS(depths_corrs_g[i][0],depths_corrs_g[i][1]).fit().params for i in range(space_length)]
#
#
# sizefigs_L=(16,8)
# gs = gridspec.GridSpec(1, 2)
#
# fig=plt.figure(facecolor='white',figsize=sizefigs_L)
# ax=fig.add_subplot(gs[0, 0])
# ax=settings_plot(ax)
# plt.plot(10000*lmb_space,coeff_l)
# plt.xlabel(r'Price impact ($10000\times\lambda$)',fontsize=18)
# plt.ylabel('Slope of regressing best-price depth \n on queue-inventory correlation',fontsize=18)
#
# ax=fig.add_subplot(gs[0, 1])
# ax=settings_plot(ax)
# plt.plot(10000*gamma_space,coeff_g)
# plt.xlabel(r'Inventory penalty ($10000\times\gamma$)',fontsize=18)
# plt.ylabel('Slope of regressing best-price depth \n on queue-inventory correlation',fontsize=18)
# plt.tight_layout(pad=5.0)
# #plt.savefig('../Output/slopes_params.png',bbox_inches='tight')

def importance_inventory(k,gamma,lmb):
    return (gamma/(gamma+lmb))**k

sizefigs_L=(14,8)
gs = gridspec.GridSpec(1, 1)

k_range=np.linspace(1,10,10)

fig=plt.figure(facecolor='white',figsize=sizefigs_L)
ax=fig.add_subplot(gs[0, 0])
ax=settings_plot(ax)
plt.plot(k_range,[importance_inventory(10-ki+1,gamma,lmb) for ki in k_range],
         label=r'$\gamma=\frac{1}{900}$, $\lambda=\frac{1}{900}$')
plt.plot(k_range,[importance_inventory(10-ki+1,2*gamma,lmb) for ki in k_range],
         label=r'$\gamma=\frac{2}{900}$, $\lambda=\frac{1}{900}$',c='r',ls='--')
plt.plot(k_range,[importance_inventory(10-ki+1,gamma,2*lmb) for ki in k_range],
         label=r'$\gamma=\frac{1}{900}$, $\lambda=\frac{2}{900}$',c='g',ls='-.')
plt.legend(loc='best',fontsize=18,frameon=False)
plt.xlabel(r'Queue position',fontsize=18)
plt.ylabel('Impact of unit inventory change on total depth',fontsize=18)
plt.savefig('../Output/marginal_impact_queue.png',bbox_inches='tight')


example=pd.DataFrame(index=['MM1','MM2','MM3'])

list_inventories=[(6,0,0),(2,2,2),(0,0,6),(-2,2,6)]
string_inv=[str(x) for x in list_inventories]
for inv in list_inventories:
    example[str(inv)]=depth_indiv(inv,params)

sizefigs_L=(14,8)
gs = gridspec.GridSpec(1, 1)

fig=plt.figure(facecolor='white',figsize=sizefigs_L)
ax=fig.add_subplot(gs[0, 0])
ax=settings_plot(ax)
plt.bar(string_inv,example.loc['MM1'],label='Market Maker 1')
plt.bar(string_inv, example.loc['MM2'], bottom=example.loc['MM1'], label='Market Maker 2')
plt.bar(string_inv, example.loc['MM3'], bottom=example.loc['MM1']+example.loc['MM2'], label='Market Maker 3')
plt.xlabel('Market maker inventories',fontsize=18)
plt.ylabel('Quote size', fontsize=18)
plt.legend(loc='best',fontsize=18,frameon=False)
plt.savefig('../Output/theory_example_params.png',bbox_inches='tight')


