import subprocess

program_list=["build_panel.py",
              "fill_zero_quant.py",
              "select_mm_data.py",
              "mm_quotes_preliminaries.py",
              "depth_processing.py",
              "sumstats.py",
              "pivot_snapshots.py"]

for program in program_list:
    print("Starting: ", program)
    subprocess.call(['python',program])
    print("Finished! ", program)