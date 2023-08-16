# Stork

System for automated data and pipeline migration. Stork automates the process of data and pipeline migration to database and cloud environments.
Stork migrates the data and project in three steps:
1. Pipeline Analysis
2. Data Transfer
3. Pipeline Rewrite

### Static Code Analysis 

Through parsing the AST of each pipeline in a given repository, Stork generates essential metadata regarding the location and format of the data. Next, Stork formats and migrates the data to a new destination in a hosted Database Management System or a cloud storage service. 

## Setup [TODO - outdated]
To setup the virtual environment and install the required dependencies, run the setup.sh script with:

* bash ./setup.sh

## Using the system [TODO - outdated]
Run the pipeline transformer with:

* python ast-playground.py --pipeline=examples/PIPELINE_NAME

There are two example pipelines:

test.py - handles only data ingestion from a local .txt file, .csv file with pandas, 
and auto-generated numpy arrays.

argus-eyes.py - example pipeline that imports four .csv files from the ArgusEyes paper by Schelter et al. 
