# Adopt LPCE in PostgreSQL
LPCE can be used as the extension of standard PostgreSQL cost-based
query optimizer to provide cardinality estimation. 
Its basic principle is to use cardinalities estimated by learning-based estimator to replace the native cardinalities estimated by traditional histogram-based estimator.
This implementation is a generic implementation that any learning-based estimator can be adopted to serve cardinality estimation.

<br>


## Modify PostgreSQL code

In `src/backend/optimizer/path/cardprovider.c`, replace the absolute path to `LPCE-I/estimator.py`.


```
char* command_part_1 = "python3  ABSOLUTE_PATH_TO/LPCE/LPCE-I/estimator.py "; 
```
replace the absolute path to `LPCE-I/est_cards.txt`.
```
FILE *fp = fopen("ABSOLUTE_PATH_TO/LPCE/LPCE-I/est_cards.txt", "r");
```
```
fp = fopen("ABSOLUTE_PATH_TO/LPCE/LPCE-I/est_cards.txt", "r");
```
If you want to record the log of using LPCE, you might replace the log file `pg_log.txt`
```
FILE * fp = fopen("ABSOLUTE_PATH_TO/pg_log.txt", "a+");
```
<br>

## Install PostgreSQL with LPCE-I
In path of source code `postgresql-13.0/src`, make and make install:
```
make -j 8 and make install
```
<br>


## Use LPCE in PostgreSQL

Enter the database imdb
```
bin/psql -d imdb
```
Set `card_type = 2` to use cardinalities from LPCE
```
Alter system set card_type = 2;
```
Restart the postgres
```
bin/pg_ctl restart -D pgData
```
Execute your query as usual, and you may use `EXPLAIN ANALYZE` to check the execution plan
```
EXPLAIN ANALYZE SELECT COUNT(*) FROM title t,movie_companies mc,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k,movie_link ml WHERE t.id=mc.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=ml.movie_id AND t.production_year<1995 AND mc.id>967215 AND mi.info_type_id=42 AND mi_idx.id<1073108 AND mk.id<323877 AND ml.linked_movie_id<1142364;
```
If you want to set back to the default estimation of PostgreSQL `card_type = 0`, and then restart
```
Alter system set card_type = 0;
```

<br>

## Acknowledgment
- Current release is adopting LPCE-I in PostgreSQL.  We will release the implementation of using LPCE-R in PostgreSQL soon.
- Current release was tested on PostgreSQL 13.0 version.
- Current release is a naive way to call the LPCE estiamtion via linux COMMAND, which of course takes the extra cost. 
However, it is the quickest setup to use our LPCE demo.



