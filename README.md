
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


In `workload` directory:
There are query workloads for testing. The queries are formatted as:
```
SQL QUERY#End-to-end execution#Cardinality
```
Here the end-to-end execution is the time of executing the query on PostgreSQL 13.0.




## Call LPCE in PostgreSQL
LPCE can be called in PostgreSQL.
LPCE can used to provide cardinality estimation for plan search in PostgreSQL.
Moreover, we provide a generic cardinality estimation adopter for PostgreSQL, so that any learning-based estimator can be easily used to provide cardinality estimation. 
For details, please check in `/LPCE_inPostgres`.



### Installation

The module works with PostgreSQL 13.0 .
LPCE has to be unpacked into contrib directory and then to be compiled and
installed with `make install`.

```
cd contrib/LPCE                                                  # enter aqo directory
make && make install                                             # install LPCE
make clean && make && make install                               # (if re-install LPCE)
```

In your database:

`CREATE EXTENSION aqo;`

Modify your postgresql.conf:

`shared_preload_libraries = 'LPCE'`

and restart PostgreSQL. It is essential that library is preloaded during server startup, because
adaptive query optimization must be enabled on per-cluster basis instead
of per-database.



### Usage

In `cardinality_estimation.c` file (19 line), place the path to call LPCE estimator (you may also call your own learning-based esitmator):

`char cmd[10240] = "python3 /YOUR/PATH/TO/LPCE/parser.py ";`

Enable LPCE (or your estimator) in PostgreSQL:

`set lpce.mode="learned";`


Execute SQL query:

`EXPLAIN ANALYZE SQL QUERY`




### Acknowledgment
LPCE is based on [AQO](https://github.com/postgrespro/aqo) ([Adaptive Cardinality Estimation](https://arxiv.org/abs/1711.08330)) implementation as an extension tool for PostgreSQL.

