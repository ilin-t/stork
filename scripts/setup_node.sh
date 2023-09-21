## Install
apt install python3.8-venv
python3 -m venv venv
source venv/bin/activate

# Install the requirements for Stork
python3 -m pip install -r requirements.txt

#python3 src/log_modules/parse_repos.py --threads=12 --repos=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-2days/repositories-test/ --packages=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-2days/packages/ --outputs=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-2days/outputs/
#python3 src/log_modules/parse_requirements.py --threads=12 --packages=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-2days/packages/
#python3 src/log_modules/plot_libraries.py --path=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-2days/packages/

DATE=$(date +%d-%m-%Y-%H-%M)
REPOSITORY=$1
ROOT="/hpi/fs00/share/fg-rabl/ilin.tolovski"

python3 src/log_modules/parallel_download.py

mkdir $ROOT/results/$DATE-$REPOSITORY
mkdir $ROOT/results/$DATE-$REPOSITORY/packages


python3 src/log_modules/parse_repos.py --threads=12 --repositories=$ROOT/$REPOSITORY/repositories-test/ --packages=$ROOT/results/$DATE-$REPOSITORY/packages/ --outputs=$ROOT/results/$DATE-$REPOSITORY/
python3 src/log_modules/parse_requirements.py --threads=12 --packages=$ROOT/$REPOSITORY/packages/ --outputs=$ROOT/results/$DATE-$REPOSITORY/ --repositories=$ROOT/$REPOSITORY/repositories-test/
python3 src/log_modules/plot_libraries.py --outputs=$ROOT/results/$DATE-$REPOSITORY/



#python3 ../src/log_modules/parse_repos.py --threads=128 --repos=$ROOT/$REPOSITORY/repositories-test/ --packages=$ROOT/$REPOSITORY/packages/ --outputs=$ROOT/results/$DATE-$REPOSITORY
#python3 ../src/log_modules/parse_requirements.py --threads=128 -packages=$ROOT/$REPOSITORY/packages/
#python3 ../src/log_modules/plot_libraries.py --path=$ROOT/results/$DATE-$REPOSITORY

#python3 src/log_modules/parse_repos.py --threads=128 --repos=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-download/repositories-test/ --packages=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-download/packages/ --outputs=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-download/outputs/
#python3 src/log_modules/parse_requirements.py --threads=128 --packages=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-download/packages/
#python3 src/log_modules/plot_libraries.py --path=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-download/packages/
