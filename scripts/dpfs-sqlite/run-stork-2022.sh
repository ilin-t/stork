## Install
apt install python3.8-venv
python3 -m venv venv
source venv/bin/activate

# Install the requirements for Stork
python3 -m pip install -r requirements.txt

DATE=$(date +%d-%m-%Y-%H-%M)
REPOSITORY=$1
YEAR=$2
ROOT="/hpi/fs00/share/fg-rabl/ilin.tolovski"

python3 benchmarks/run_mt_db_sqlite.py --threads=36 --repositories=$ROOT/results/21-11-2023-13-40-stork-zip-flag-year-2022/repositories/library_reads/aggregated_results.txt --outputs=$ROOT/results/$DATE-$REPOSITORY-year-$YEAR/ --pipelines=$ROOT/results/21-11-2023-13-40-stork-zip-flag-year-2022/pipelines/library_reads/aggregated_results.txt
