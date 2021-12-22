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
data <- read.csv("../ProcessedData/depth_snapshots.csv",
                 header=TRUE, sep=",")

data$Depth_Others=data$Depth_Total_Side-data$Depth_Side_MM


data$dask <- ifelse(data$side == 'ask', 1, 0)
data$dbid <- ifelse(data$side == 'bid', 1, 0)


mmth=round(0.75*n_distinct(data$account)) # cut-off for MM active in the snapshot

data$rho_dside=data$rho_corrcoef_spearman*data$dside
data$rho_ask=data$rho_corrcoef_spearman*data$dask
data$rho_bid=data$rho_corrcoef_spearman*data$dbid
data$AggInventory=data$AggInventory/100

m1<-felm(Depth_Side_MM ~ rho_dside
    | externalSymbol + date | 0 |
    externalSymbol + date + datetime, data=subset(data,mm_active>=mmth), exactDOF = TRUE)
m2<-felm(Depth_Side_MM ~ rho_dside + priority_levels
    | externalSymbol + date  | 0 |
    externalSymbol + date + datetime, data=subset(data,mm_active>=mmth), exactDOF = TRUE)
m3<-felm(Depth_Side_MM ~ rho_dside + priority_levels + OrderImbalance
    | externalSymbol + date | 0 | externalSymbol + date+ datetime, data=subset(data,mm_active>=mmth), exactDOF = TRUE)
m4<-felm(Depth_Side_MM ~ rho_dside + priority_levels + OrderImbalance + QSpread_bps + AggInventory
    | externalSymbol + date | 0 | externalSymbol + date+ datetime, data=subset(data,mm_active>=mmth), exactDOF = TRUE)
m5<-felm(Depth_Side_MM ~ rho_ask + rho_bid + priority_levels + OrderImbalance + QSpread_bps + AggInventory
    | externalSymbol + date | 0 | externalSymbol + date + datetime, data=subset(data,mm_active>=mmth), exactDOF = TRUE)

# generate regression table for H3
stargazer(m1,m2,m3,m4,m5,
          title = "Time priority seqeuence and market depth",
          dep.var.labels = "Market-maker quoted depth (contracts) on book side",
          covariate.labels = c("$\\hat{\\rho}(\\text{queue, inventory}) \\times d_{\\text{side}}$",
                               "$\\hat{\\rho}(\\text{queue, inventory}) \\times d_{\\text{ask}}$",
                               "$\\hat{\\rho}(\\text{queue, inventory}) \\times d_{\\text{bid}}$",
                               "queue size",
                               "order imbalance",
                               "quoted spread (bps)",
                               "aggregate inventory (x 100)"),
          multicolumn = TRUE, omit.stat = c("LL", "ser", "F"), ci = FALSE, single.row = FALSE, no.space = TRUE,
          add.lines = list(c("Symbol FE", "Yes", "Yes","Yes","Yes","Yes"),
                           c("Date FE", "Yes", "Yes","Yes","Yes","Yes")),
          report = "vc*t",
          notes = c("Standard errors clustered at symbol, date, and timestamp level"),
          out='../Output/Tables/Depth_main.tex')

