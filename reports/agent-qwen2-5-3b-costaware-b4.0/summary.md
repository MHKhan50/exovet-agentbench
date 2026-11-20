# ExoVet-AgentBench experiment summary

This file is generated from the actual run. It contains no pre-filled or assumed performance results.

- Rows used: 5323
- Host-star groups: 5158
- Outer folds: 5
- Seed: 17
- Confidence threshold: 0.85
- Maximum normalized budget: 4.0

## Metrics

```text
          policy  n_samples  accuracy  balanced_accuracy  macro_f1  roc_auc  average_precision  brier_score  mean_acquisition_cost  mean_groups_acquired  mean_invalid_actions  mean_fallback_actions  mean_budget_guard_events
     signal_only       5323  0.679316           0.744463  0.662326 0.805241           0.485932     0.189784               1.000000              1.000000                   0.0                    0.0                       0.0
           fixed       5323  0.756153           0.793924  0.731160 0.857522           0.594111     0.160911               2.773699              2.374037                   0.0                    0.0                       0.0
          random       5323  0.759158           0.796660  0.734137 0.860639           0.619304     0.159602               3.015818              2.445426                   0.0                    0.0                       0.0
        adaptive       5323  0.759158           0.795242  0.733729 0.861147           0.618047     0.158425               2.967387              2.374413                   0.0                    0.0                       0.0
full_information       5323  0.764231           0.799136  0.738559 0.866696           0.640123     0.156415               5.400000              4.000000                   0.0                    0.0                       0.0
          ollama        300  0.753333           0.785373  0.735450 0.860139           0.703638     0.163866               4.000000              3.000000                   1.0                    1.0                       1.0
```

Interpretation note: the target is the DR25 catalogue disposition, not independently established planetary truth.