
# LPCE-R
This presents how train and use LPCE-R

<br/> 

## Model training
Figure 9 in the paper present the training procedures.

In `module` directory:
1. Train `Content` module
```
python3  LPCE-I.py mode epoch_num
```
- `mode` can be selected as `Train` for training, and `Test` for testing when a model is ready. `epoch_num` is optimal setting, and as 100 epochs by default.

-  A ready model `content_module.pth` can be found at `/model` when training completes.

- The training set is in `/data`, which contians around 10K samples having 6-8 joins.


<br/> 

2. Train `Cardinality` module
```
python3  LPCE_card.py mode epoch_num
```
- `mode` can be selected as `Train` for training, and `Test` for testing when a model is ready. `epoch_num` is optimal setting, and as 30 epochs by default.

-  A ready model `card_module.pth` can be found at `/model` when training completes.

- The training set is in `/data`, which contians around 10K samples having 6-8 joins.



<br/> 

3. Train `Refine` module
```
python3  LPCE-R.py mode epoch_num

```
- Make sure trained `Cardinality` and `Refine` module can be found at `/model`.

- `mode` can be selected as `Train` for training, and `Test` for testing when a model is ready. `epoch_num` is optimal setting, and as 30 epochs by default.

- A ready model `refine_module.pth` can be found at `/model` when training completes.


<br/> 

## Use LPCE-R for query re-optimization
`estimator_test.py` presents an example of how to use LPCE-R for query re-optimization.

The example query is like:
```
 Query = "EXPLAIN ANALYZE SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info_idx mi_idx,movie_keyword mk,keyword k,movie_link ml WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=ml.movie_id AND t.production_year<1980 AND mc.id>48177 AND ci.person_id>3615876 AND mi_idx.id<842005 AND k.keyword<57169 AND ml.linked_movie_id<2164366;"
```
Assume some nodes are executed, and we get the actual cardinalities of these nodes in form of `'relids,actual_card'`.
Note that `relids` is used by PostgreSQL to denote an (intermediate) involved relation, and `'relids,actual_card'` can be collected from PostgreSQL once the nodes executed.
```
real_info = "16,842004,2,1,236,1,64,57169,164,1332318,164,1332318,132,72974,32,4523930,132,72974,4,2560952,128,45978,4,2560952,64,57169,16,842004,"
```

<br/> 

## Use LPCE-R in PostgreSQL
`estimator.py` can be cooperate with PostgreSQL for query re-optimization, during which LPCE-R receives the info. about the executed nodes,
and refines the estimation for unexecuted nodes.

PostgreSQL are needed modification to support query re-optimization (e.g., change the nested loop as blocked, and add CHECKPOINT). The implemenation will be released soon.



<br/> 

## Appendix for PostgreSQL query optimization
If you are interested how the PostgreSQL query optimization works, especially what is `relids`,
you may refer to the [ZhiHu blog](https://zhuanlan.zhihu.com/p/460709260). (Sorry for only avaiable to chinese reader.) 
