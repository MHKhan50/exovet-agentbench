# ExoVet-AgentBench

**Budgeted Agentic Evidence Acquisition for Kepler Exoplanet Candidate Vetting**
Version: `0.2.1` · Python `3.9+` · Lightweight CPU workflow

## Project overview

ExoVet-AgentBench studies whether a tool-using agent can request only the most useful groups of astronomical evidence before predicting a Kepler DR25 Supplemental catalogue disposition. The benchmark treats evidence inspection as a sequential, cost-aware decision problem.

The agent starts with inexpensive transit signal metrics, then may request transit geometry, model-fit quality or stellar context. It can stop when its predictive confidence reaches a threshold or its normalized evidence budget is exhausted. A local Ollama policy is available as an optional comparator; deterministic policies run without any language model.

**Important scientific boundary:** the target is the Kepler DR25 Supplemental catalogue disposition (`CANDIDATE` versus `FALSE POSITIVE`). It is not physical confirmation of an exoplanet. Do not use this package to confirm candidates or allocate telescope time.

## Why this research question?

Recent active-feature-acquisition literature frames sequential feature requests as cost-aware decision-making. Exoplanet vetting research continues to study classification, reliability and candidate prioritization, including cross-instrument models. This project connects those areas through a reproducible evidence-acquisition environment with explicit costs, tool traces, grouped validation and leakage controls. It is an exploratory research question, not a claim that no prior work exists.

## Research questions

1. Can sequential evidence acquisition approach full-information predictive performance at lower normalized acquisition cost?
2. Does confidence-conditioned information-gain acquisition outperform fixed and random evidence ordering at matched budgets?
3. Can a small local LLM choose valid evidence requests under explicit tool and budget constraints?

See `docs/EXPERIMENT_PROTOCOL.md` before running experiments.

## Results (v0.2.0)

**Paper:** *Told the Price, Buying Everything: Small LLM Agents in Cost-Aware Evidence Acquisition for Kepler Candidate Vetting* — [`paper/main.pdf`](paper/main.pdf).

5,323 KOIs (1,377 candidates), five folds grouped by host star; 95% intervals from 1,000 host-star bootstrap resamples.

| Budget | Policy | Mean cost | ROC AUC | Balanced accuracy |
|---|---|---|---|---|
| – | Signal only | 1.00 | 0.805 [0.794, 0.817] | 0.744 |
| – | Full information | 5.40 | 0.867 [0.857, 0.877] | 0.799 |
| 5.4 | Fixed | 3.86 | 0.863 | 0.799 |
| 5.4 | Random | 4.03 | 0.864 | 0.798 |
| 5.4 | Adaptive | 3.83 | 0.863 | 0.799 |
| 4.0 | Adaptive | 2.97 | 0.861 | 0.795 |

- Stopping at 85% confidence saves 29% of the cost with the same balanced accuracy (difference −0.001 [−0.002, 0.000]).
- The information-gain order equals the fixed order: it chose transit geometry second for 3,968 of 3,991 KOIs.
- **LLM agents** (`qwen2.5:3b`, `llama3.1:8b`; 300 fold-1 KOIs): with a neutral or a cost-aware prompt they never
  stopped early and bought every affordable group in every episode, including 47 KOIs already clear after the first
  group. At budget 4.0 `qwen2.5:3b` requested an unaffordable group in all 300 episodes.

Runs: `reports/run-02` (rule policies), `reports/agent-*-neutral-b5.4`, `reports/agent-*-costaware-b5.4` and
`reports/agent-*-costaware-b4.0` (per-KOI predictions and acquisition traces).

## Repository structure

```text
exovet-agentbench/
├── src/exovet_agentbench/    # dataset, models, agent policies, evaluation, CLI
├── tests/                    # offline unit and end-to-end smoke tests
├── docs/                     # methodology, protocol, data dictionary, ethics, references
├── data/                     # empty raw/processed directories; data is downloaded separately
├── reports/                  # generated experiment outputs
├── .github/workflows/        # Python CI
├── CITATION.cff
├── LICENSE
├── pyproject.toml
└── README.md
```

## Requirements

- Python 3.9 or newer
- macOS, Linux or Windows
- 1–2 GB free disk space is ample for code, environment and the small catalogue CSV; no GPU is required
- Optional: Ollama with a local model such as `qwen2.5:3b`

The project uses pinned NumPy, pandas and scikit-learn versions (see `pyproject.toml` and `requirements.txt`). It does not require PyTorch, TensorFlow, a cloud API key or a GPU.

## Setup in VS Code

Open the extracted `ExoVet-AgentBench-v0.1.0` folder in VS Code, then open **Terminal → New Terminal**.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
pytest -q
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` instead of the `source` command.

## Download and prepare the real dataset

The dataset is not included in this release. It is retrieved directly from the NASA Exoplanet Archive TAP service. The downloader records the exact query, UTC retrieval time, returned row count and SHA-256 checksum.

```bash
python -m exovet_agentbench download --output data/raw/koi_dr25.csv
python -m exovet_agentbench prepare --input data/raw/koi_dr25.csv --output data/processed/koi_prepared.csv
```

The fixed source table is `q1_q17_dr25_sup_koi`; the target column is `koi_disposition`. The pipeline retains `CANDIDATE` and `FALSE POSITIVE` rows only. It excludes the original pipeline disposition (`koi_pdisposition`), explicit DR25 disposition score, false-positive flags, comments and provenance from model inputs. The Supplemental table combines automated and human vetting; it is not a uniform sample for occurrence-rate estimation.

## Run the benchmark

```bash
python -m exovet_agentbench run \
  --input data/processed/koi_prepared.csv \
  --output reports/run-01 \
  --folds 5 \
  --seed 17
```

For a quick pilot, cap the number of rows (this changes the evaluation sample and must be reported):

```bash
python -m exovet_agentbench run --input data/processed/koi_prepared.csv --output reports/pilot-01 --folds 3 --seed 17 --max-samples 1200
```

The run writes:

- `metrics.csv` — predictive and acquisition metrics by policy
- `predictions.csv` — per-object predictions and acquisition costs
- `acquisition_traces.jsonl` — auditable sequential tool-use traces
- `run_metadata.json` — settings, versions, class counts and split details
- `summary.md` — generated metric table and interpretation boundary

No benchmark performance numbers are pre-filled in this repository. Run the experiment on the downloaded archive snapshot before reporting results.

## Optional local Ollama agent

Start Ollama locally and make sure the model is available. The default model matches the lightweight local-model setup documented for this research workstation.

```bash
ollama list
python -m exovet_agentbench run \
  --input data/processed/koi_prepared.csv \
  --output reports/ollama-pilot-01 \
  --folds 5 \
  --seed 17 \
  --include-ollama \
  --ollama-model qwen2.5:3b \
  --ollama-sample-limit 50
```

The Ollama agent sees only evidence groups already acquired, the current model probability, remaining budget and available group names. It does not receive the hidden feature groups or target. Invalid actions are logged and fall back to the deterministic adaptive policy; attempted over-budget requests are intercepted by the environment guard. The default LLM sample limit is small; do not compare its metrics with full-test metrics unless all policies are evaluated on the same sample.

## GitHub repository

Create the public repository with this exact name:

`MHKhan50/exovet-agentbench`

After tests and data/experiment review, the intended SSH publishing commands are:

```bash
git init
git add .
git commit -m "Initial release: ExoVet-AgentBench v0.1.0"
git branch -M main
git remote add origin git@github.com:MHKhan50/exovet-agentbench.git
git push -u origin main
```

The dataset is excluded from Git by `.gitignore`; commit the downloader manifests and experiment outputs only if they are appropriate for the repository and do not contain unreviewed large data files.

## Testing

```bash
pytest -q
python -m compileall -q src tests
```

The tests use small temporary in-memory fixtures to verify software behaviour. Those fixtures are not astronomical observations and are not used as research data. A passing test suite verifies code paths, not the scientific validity of a result.

## Research documentation

- `docs/PROJECT_RATIONALE.md`
- `docs/METHODOLOGY.md`
- `docs/EXPERIMENT_PROTOCOL.md`
- `docs/DATA_DICTIONARY.md`
- `docs/ETHICS_AND_LIMITATIONS.md`
- `docs/REFERENCES.md`

## Citation

See `CITATION.cff`. Cite the NASA archive dataset with DOI [10.26133/NEA5](https://doi.org/10.26133/NEA5) and the DR25 catalogue paper with DOI [10.3847/1538-4365/aab4f9](https://doi.org/10.3847/1538-4365/aab4f9). Record the dataset retrieval timestamp and checksum from the generated manifest.

## License

The software in this repository is released under the MIT License. The NASA Exoplanet Archive dataset is not bundled; its source terms and acknowledgement guidance remain applicable.
