# Ethics, scientific scope and limitations

## Intended use

This repository is an educational and research benchmark for sequential evidence acquisition on a public astronomy catalogue. It is not an exoplanet discovery system, candidate confirmation tool, telescope scheduler or substitute for professional astronomical analysis.

## Label semantics

The target is the Kepler DR25 Supplemental `koi_disposition`. The Supplemental table combines automated and human vetting and is intended to provide a best-knowledge disposition for individual KOIs. A `CANDIDATE` label is not proof that an object is a planet. The archive notes that some statistically validated or confirmed objects may be classified as false positives after detailed follow-up review. The underlying Robovetter study also reports that completeness and reliability vary with period and signal-to-noise. Model performance against these labels is therefore not equivalent to physical truth or scientific discovery.

## Dataset and selection effects

The dataset contains objects selected into the Kepler KOI process. It is not a random sample of stars or all possible transiting events. The DR25 Supplemental table is not the uniformly vetted sample intended for occurrence-rate calculations. Results may reflect the Kepler instrument, pipeline, stellar population, data-release choices, follow-up availability and historical vetting practice.

## Evidence costs

The four evidence-group costs are normalized experimental assumptions. They are not observed costs of retrieving telescope data, running a scientific test, or employing an astronomer. Any operational interpretation requires cost elicitation with domain experts and sensitivity analysis.

## Model limitations

The first release uses tabular catalogue features and logistic regression. It does not process raw light curves, pixel-level diagnostics, spectroscopy, radial-velocity follow-up, image-centroid data or external astrophysical catalogues. The optional Ollama agent is local and experimental; its text output is not a scientific explanation and must not be treated as one.

## Leakage and validation

The pipeline excludes the disposition score, explicit false-positive flags, comments and provenance fields from model inputs. Host-star grouped splitting reduces same-star leakage. Nevertheless, derived catalogue features may share upstream pipeline information, and a host-group split does not establish transfer to TESS, PLATO or another instrument. Independent mission-level validation is required.

## Data handling

The dataset is downloaded directly from the NASA Exoplanet Archive and is not redistributed in this repository. Preserve the archive DOI, retrieval timestamp and checksum. Review the archive's current data-use and acknowledgement guidance before redistribution or commercial use.

## Human oversight

No model output should be used to confirm or reject a planet, prioritize expensive follow-up observations, or publish an astrophysical claim without independent review by qualified astronomers and corroborating evidence.
