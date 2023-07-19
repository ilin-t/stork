# Install
python3 -m venv venv
source venv/bin/activate

# Install the requirements for Stork
python3 -m pip install -r requirements.txt

# Download Python repositories from Github. Downloads all repositories from 2018 onwards.
#python3 src/log_modules/get_repos.py
python3 src/log_modules/analyze_repos.py
python3 src/log_modules/process_requirements.py
python3 src/log_modules/plot_libraries.py


#sudo -HE /home/ilint/HPI/repos/stork/venv/bin/python src/log_modules/get_repos.py
#sudo -HE /home/ilint/HPI/repos/stork/venv/bin/python src/log_modules/analyze_repos.py
#sudo -HE /home/ilint/HPI/repos/stork/venv/bin/python src/log_modules/process_requirements.py


