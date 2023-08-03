#!/usr/bin/env bash

#SBATCH --account rabl
#SBATCH --output slurm.sh.out
#SBATCH --error slurm.sh.out
#SBATCH --job-name=node-test
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ilin.tolovski@hpi.de
#SBATCH --mem=16G
#SBATCH --cpus-per-task=10
#SBATCH --partition=magic
#SBATCH --constraint=CPU_PROD:XEON
#SBATCH --time=1:00:00

#export PYTHONPATH=${PYTHONPATH}:/usr/bin/python3
cd /hpi/fs00/share/fg-rabl/ilin.tolovski/projects/stork/
srun bash setup_node.sh