# Experiment protocol (pre-results)

## Primary questions

- **RQ1:** At what normalized acquisition cost do sequential policies reach predictive performance close to the full-information reference?
- **RQ2:** Does confidence-conditioned information-gain acquisition outperform fixed and random evidence ordering at matched cost budgets?
- **RQ3:** On a capped sample, can a local Ollama model choose valid evidence requests and achieve a useful cost/performance trade-off relative to deterministic policies?

## Hypotheses to test (not results)

- **H1:** Adaptive acquisition will reduce mean acquisition cost relative to full information while maintaining competitive macro-F1.
- **H2:** The adaptive policy will outperform random ordering at comparable normalized cost.
- **H3:** The optional local LLM policy will produce some invalid or suboptimal requests; the environment guard should prevent budget violations and log fallbacks.

These are falsifiable hypotheses. No result is assumed in the repository.

## Dataset and labels

- Source: NASA Exoplanet Archive, Kepler Q1-Q17 DR25 Supplemental KOI table (`q1_q17_dr25_sup_koi`).
- Target: `koi_disposition`; 1 = `CANDIDATE`, 0 = `FALSE POSITIVE`.
- Exclude rows with other dispositions and missing host-star or KOI identifiers.
- Do not substitute the cumulative KOI table: it combines activity tables with different disposition and parameter provenance. The DR25 Supplemental table is intentionally a best-knowledge, human-plus-automated disposition source and is not a uniform sample for occurrence-rate estimation; this protocol is limited to individual KOI disposition prediction.
- Exclude the original pipeline disposition (`koi_pdisposition`), explicit disposition scores, false-positive flags, comments and provenance fields from model inputs.

## Splits and leakage controls

- Primary protocol: 5 outer `StratifiedGroupKFold` folds, seed 17, grouped by `kepid`.
- For each outer fold, use an inner grouped split from the outer training partition to estimate the adaptive acquisition table.
- Fit imputers and scalers within each training partition only.
- Keep all rows for a host star in one fold.
- Report the actual row count, class counts, unique host count, data hash and retrieval timestamp.

## Baselines and policy settings

- Signal-only, fixed-order, random-order, adaptive information-gain and full-information reference.
- Default stop threshold: maximum class probability >= 0.85.
- Default normalized budget: 5.4 (the sum of all group costs).
- Sensitivity analysis: confidence thresholds 0.65, 0.75, 0.85 and 0.95; budgets 2.2, 3.6 and 5.4; and a ±25% perturbation of each group cost.
- Optional local Ollama comparator: `qwen2.5:3b`, temperature 0, maximum 50 test samples per run by default. Report its sample count separately; do not compare it to full-test metrics without matching the evaluation sample.

## Metrics

- Predictive: accuracy, balanced accuracy, macro-F1, ROC-AUC, average precision, Brier score.
- Acquisition: mean normalized cost, mean number of groups requested, cost/performance curve.
- Agent integrity: invalid action count, fallback count and budget-guard override count. The environment must prevent actual budget overspend; an attempted over-budget request is logged and replaced or stopped.
- Report per-fold metrics and uncertainty intervals in any paper extension. The initial CLI aggregates predictions across folds; a publication-grade study should add host-cluster bootstrap intervals and predeclared subgroup analyses.

## Decision rules

The primary comparison is adaptive versus fixed and random policies at their observed mean costs. Do not claim superiority solely from a single threshold. Report the full-information reference and cost/performance trade-off. If the target distribution or split sizes differ materially from expectations, document the deviation before interpreting results.

## Non-claims

This protocol does not estimate exoplanet occurrence rates, validate candidates, allocate telescope time, or replace expert vetting. Catalogue dispositions are proxy labels and may contain errors or selection effects.
