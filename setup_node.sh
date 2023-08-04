# Install
apt install python3.8-venv
python3 -m venv venv
source venv/bin/activate

# Install the requirements for Stork
python3 -m pip install -r requirements.txt

python3 src/log_modules/parse_repos.py --threads=12 --repos=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-2days/repositories-test --outputs=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-2days/outputs/repo_stats
python3 src/log_modules/parse_requirements.py --threads=12 --packages=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-2days/packages
python3 src/log_modules/plot_libraries.py --path=/hpi/fs00/share/fg-rabl/ilin.tolovski/stork-zip-2days/packages/
