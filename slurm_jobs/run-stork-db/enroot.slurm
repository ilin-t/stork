#!/bin/bash
#SBATCH -A rabl
#SBATCH --job-name=postgres
#SBATCH --mail-user=youremail@hpi.de
#SBATCH --mail-type=ALL
#SBATCH --time=24:00:00
#SBATCH --mem=10G
#SBATCH --cpus-per-task=10
#SBATCH --partition=magic
#SBATCH --nodelist=cx02
#SBATCH -n 1
#SBATCH --tmp=5G

#Create a partition in the local directory
mkdir -p /scratch/ilin.tolovski/pg_data

#Copy the contents of folders you need in local storage
cp -R /hpi/fs00/share/fg-rabl/ilin.tolovski/pg_data /scratch/ilin.tolovski/pg_data

#Change permissions accordingly
chmod 700 /scratch/ilin.tolovski/pg_data

#To start the container first you need to have it created with enroot import, then enroot create
enroot start -m /scratch/ilin.tolovski/pg_data:/var/lib/postgresql/16/main \
-m /hpi/fs00/share/fg-rabl/ilin.tolovski/projects/stork:/app/stork \
--rw ilintolovski+postgres-test-db bash /app/stork/scripts/test.sh
