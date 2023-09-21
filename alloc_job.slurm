#!/usr/bin/env bash

#SBATCH --account rabl
#SBATCH --output slurm.sh.out
#SBATCH --error slurm.sh.out
#SBATCH --job-name=stork-repository-download
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ilin.tolovski@hpi.de
#SBATCH --mem=64G
#SBATCH --partition=magic
#SBATCH --constraint=CPU_PROD:EPYC
#SBATCH --time=72:00:00

#export PYTHONPATH=${PYTHONPATH}:/usr/bin/python3

cd /hpi/fs00/share/fg-rabl/ilin.tolovski/projects/stork/
srun bash scripts/node_download_repos.sh
