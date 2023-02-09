
# LPCE-I
This is for paper submission: "Speeding Up End-to-end Query Execution via Learning-based Progressive Cardinality Estimation".

<br/> 

## Model training
In `LPCE-I` directory:

Train LPCE-I model:
```
python3  lpcei.py mode epoch_num
```
- `mode` can be selected as `Train` for training, and `Test` for testing when a model is ready. `epoch_num` is optimal setting, and as 100 epochs by default.

-  A ready model `model_i.pth` can be found at `/model` when training completes.

- The training set is in `/data`, which contians around 10K samples having 6-8 joins.


<br/> 

## Model Inference
LPCE-I model for cardinality estimation:
```
python3  estimator.py "SQL QUERY"
```
-  "SQL QUERY" is one query, note that currently only simple IMDB query are supported.
For example:
```
python3  estimator.py "SELECT COUNT(*) FROM title t,movie_companies mc,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k,movie_link ml WHERE t.id=mc.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=ml.movie_id AND t.production_year<1995 AND mc.id>967215 AND mi.info_type_id=42 AND mi_idx.id<1073108 AND mk.id<323877 AND ml.linked_movie_id<1142364;"
```

The return is like:
```
Number of cardinalities to estimate: 96
Model inference time:  35.635948181152344 ms
Learned estimator outputs cardinality:
[345086, 507478, 19613, 393467...]

``` 
The information includes:
-  a number of cardinalities that needs to estimate for plan search via dynamic programming.
-  the model inference time, which includes the cost of parsing and encoding the query.
-  a list of estimated cardinalities, which are the cardinalities needed for plan search dynamic programming at PostgreSQL query optimization.

The estimation result are stored in a file `est_cards.txt`, each line is like:

```
relids,estimated_card
2,345086
4,507478
``` 
- `relids` is the relation relids used in PostgreSQL optimizer (refer to PostgreSQL source code /src/backend/optimizer).
- `estimated_card` is the estimation of LPCE-I.

Espeically, you might need to rewrite the path of trained model and estiamtion results in `estimator.py`:

``` 
model_path = "ABSOLUTE_PATH_TO_TRAINED_MODEL"
result_path = "ABSOLUTE_PATH_TO_STORE_ESTIMATION_RESULT"
``` 


<br/> 

## LPCE-I in PostgreSQL
Refer to PostgreSQL-LPCE for how use the cardinalities provided by LPCE-I for query optimization.















