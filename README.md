# switcheroo

Smart data ingestion in machine learning pipelines

## Setup
To setup the virtual environment and install the required dependencies, run the setup.sh script with:

bash ./setup.sh

## Using the system

Run the pipeline transformer with:

python ast-playground.py --pipeline=examples/PIPELINE_NAME

There are two example pipelines:

test.py - handles only data ingestion from a local .txt file, .csv file with pandas, 
and auto-generated numpy arrays.

argus-eyes.py - example pipeline that imports four .csv files from the ArgusEyes paper by Schelter et al. 
