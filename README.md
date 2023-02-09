
# LPCE
This is for SIGMOD 2023 paper: "Speeding Up End-to-end Query Execution via Learning-based Progressive Cardinality Estimation".
This branch is only for author's use.

<br/> 

## LPCE-I

- In `LPCE-I` directory, please check the `README` for how to train and test  LPCE-I model.

<br/> 

## LPCE-R
-  In `LPCE-R` directory, please check the `README` for how to train and test  LPCE-R model.


<br/>

## Workload
- In `Workload` directory, please check the `join-six.sql` and `join-eight.sql` for experiments.

<br/>

## Distill
-  In `Distill` directory, please check the `README` for how to distill LPCE model.


<br/>

## Use LPCE in Postgres
- In `LPCE_inPostgres` directory, please check how to adopt LPCE in PostgreSQL for query speedup.

<br/>

## Technical report
- `techreport.pdf` fills in some details not shown in SIGMOD paper due to the limited space.


<br/>

## From author
- Current release is adopting LPCE-I in PostgreSQL.  We will release the adoption of LPCE-R in PostgreSQL soon.
- Current release was tested on PostgreSQL 13.0 version.
