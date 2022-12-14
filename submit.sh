#!/bin/bash
# Specify a partition 
#SBATCH --partition=bluemoon
# Request nodes 
#SBATCH --nodes=1
# Request some processor cores 
#SBATCH --ntasks=4
# Request GPUs 
#SBATCH --gres=gpu:0
# Request memory 
#SBATCH --mem=25G
# Maximum runtime of 2 hours
#SBATCH --time=02:00:00

python3 run_model.py $1 $2 $3 $4
