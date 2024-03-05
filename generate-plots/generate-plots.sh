export PYTHONPATH=${PYTHONPATH}:/usr/bin/python3

mkdir plots
cd python_files

for f in *.py; do python3 "$f"; done