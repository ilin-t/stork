apt install python3.8-venv
python3 -m venv venv
source venv/bin/activate

# Install the requirements for Stork
python3 -m pip install -r requirements.txt

ROOT="/hpi/fs00/share/fg-rabl/ilin.tolovski"

python3 src/log_modules/parallel_download.py