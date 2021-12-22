library(xtable)
library(plm)
library(dplyr)
library(lmtest)
library(tidyr)
library(lfe)
library(stargazer)
library(broom)
library(standardize)
library(rstudioapi)

# Load data in memory
# -------------------------------
setwd(dirname(getActiveDocumentContext()$path))
data <- read.csv("../ProcessedData/mquotes_ZF_mm.csv",
                 header=TRUE, sep=",")



# dummy for `ask` and `side`
data$dside <- ifelse(data$side == 'ask', 1, -1)
data$dask <- ifelse(data$side == 'ask', 1, 0)

# Queue Length x dside
data$queuelength=data$priority_levels*data$dside


data$MQ_Inventory_std<-scale_by(MarginalQuote_Inventory~externalSymbol+date+account, data)
data$QueueAhead_std<-scale_by(Depth_BeforeQuote_Side~externalSymbol+date+account, data)

# variant -- standardize across data set
data$MQ_Inventory_std_var<-scale(data$MarginalQuote_Inventory)[,1]
data$QueueAhead_std_var<-scale(data$Depth_BeforeQuote_Side)[,1]

data$spread_std<-scale(data$QSpread_bps)[,1]
data$depth_std<-scale(data$QSpread_bps)[,1]
data$oi_side=data$OrderImbalance_pct*data$dside



# Qm = Quantity x Side Dummy
data$qm=data$quantity*data$dside
data$spread_dask=100*data$dask*data$spread_std
data$queue_dside=data$QueueAhead_std*data$dside
data$priority_dside=data$priority*data$dside # alternative for queue_dside
data$depth_dside=data$depth_std*data$dside

# variant -- standardize across data set
data$queue_dside_var=data$QueueAhead_std_var*data$dside
data$snapshot<-paste(data$externalSymbol,data$datetime,data$side)


m1 <-felm(qm ~ dask+spread_dask+queue_dside+MQ_Inventory_std + queuelength + depth_dside + oi_side
    | account + externalSymbol + date | 0 |
    account+externalSymbol+date, data=subset(data), exactDOF = TRUE)
m2 <-felm(qm ~ dask+spread_dask+queue_dside+MQ_Inventory_std + queuelength + depth_dside
    | account + externalSymbol + date | 0 |
    account+externalSymbol+date, data=subset(data), exactDOF = TRUE)
m3 <-felm(qm ~ dask+spread_dask+queue_dside+MQ_Inventory_std + queuelength
    | account + externalSymbol + date | 0 |
    account+externalSymbol+date, data=subset(data), exactDOF = TRUE)
m4<-felm(qm ~ dask+ queue_dside+MQ_Inventory_std + queuelength
    | account + externalSymbol + date | 0 |
    account+externalSymbol+date, data=subset(data), exactDOF = TRUE)
m5 <-felm(qm ~ dask+spread_dask+priority_dside + MQ_Inventory_std + queuelength + depth_dside
    | account + externalSymbol + date | 0 |
    account+externalSymbol+date, data=subset(data), exactDOF = TRUE)
# m6 <-felm(qm ~ queue_dside+MQ_Inventory_std
#     | snapshot | 0 | snapshot, data=subset(data), exactDOF = TRUE)

# generate regression table for H3
stargazer(m1,m2,m3,m4,m5,
          title = "Impact of queue size and trader inventory on marginal quotes (3-way standardized)",
          dep.var.labels = "Marginal quote size",
          report = "vc*t",
          covariate.labels = c("$d_{\\text{ask}}$","quoted spread $\\times d_{\\text{ask}}$ ",
                               "queue ahead $\\times d_{\\text{side}}$ ","order priority $\\times d_{\\text{side}}$ ",
                               "Inventory","queue length",
                               "book depth $\\times d_{\\text{side}}$",
                               "order imbalance $\\times d_{\\text{side}}$"),
          multicolumn = TRUE, omit.stat = c("LL", "ser", "F"), ci = FALSE, single.row = FALSE, no.space = TRUE,
          add.lines = list(c("Symbol FE", "Yes", "Yes","Yes","Yes","Yes"),
                           c("Date FE", "Yes", "Yes","Yes","Yes","Yes"),
                           c("Trader FE", "Yes", "Yes","Yes","Yes","Yes")),
          notes = c("Standard errors clustered at symbol, date, and trader level."),
          out='../Output/Tables/ASICtable_main.tex')