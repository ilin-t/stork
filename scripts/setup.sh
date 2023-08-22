# Install
python3 -m venv venv
source venv/bin/activate

# Install the requirements for Stork
python3 -m pip install -r requirements.txt

# Download Python repositories from Github. Downloads all repositories from 2018 onwards.
#python3 src/log_modules/get_repos.py
#python3 src/log_modules/parallel_download.py


#python3 src/log_modules/parse_repos.py --threads=12 --repos=/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/repositories-test --outputs=/mnt/fs00/rabl/ilin.tolovski/stork-zip-2days/outputs/repo_stats

DATE=$(date +%d-%m-%Y-%H-%M)
REPOSITORY=$1
ROOT="/mnt/fs00/rabl/ilin.tolovski"
mkdir $ROOT/results/$DATE-$REPOSITORY
mkdir $ROOT/results/$DATE-$REPOSITORY/packages


python3 src/log_modules/parse_repos.py --threads=12 --repositories=$ROOT/$REPOSITORY/repositories-test/ --packages=$ROOT/results/$DATE-$REPOSITORY/packages/ --outputs=$ROOT/results/$DATE-$REPOSITORY/
python3 src/log_modules/parse_requirements.py --threads=12 --packages=$ROOT/$REPOSITORY/packages/ --outputs=$ROOT/results/$DATE-$REPOSITORY/ --repositories=$ROOT/$REPOSITORY/repositories-test/
python3 src/log_modules/plot_libraries.py --outputs=$ROOT/results/$DATE-$REPOSITORY/

