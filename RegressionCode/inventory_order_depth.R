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
data <- read.csv("../ProcessedData/pivot_quotes_inventories.csv",
                 header=TRUE, sep=",")

m_ask_1<-felm(Depth_MM ~ X1.0 + X2.0 + X3.0
    | externalSymbol + date| 0 |
    externalSymbol + date + datetime, data=subset(data,no_MM_quotes>=2 & side=='ask'), exactDOF = TRUE)
m_ask_2<-felm(Depth_MM ~ X1.0 + X2.0 + X3.0 + QSpread_bps
    | externalSymbol + date| 0 |
    externalSymbol + date + datetime, data=subset(data,no_MM_quotes>=2 & side=='ask'), exactDOF = TRUE)
m_ask_3<-felm(Depth_MM ~ X1.0 + X2.0 + X3.0 + QSpread_bps + OrderImbalance
    | externalSymbol + date| 0 |
    externalSymbol + date + datetime, data=subset(data,no_MM_quotes>=2 & side=='ask'), exactDOF = TRUE)
m_bid_1<-felm(Depth_MM ~ X1.0 + X2.0 + X3.0
    | externalSymbol + date| 0 |
    externalSymbol + date + datetime, data=subset(data,no_MM_quotes>=2 & side=='bid'), exactDOF = TRUE)
m_bid_2<-felm(Depth_MM ~ X1.0 + X2.0 + X3.0 + QSpread_bps
    | externalSymbol + date| 0 |
    externalSymbol + date + datetime, data=subset(data,no_MM_quotes>=2 & side=='bid'), exactDOF = TRUE)
m_bid_3<-felm(Depth_MM ~ X1.0 + X2.0 + X3.0 + QSpread_bps + OrderImbalance
    | externalSymbol + date| 0 |
    externalSymbol + date + datetime, data=subset(data,no_MM_quotes>=2 & side=='bid'), exactDOF = TRUE)

# generate regression table for H3
stargazer(m_ask_1,m_ask_2,m_ask_3, m_bid_1, m_bid_2, m_bid_3,
          title = "Time priority and marginal impact of inventory on depth ",
          dep.var.labels = 'Market-maker quoted depth',
          column.labels = c("Ask side","Bid side"),
          column.separate = c(3,3),
          covariate.labels = c("Inventory: Priority \\#1",
                               "Inventory: Priority \\#2",
                               "Inventory: Priority \\#3",
                               "quoted spread (bps)",
                               "order imbalance"),
          multicolumn = TRUE, omit.stat = c("LL", "ser", "F"), ci = FALSE, single.row = FALSE, no.space = TRUE,
          add.lines = list(c("Symbol FE", "Yes", "Yes","Yes","Yes","Yes","Yes"),
                           c("Date FE", "Yes", "Yes","Yes","Yes","Yes","Yes")),
          report = "vc*t",
          notes = c("Standard errors clustered at symbol, date, and timestamp level"),
          out='../Output/Tables/Depth_Ordering.tex')

