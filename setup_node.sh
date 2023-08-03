# Install
python3 -m pip install --user virtualenv
python3 -m venv venv
source venv/bin/activate

# Install the requirements for Stork
python3 -m pip install -r requirements.txt

python3 src/log_modules/plot_libraries.py --path=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-2days/packages/node_test/

