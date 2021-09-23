# Adopt LPCE in PostgreSQL
LPCE can be used as the extension of standard PostgreSQL cost-based
query optimizer to provide cardinality estimation. 
Its basic principle is to use cardinalities estimated by learning-based estimator to replace the native cardinalities estimated by traditional histogram-based estimator.
This implementation is a generic implementation that any learning-based estimator can be adopted to serve cardinality estimation.



## Installation

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



## Usage

In `cardinality_estimation.c` file (19 line), place the path to call LPCE estimator (you may also call your own learning-based esitmator):

`char cmd[10240] = "python3 /YOUR/PATH/TO/LPCE/parser.py ";`

Enable LPCE (or your estimator) in PostgreSQL:

`set lpce.mode="learned";`


Execute SQL query:

`EXPLAIN ANALYZE SQL QUERY`




## Reference
LPCE is referenced to [AQO](https://github.com/postgrespro/aqo) ([Adaptive Cardinality Estimation](https://arxiv.org/abs/1711.08330)) implementation as an extension tool for PostgreSQL.




