# ExoVet-AgentBench experiment summary

This file is generated from the actual run. It contains no pre-filled or assumed performance results.

- Rows used: 6816
- Host-star groups: 6503
- Outer folds: 5
- Seed: 17
- Confidence threshold: 0.85
- Maximum normalized budget: 5.4

## Metrics

```text
          policy  n_samples  accuracy  balanced_accuracy  macro_f1  roc_auc  average_precision  brier_score  mean_acquisition_cost  mean_groups_acquired  mean_invalid_actions  mean_fallback_actions  mean_budget_guard_events
     signal_only       6816  0.454372           0.496061  0.447811 0.494422           0.287833     0.250000               1.000000              1.000000                   0.0                    0.0                       0.0
           fixed       6816  0.663292           0.556143  0.557644 0.629302           0.377322     0.246055               5.397183              3.998239                   0.0                    0.0                       0.0
          random       6816  0.663292           0.556143  0.557644 0.629302           0.377322     0.246055               5.399061              3.999413                   0.0                    0.0                       0.0
        adaptive       6816  0.663292           0.556143  0.557644 0.629302           0.377322     0.246055               5.397183              3.998239                   0.0                    0.0                       0.0
full_information       6816  0.663292           0.556143  0.557644 0.629302           0.377322     0.246055               5.400000              4.000000                   0.0                    0.0                       0.0
```

Interpretation note: the target is the DR25 catalogue disposition, not independently established planetary truth.