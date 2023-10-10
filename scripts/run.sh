python3 -m venv venv
source venv/bin/activate

#export PIP_CACHE_DIR=/scratch/ilin.tolovski/
#export PYTHONPATH=${PYTHONPATH}:/usr/bin/python3
#export PYTHONPATH=${PYTHONPATH}:/scratch/ilin.tolovski/python-libs/

# Install the requirements for Stork
#python3 -m pip install --target=/scratch/ilin.tolovski/python-libs/ -r requirements.txt
python3 -m pip install -r requirements.txt

DATE=$(date +%d-%m-%Y-%H-%M)
REPOSITORY=$1
#DATEREPOSITORY=$2
#ROOT="/scratch/ilin.tolovski"
#ROOT="/hpi/fs00/share/fg-rabl/ilin.tolovski/"
ROOT="/home/ilint/HPI/repos/pipelines/"

python3 ../benchmarks/run.py --repositories=$ROOT/$REPOSITORY/repositories-test/ --outputs=$ROOT/results-2days

