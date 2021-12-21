#!/bin/bash
#SBATCH -J fill_zero_quotes
#SBATCH --array=0-241                    # how many tasks in the array
#SBATCH -c 1                             # one CPU core per task
#SBATCH -t 0-4:00:00
#SBATCH -o marginalquote_fill-%a.out
#SBATCH --mail-type=ALL
#SBATCH --mail-user=marius.zoican@rotman.utoronto.ca
#SBATCH -p standard
#SBATCH --mem=8000

# Load software
# module load anaconda/3.5.3
# source activate ldaenv

# Run python script with a command line argument
srun --unbuffered fill_zero_quant_SLURM.py $SLURM_ARRAY_TASK_ID
