
# LPCE
This is for paper submission: "Speeding Up End-to-end Query Execution via Learning-based Progressive Cardinality Estimation".



## LPCE-R
In `LPCE-R` directory:

To train LPCE-R model, the first step is to train cardinality module and content module.
Content module can be adopted directly from LPCE-I.
Cardinality module needs the feature vector with real cardinalities of children nodes at exeuction plan. 
The feature vectors as training set can be found at `./data/train10K/feature.txt`, one feature vector example is:
```
1 0 0 0 0 0 0 0 1 0 0 1 ... 0 0 1 5659998 106811
```
where `5659998` and `106811` are the cardinalities of left and right children node, respectively.
Then we can train cardinality module via:
```
python3  lpce_card.py
```
After obtaining cardinality module, we can start to train refine module:
```
python3  lpcer.py
```
The training set is `/data/train10K`.
The testing set is `/queries` used for evaluating the estimation error during training. 
The mode could be configured as `Train` for training a model, or `Test` for inference in `lpcer.py`.
