#!/usr/bin/env bash

#SBATCH --account rabl
#SBATCH --output slurm-stork-db-2019.sh.out
#SBATCH --error slurm-error-db-2019.sh.out
#SBATCH --job-name=stork-coverage-2019-db
#SBATCH --mail-type=ALL
#SBATCH --mail-user=ilin.tolovski@hpi.de
#SBATCH --mem=72G
#SBATCH --partition=magic
#SBATCH --nodelist=cx13
#SBATCH --time=72:00:00

export PYTHONPATH=${PYTHONPATH}:/usr/bin/python3
cd /hpi/fs00/share/fg-rabl/ilin.tolovski/projects/stork/

srun bash scripts/dpfs-sqlite/run-stork-2019.sh stork-zip-flag 2019





