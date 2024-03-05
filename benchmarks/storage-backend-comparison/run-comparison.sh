# Set the Python environment
export PYTHONPATH=${PYTHONPATH}:/usr/bin/python3

S3CONFIG=$1

echo $S3CONFIG

ROOT=$PWD

cd pipelines
#Generating the dataset file
#python3 proto-10-mb.py
#python3 proto-100-mb.py
#python3 proto-1000-mb.py


# Move to the stork runner
cd ../../../

# Run Stork on the existing pipelines
#python3 $PWD/src/stork_fs.py --repositories=$ROOT/pipelines --individual_logs=$ROOT/outputs/lfs/individual_logs/ --outputs=$ROOT/outputs/lfs/
python3 $PWD/src/stork_s3.py --credentials=$S3CONFIG --repositories=$ROOT/pipelines/ --individual_logs=$ROOT/outputs/s3/individual_logs/ --outputs=$ROOT/outputs/s3/
#python3 $PWD/src/stork_db.py --repositories=$ROOT/pipelines/ --individual_logs=$ROOT/outputs/pg/individual_logs/ --outputs=$ROOT/outputs/pg


