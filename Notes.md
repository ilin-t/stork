### Notes

### Preprocessing implementation
* Use a tree structure to follow the preprocessing steps from the import of a library to the final data shape
  * Creating a DAG is one option, check Behrouz's paper
  * Indexing of preprocessing steps - BTree?

* Inject format checking in between to ensure data format compatibility 

* Do generic transformations like sklearn provides (look in the pipeline from Ricardo)  

    *TODO:* Finish up the visitor methods.
### Evaluation
* Create a baseline pipeline for each pipeline. Use a generic model (RF, log regression, etc.) to achieve baseline pipeline performance.
* Use the baseline to compare for a "random" pipeline that your dataset was used for and adapted and whether it proved for a better performance

### Paper
* Provide the paper structure
* Write up a motivation
* Outline the contributions and evaluation criteria

