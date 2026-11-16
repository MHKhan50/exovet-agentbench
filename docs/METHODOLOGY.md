# Methodology

## Research question

Can a sequential agent acquire only the most useful groups of Kepler candidate evidence and reduce normalized inspection cost while retaining predictive agreement with the Kepler Q1-Q17 DR25 catalogue disposition?

This is a benchmark of **catalogue-disposition prediction and evidence acquisition**. It does not confirm or reject the physical existence of an exoplanet.

## Data source and target

The pipeline queries the fixed NASA Exoplanet Archive table `q1_q17_dr25_sup_koi`. It retains rows whose `koi_disposition` is `CANDIDATE` or `FALSE POSITIVE`. The binary target is 1 for `CANDIDATE` and 0 for `FALSE POSITIVE`. Other values, if present, are excluded.

The DR25 Supplemental table combines automated and human-based vetting and is intended to represent the best-knowledge disposition of individual KOIs. The archive explicitly distinguishes it from uniformly vetted catalogues intended for occurrence-rate calculations. This project therefore studies candidate-level catalogue-disposition prediction only; it does not estimate planet occurrence rates. The Robovetter paper documents that completeness and reliability vary with signal-to-noise and orbital period. The target must be interpreted as the published DR25 Supplemental disposition, not as error-free physical ground truth.

## Leakage control

The downloader deliberately does not request `koi_score`, the original pipeline disposition `koi_pdisposition`, explicit false-positive flags (`koi_fpflag_*`), comments, disposition provenance, or the target as model features. The target is retained only for evaluation. Host-star identifiers and KOI names are identifiers and are never model inputs.

Rows are split with `StratifiedGroupKFold` using `kepid` as the group. This prevents multiple KOIs around one host star from appearing in both training and outer-test folds.

## Evidence groups and normalized costs

The environment exposes four evidence groups in sequence. Costs are benchmark assumptions, expressed in normalized units; they are not measured telescope time, staff effort, or monetary costs.

| Group | Contents | Cost |
|---|---|---:|
| `signal_metrics` | Transit SNR, number of transits, maximum multiple-event and single-event statistics | 1.0 |
| `transit_geometry` | Period, duration, depth, impact parameter, radius ratio, fitted stellar density | 1.2 |
| `fit_quality` | Reduced chi-square and model degrees of freedom | 1.4 |
| `stellar_context` | Effective temperature, surface gravity, metallicity, stellar radius, mass and age | 1.8 |

The agent initially receives `signal_metrics`. It may request one remaining group at a time, or stop. The environment enforces the cost budget and does not expose unrequested feature values to the optional Ollama agent.

## Models and policies

A logistic-regression pipeline (median imputation, missingness indicators, standardization and class-balanced logistic regression) is fitted for every non-empty subset of evidence groups. This makes the prediction model explicit and keeps the experiment feasible on a laptop CPU.

Policies:

1. **Signal-only** — use the initial group and stop.
2. **Fixed order** — request groups in the predeclared order until confidence reaches the stopping threshold or the budget is exhausted.
3. **Random order** — request remaining groups in a seeded random order, with the same stopping rule.
4. **Adaptive information-gain policy** — estimate entropy reduction per normalized cost on an inner, host-group-disjoint calibration split. The estimate is conditioned on the current confidence bucket (low, medium or high). The outer-test labels are never used to select actions.
5. **Full-information reference** — acquire every group and use the corresponding full-feature model.
6. **Optional local Ollama policy** — a local model (default `qwen2.5:3b`) receives only currently visible evidence, the current model probability, available group names and remaining budget. Invalid actions fall back to the deterministic adaptive policy and are logged; attempted over-budget requests are caught by a separate budget guard.

The optional Ollama policy is an experimental comparator, not a required dependency and not a clinical or astronomical authority. It is run on a capped sample by default because local inference can be slow.

## Evaluation

Outer evaluation uses grouped stratified folds. Within each outer training fold, a second grouped split estimates the adaptive policy table. Final subset models are then refitted on the full outer training fold. This separates policy estimation from outer-test evaluation.

Reported metrics include accuracy, balanced accuracy, macro-F1, ROC-AUC, average precision, Brier score, mean normalized acquisition cost, mean number of evidence groups, invalid LLM actions and fallback actions. The full-information reference provides a cost/performance point, not a claim of optimality.

## Reproducibility

The data downloader records the exact TAP query, retrieval time and SHA-256. The experiment writes `metrics.csv`, `predictions.csv`, `acquisition_traces.jsonl`, `run_metadata.json` and `summary.md`. Fix the seed and retain the raw data manifest to reproduce a run.
