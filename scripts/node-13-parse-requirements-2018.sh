## Install
#apt install python3.8-venv
#python3 -m venv venv
#source venv/bin/activate

export PIP_CACHE_DIR=/scratch/ilin.tolovski/
export PYTHONPATH=${PYTHONPATH}:/usr/bin/python3
export PYTHONPATH=${PYTHONPATH}:/scratch/ilin.tolovski/python-libs/

# Install the requirements for Stork
python3 -m pip install --target=/scratch/ilin.tolovski/python-libs/ -r requirements.txt

#DATE=$(date +%d-%m-%Y-%H-%M)
#REPOSITORY=$1
#DATEREPOSITORY=$2

DATE=$(date +%d-%m-%Y-%H-%M)
REPOSITORY=$1
ROOT="/scratch/ilin.tolovski"

ROOT="/scratch/ilin.tolovski"

#mkdir $ROOT/results/$DATE-$REPOSITORY
#mkdir $ROOT/results/$DATE-$REPOSITORY/packages


#python3 src/log_modules/parse_repos.py --threads=36 --repositories=$ROOT/$REPOSITORY/repositories/ --packages=$ROOT/results/$DATE-$REPOSITORY/packages/ --outputs=$ROOT/results/$DATE-$REPOSITORY/
python3 src/log_modules/parse_requirements.py --threads=36 --packages=$ROOT/results/$DATE-$REPOSITORY/packages/ --outputs=$ROOT/results/$DATE-$REPOSITORY/ --repositories=$ROOT/$REPOSITORY/repositories/year-2018/
python3 src/log_modules/plot_libraries.py --outputs=$ROOT/results/$DATEREPOSITORY/
