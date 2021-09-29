
# LPCE
This is for paper submission: "Speeding Up End-to-end Query Execution via Learning-based Progressive Cardinality Estimation".

<br/> 

## LPCE-I
In `LPCE-I` directory:


Train LPCE-I model:
```
python3  lpcei.py
```
The training set is `/data`.
The testing set is `/queries` used for evaluating the estimation error during training. 
The mode could be configured as `Train` for training a model, or `Test` for inference in `lpcei.py`.

LPCE-I model for cardinality estimation:
```
python3  estimator.py "SQL QUERY"
```
The return contains: 
1) a number of cardinalities that needs to estimate for plan search via dynamic programming.
2) the model inference time, which includes the cost of parsing and encoding the query.
3) a list of estimated cardinalities. 


In `workload` directory:
There are query workloads for testing. The queries are formatted as:
```
SQL QUERY#End-to-end execution#Cardinality
```
Here the end-to-end execution is the time (unit ms) of executing the query on PostgreSQL 13.0.

In `model` directory:
there is an example ready model `example_model.pth`, which can be further compressed via knowledge distillation.













