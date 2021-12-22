library(xtable)
library(plm)
library(dplyr)
library(lmtest)
library(tidyr)
library(lfe)
library(stargazer)
library(broom)
library(purrr)
library(rstudioapi)
# Load data in memory
# -------------------------------
setwd(dirname(getActiveDocumentContext()$path))
data <- read.csv("../ProcessedData/mquotes_ZF_mm.csv",
                 header=TRUE, sep=",")


# dummy for `ask` and `side`
data$dside <- ifelse(data$side == 'ask', 1, -1)
data$dask <- ifelse(data$side == 'ask', 1, 0)

myvars<-c("quantity",'MarginalQuote_Inventory','Depth_Total_Side','QSpread_bps', 'priority')
dataforsum<-data[myvars]

stargazer(dataforsum,flip=TRUE,summary.stat=c("mean","sd","p25","median","p75","n"),
          title='Summary statistics on market-maker quotes',
          covariate.labels = c("Quote size","Inventory","Book depth","Quoted spread (bps)","Queue size"),
          digits = 2, notes='Data from 30-second order book snapshots with active market-makers',
          out='../Output/Tables/sumstats.tex')

mmdata <- read.csv("../ProcessedData/sumstats_EOD.csv",
                 header=TRUE, sep=",")
mmdata$NetPosition=mmdata$NetPosition*100
mmdata$StdInventory=mmdata$StdInventory*100
mmdata$BBO_share=mmdata$BBO_share*100

mmdata_select <- mmdata[c("mmlabel","num_trades",'quantity','NetPosition','StdInventory','BBO_share')]


stargazer(subset(mmdata_select,mmlabel==1)[c("num_trades",'quantity','NetPosition','StdInventory','BBO_share')],
          summary.stat=c("mean","sd","p25","median","p75","n"),
          title='Trading statistics for market maker accounts',
          covariate.labels = c("Trade count",'Volume','Net pos. (\\%)','Inventory variation (\\%)','Time at BBO (\\%)'), flip=TRUE,
          digits = 2,out='../Output/Tables/mmstats.tex')

stargazer(subset(mmdata_select,mmlabel==0)[c("num_trades",'quantity','NetPosition','StdInventory','BBO_share')],
          summary.stat=c("mean","sd","p25","median","p75","n"),
          title='Trading statistics for non-market maker accounts',
          covariate.labels = c("Trade count",'Volume','Net pos. (\\%)','Inventory variation (\\%)','Time at BBO (\\%)'), flip=TRUE,
          digits = 2, out='../Output/Tables/nonmmstats.tex')