import subprocess

program_list=["generate_list_traders.py",
              "account_dailysummary.py",
              "BBOpresence.py",
              "mm_hft_label.py",
              "inventory_panel.py",
              "mean_reversion_inventory.py",
              "mean_reversion_graph.py",
              "risksharing_correlations.py",
              "risksharing_inefficiency.py",
              "risksharing_graphs.py"
 ]

for program in program_list:
    print("Starting: ", program)
    subprocess.call(['python',program])
    print("Finished! ", program)
    print("---------------")