# Changelog

## 0.2.1 — 2026-11-20

- Paper: related work (Robovetter, Autovetter, Astronet, tool overuse); cost comparison on the same 300 KOIs
  (5.40 against 4.33, 25% more); balanced accuracy of the agents at budget 4.0 (0.785).

## 0.2.0 — 2026-11-20

- DR25 transit fits joined to the Supplemental dispositions; empty DR25 columns dropped; fit-quality group uses the
  odd-even depth significance; empty features rejected.
- Cost-aware prompt condition for the Ollama agent (`--ollama-prompt cost_aware`).
- Results: rule policies on 5,323 KOIs and LLM agents (two models, two prompts, budgets 5.4 and 4.0) on 300 KOIs in
  `reports/`; paper in `paper/`.

## 0.1.0 — 2026-11-16

- Initial release of a grouped, cost-aware evidence-acquisition benchmark for Kepler DR25 KOI dispositions.
- Added NASA TAP downloader, provenance manifests and leakage-screened preparation pipeline.
- Added signal-only, fixed-order, random-order, adaptive information-gain and full-information policies.
- Added optional guarded local Ollama policy adapter.
- Added grouped cross-validation, metrics, prediction traces, documentation and offline tests.
- No empirical benchmark results are claimed in this release.
