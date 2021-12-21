# Workflow for TMX project


## 1. Market-maker labels and risk-sharing results.

* All the Python codes below can be run (in order) from batch file `Code\0_batch_inventory.py`

### 1.1 Generate market-maker labels

1. Run `generate_list_traders.py` to get a correspondence between each AP, trader, and account. 
   Saves resulting panel at `ProcessedData\ap_account_trader.csv`.
2. Run `account_dailysummary.py` to obtain a trader-stock-day panel with 
   Kirilenko, Kyle, Samadi and Tuzun (2017, JF) variables -- net position, 
   number of trades/volume traded, standard deviation of inventory. Saves a panel at 
   `ProcessedData\account_EODdata.csv`.
3. Run `BBOpresence.py` to obtain a panel with each traders' time share at best bid and ask (or both ask and bid).
   Saves the panel at `ProcessedData\BBO_presence_MM.csv`.
4. Run `mm_hft_label.py` to assign labels for market makers (using KKST-based methodology and presence at the BBO) 
   as well as HFT labels based on TMX information. Saves file with labels at  `ProcessedData\mm_hft_labels.csv`.
   
### 1.2 Study market-maker inventories

5. Run `inventory_panel.py` to get inventory panels for each market maker at various frequencies (e.g., 30 second, 
   1 minute, 30 minutes, 1 hour). Panels are saved in `ProcessedData/Inventories/inventory_panel_FREQUENCY.csv`.
6. Run `mean_reversion_inventory.py` to estimate inventory half-life (in minutes) for each market-maker using an AR(1) 
   process. Half-life panel saved as `ProcessedData/inventory_halflife.csv`.
7. Run `mean_reversion_graph.py` to generate a two-panel figure of BBO presence and inventory half-lives across 
   market makers. Figure is saved as `Output/BBOshares_Halflife_MM.png`.

### 1.3 Study risk-sharing by market-makers
8. Run `risksharing_correlations.py` to obtain the average pairwise correlation between MM inventory 
   based on 30-second inventory panel. Output saved as `ProcessedData/Inventories/InvCorrelations.csv`.
9. Run  `risksharing_inefficiency.py` to obtain estimates of MM risk-sharing inefficiency 
   (based on a quadratic inventory model). Inefficiency panel 
   saved as `ProcessedData/Inventories/InvInefficiency.csv`.
10. Run  `risksharing_graphs.py` to plot the average pairwise correlation and risk-sharing inefficiency. 
    Output saved as `Output/mm_risksharing.png`  
    

## 2. Generate the snapshot-trader marginal quote panel and snapshot depth panel.

* All the codes below can be run (in order) from batch file `Code\1_batch_getmainpanel.py`.

11. Run `build_panel.py` on the raw data to generate a folder with marginal quote panels for all traders 
   (`ProcessedData\MarginalQuotePanels\`). The code uses auxiliary functions from `functions_tmxdata.py`.
12. Run `fill_zero_quant.py` to take each marginal quote panel and:
    1. Assign quantities of zero on the no-quote side for traders active on one side of the book. Such zero-quantities 
       enter the book "as if" they are at the lowest priority.
    2. Merge the trader IDs with the market-maker or HFT label.
    3. Resample the panels every 30s (to avoid double-counting quotes)   
    4. Save the resulting panels in `ProcessedData\MarginalQuotePanels_ZF\`
* Running `fill_zero_quant.py` takes a lot of time. The folder `Code\ForSlurm\` includes a 
  slightly modified version and a SLURM script to run the code in parallel on the Rotman Research Node. 
  Panels need to be manually transferred to the repo, using e.g., WinSCP.
13. Run `select_mm_data.py` to only select the market-maker quotes and save to 
   file `ProcessedData\mquotes_ZF_mm.csv`. This is the main panel for regressions. 
14. Run `depth_processing.py` to build a panel with 30-second order book snapshots and 
   correlation coefficients between inventory and queue position. 
   Save file as `ProcessedData\depth_snapshots.csv`. The file also generates two representative figures: 
    `Output/depth_correlation.png` (impact of inventory-queue correlation on depth) 
    and `Output/rho_distribution.png` (distribution of inventory-queue correlations). 
15. Use `sumstats.py` to generate the figures for adverse selection (`Output/queue_quantities.png`) 
    and inventory (`Output/inventory_concerns.png`).
16. Run `mm_quotes_preliminaries.py` to generate `mquotes_mm.csv` which is the same as `mquotes_ZF_mm.py`
    but without zero quantities filled.
17. Run `pivot_snapshots.py` to obtain a panel with marginal inventories for MMs as a function of 
    their relative priority level in the book. Panel is saved at `ProcessedData/pivot_quotes_inventories.csv`.    
   

## 3. Econometric analysis
17. Use `RegressionCode/summary_stats.R` to produce summary stats tables for market-makers 
    (`Output/Tables/mmstats.tex`), non-market makers (`Output/Tables/nonmmstats.tex`) and for 
    all quote snapshots (`Output/Tables/sumstats.tex`) 
18. Use `RegressionCode/regression_tests.R` for econometric analysis on `mquotes_ZF_mm.csv`. 
   Output is a table with structural regression estimates: `Output/Tables/ASICtable_main.tex`
19. Use `RegressionCode/depth_tests.R` for econometric analysis on `depth_snapshots.csv`.
   Output is a table with estimates on depth effects: `Output/Tables/Depth_main.tex`.
20. Use `RegressionCode/inventory_order_depth.R` for econometric analysis on `pivot_quotes_inventories.csv`.
   Output is a table with the marginal impact of inventory as a function of queue position: 
   `Output/Tables/Depth_Ordering.tex`.

## 4. Miscellenea

21. Use `theory_figure.py` to generate theory-supporting figures `Output/theory_example_params.png` and 
    `Output/marginal_impact_queue.png`.
22. Use  `get_average_trade.py` to estimate the average trade size in the data.


