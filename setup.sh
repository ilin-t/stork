# Install
python3 -m venv venv
source venv/bin/activate

# Install the requirements for Stork
python3 -m pip install -r requirements.txt

# Download Python repositories from Github. Downloads all repositories from 2018.
sudo -HE /home/ilint/HPI/repos/stork/venv/bin/python src/log_modules/get_repos.py
