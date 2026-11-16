# Project rationale and portfolio-overlap check

## Selected domain

Astronomy / exoplanet candidate vetting. The project studies **sequential evidence acquisition** over Kepler Objects of Interest (KOIs), rather than creating another generic agent-reliability benchmark or upgrading an earlier project.

## Portfolio-overlap review

The available public repository list and known completed work were reviewed before topic selection. Existing work spans agent memory integrity, tool policies and recovery, cancellation and decomposition, RAG and retrieval, procurement and allocation, flood/heat/groundwater/environmental monitoring, healthcare workflows, education, Roman Urdu/Turkic language work, OCR, image/audio classification and digital-history projects. No existing exoplanet, astronomy or Kepler candidate-vetting project was identified.

This project therefore adds a distinct scientific domain and data source. It does not reuse the scope of DialysisFlow-AgentBench or rename an earlier Pakistan, healthcare, environmental, multilingual, procurement, education or generic agent-reliability project.

## Literature and data suitability

- The NASA Exoplanet Archive documents the DR25 Supplemental KOI table as a best-knowledge candidate/false-positive catalogue built from automated and human vetting, including follow-up information. The archive explicitly distinguishes it from uniformly vetted catalogues intended for occurrence-rate calculations. This project limits its claims to individual catalogue-disposition prediction.
- Thompson et al. (2018) describe the underlying Kepler DR25 Robovetter catalogue and show that completeness and reliability vary across signal-to-noise and period regimes.
- IJCAI 2026 provides a recent peer-reviewed survey of active feature acquisition as cost-aware sequential decision-making.
- Recent exoplanet ML work includes cross-instrument candidate prioritization (2026) and interpretable Kepler vetting (2025). The project does **not** claim to be the first ML system for exoplanet vetting. Its research question is the controlled comparison of evidence-request policies, explicit acquisition costs and optional local LLM tool selection.

## Feasibility

The NASA archive documentation reports 9,564 KOIs in the Supplemental table. The project downloads only a selected set of tabular fields, not multi-gigabyte light-curve or posterior-chain archives. A CPU-only scikit-learn workflow with four evidence groups is suitable for the MacBook Air M4 / 16 GB configuration. The repository contains no copy of the dataset; the pipeline downloads it from the archive and records a timestamp and checksum.

## Novelty statement

This is a new project in the user's known portfolio, not a verified first-in-literature contribution. Any publication claim must be based on the completed experiments, a broader literature review and expert review of the benchmark design.
