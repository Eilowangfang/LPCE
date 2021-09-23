
# LPCE
This is for paper submission: "Speeding Up End-to-end Query Execution via Learning-based Progressive Cardinality Estimation".

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


## Call LPCE in PostgreSQL
LPCE can be called in PostgreSQL.
LPCE can used to provide cardinality estimation for plan search in PostgreSQL.
Moreover, we also provide a generic cardinality estimator adopter for PostgreSQL, so that any learning-based estimator can be easily used to provide cardinality estimation. 
For details, please check in `/LPCE_inPostgres`.
