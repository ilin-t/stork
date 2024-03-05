export PYTHONPATH=${PYTHONPATH}:/usr/bin/python3

mkdir plots
cd python_files
#python3 plot_distributions.py
#python3 plot_library_distribution.py
#python3 plot_library_tail.py
#python3 plot_llm_results.py
#python3 plot_pipeline_dist.py
##python3 plot_ratios.py


for f in *.py; do python3 "$f"; done