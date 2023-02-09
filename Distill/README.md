
# LPCE
This is for paper submission: "Speeding Up End-to-end Query Execution via Learning-based Progressive Cardinality Estimation".

<br/> 




<br/> 

## Distillation
In `Distill` directory:

To further compress LPCE-I model with knowledge distillation, run:
```
python3  lpce_distill.py
```
In `lpce_distill` directory:
there are `sru_distill.py` that enables SRU student model to extract knowledge from teacher model,
and `trainer_distll.py` that guides the training flow with teacher model, which contains the loss computation of hint and prediction loss.