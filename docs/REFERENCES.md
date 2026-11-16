# References and provenance

1. **NASA Exoplanet Archive.** *Kepler Objects of Interest DR25 Table*. Dataset DOI: [10.26133/NEA5](https://doi.org/10.26133/NEA5). The archive requests that users record the version/access date and the number of returned rows. This release queries the Supplemental table `q1_q17_dr25_sup_koi`, listed in the [NASA TAP table guide](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html).
2. **Thompson, S. E., et al. (2018).** Planetary Candidates Observed by *Kepler*. VIII. A Fully Automated Catalog With Measured Completeness and Reliability Based on Data Release 25. *The Astrophysical Journal Supplement Series*, 235(2), 38. [https://doi.org/10.3847/1538-4365/aab4f9](https://doi.org/10.3847/1538-4365/aab4f9). Primary description of the DR25 Robovetter catalogue and its measured completeness/reliability.
3. **NASA Exoplanet Archive.** *Retrieving Exoplanet Archive Data With Table Access Protocol*. [TAP documentation](https://exoplanetarchive.ipac.caltech.edu/docs/TAP/usingTAP.html). Documents table names, ADQL queries and CSV output.
4. **NASA Exoplanet Archive.** *Kepler Objects of Interest (KOI) Activity Tables: Purpose of the DR25 Supplemental Table*. [Official documentation](https://exoplanetarchive.ipac.caltech.edu/docs/PurposeOfKOITable.html). Explains the difference between the uniform DR25 catalogue and the best-knowledge Supplemental dispositions.
5. **NASA Exoplanet Archive.** *Data Columns in Kepler Objects of Interest Table*. [Column documentation](https://exoplanetarchive.ipac.caltech.edu/docs/API_kepcandidate_columns.html). Definitions for disposition, transit, signal and stellar parameters; field meanings are used with the DR25 delivery.
6. **Aronsson, L., Rahbar, A., & Chehreghani, M. H. (2026).** A Survey on Active Feature Acquisition Strategies. *Proceedings of IJCAI 2026*, Survey Track, 7740–7748. [https://doi.org/10.24963/ijcai.2026/860](https://doi.org/10.24963/ijcai.2026/860). Formalizes sequential feature acquisition as cost-aware decision-making and surveys model-based, model-free and hybrid approaches.
7. **Kopparapu, V., et al. (2026).** Toward Instrument-agnostic Exoplanet Candidate Prioritization. *The Astronomical Journal*, 172, 100. [https://doi.org/10.3847/1538-3881/ae7d0f](https://doi.org/10.3847/1538-3881/ae7d0f). Recent cross-mission machine-learning work on candidate prioritization using Kepler and TESS archive parameters.
8. **Marín Díaz, G. (2025).** FAS-XAI: Fuzzy and Explainable AI for Interpretable Vetting of Kepler Exoplanet Candidates. *Mathematics*, 13(23), 3796. [https://doi.org/10.3390/math13233796](https://doi.org/10.3390/math13233796). Related interpretable machine-learning study using Kepler TCE/KOI parameters.

## Provenance notes

- The downloader uses the NASA Exoplanet Archive TAP service and selects the fixed `q1_q17_dr25_sup_koi` Supplemental delivery, not the cumulative KOI table.
- Each download creates a manifest containing the literal ADQL query, retrieval timestamp, row count and SHA-256 checksum.
- The code release is MIT licensed. The NASA dataset is not included in the ZIP; its own source terms and citation apply.
- No DOI is claimed for this software release. A repository URL is recorded in `CITATION.cff` as the intended GitHub location.
