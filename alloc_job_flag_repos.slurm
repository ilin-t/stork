#!/usr/bin/env bash

#SBATCH --account rabl
#SBATCH --output slurm.sh.out
#SBATCH --error slurm.sh.out
#SBATCH --job-name=stork-flag-repositories
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ilin.tolovski@hpi.de
#SBATCH --mem=64G
#SBATCH --partition=magic
#SBATCH --nodelist=cx15
#SBATCH --constraint=CPU_PROD:XEON
#SBATCH --time=72:00:00

export PYTHONPATH=${PYTHONPATH}:/usr/bin/python3
cd /hpi/fs00/share/fg-rabl/ilin.tolovski/projects/stork/

srun bash scripts/flag_repos.sh stork-zip-flag 2018
srun bash scripts/flag_repos.sh stork-zip-flag 2019
srun bash scripts/flag_repos.sh stork-zip-flag 2020
srun bash scripts/flag_repos.sh stork-zip-flag 2021
srun bash scripts/flag_repos.sh stork-zip-flag 2022
srun bash scripts/flag_repos.sh stork-zip-flag 2023

