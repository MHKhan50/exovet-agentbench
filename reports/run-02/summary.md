# ExoVet-AgentBench experiment summary

This file is generated from the actual run. It contains no pre-filled or assumed performance results.

- Rows used: 5323
- Host-star groups: 5158
- Outer folds: 5
- Seed: 17
- Confidence threshold: 0.85
- Maximum normalized budget: 5.4

## Metrics

```text
          policy  n_samples  accuracy  balanced_accuracy  macro_f1  roc_auc  average_precision  brier_score  mean_acquisition_cost  mean_groups_acquired  mean_invalid_actions  mean_fallback_actions  mean_budget_guard_events
     signal_only       5323  0.679316           0.744463  0.662326 0.805241           0.485932     0.189784               1.000000              1.000000                   0.0                    0.0                       0.0
           fixed       5323  0.763667           0.798756  0.738037 0.863232           0.626524     0.157309               3.855796              2.975202                   0.0                    0.0                       0.0
          random       5323  0.763479           0.798393  0.737794 0.863538           0.631755     0.157355               4.030434              3.073831                   0.0                    0.0                       0.0
        adaptive       5323  0.763667           0.798519  0.737968 0.863427           0.625544     0.157230               3.825437              2.946459                   0.0                    0.0                       0.0
full_information       5323  0.764231           0.799136  0.738559 0.866696           0.640123     0.156415               5.400000              4.000000                   0.0                    0.0                       0.0
```

Interpretation note: the target is the DR25 catalogue disposition, not independently established planetary truth.