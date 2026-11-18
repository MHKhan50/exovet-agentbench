# Data dictionary

The raw download is a CSV subset of the NASA Exoplanet Archive Kepler Q1-Q17 DR25 Supplemental KOI table. The processed table contains `kepid`, `kepoi_name`, `target`, and the numeric feature columns below.

| Field | Meaning | Unit / type | Role |
|---|---|---|---|
| `kepid` | Kepler host-star identifier | string identifier | Group split only; never a model feature |
| `kepoi_name` | Kepler Object of Interest identifier | string identifier | Trace key only; never a model feature |
| `koi_disposition` | DR25 Supplemental best-knowledge disposition | categorical | Raw target source; removed from processed model inputs |
| `koi_pdisposition` | Original Kepler pipeline disposition | categorical | Excluded to prevent target leakage |
| `target` | Binary mapping of Supplemental disposition | 1 candidate, 0 false positive | Evaluation target only |
| `koi_model_snr` | Transit signal-to-noise ratio | dimensionless | `signal_metrics` |
| `koi_num_transits` | Number of expected or partially observed transits | count | `signal_metrics` |
| `koi_max_mult_ev` | Maximum multiple-event statistic | dimensionless | `signal_metrics` |
| `koi_max_sngle_ev` | Maximum single-event statistic | dimensionless | `signal_metrics` |
| `koi_period` | Orbital period | days | `transit_geometry` |
| `koi_duration` | Transit duration | hours | `transit_geometry` |
| `koi_depth` | Transit depth | parts per million | `transit_geometry` |
| `koi_impact` | Impact parameter | stellar radii, dimensionless | `transit_geometry` |
| `koi_ror` | Planet-to-star radius ratio | dimensionless | `transit_geometry` |
| `koi_srho` | Fitted stellar density | g/cm^3 | `transit_geometry` |
| `koi_bin_oedp_sig` | Significance of the odd-even transit depth difference (DR25 KOI table) | sigma | `fit_quality` |
| `koi_steff` | Stellar effective temperature | K | `stellar_context` |
| `koi_slogg` | Stellar surface gravity | log10(cm s^-2) | `stellar_context` |
| `koi_smet` | Stellar metallicity | dex | `stellar_context` |
| `koi_srad` | Stellar radius | solar radii | `stellar_context` |
| `koi_smass` | Stellar mass | solar masses | `stellar_context` |

Missing numerical values are retained and imputed inside each training fold. The downloader intentionally excludes `koi_score`, the original pipeline disposition `koi_pdisposition`, explicit `koi_fpflag_*` false-positive flags, disposition comments and provenance to reduce direct target leakage.
