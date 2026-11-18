"""Command-line interface for ExoVet-AgentBench."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .data import download_dataset, load_prepared_dataset, prepare_dataset, sha256_file
from .evaluate import run_experiment


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="exovet", description="Budgeted evidence-acquisition benchmark for Kepler KOI vetting.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    download_parser = subparsers.add_parser("download", help="Download the Kepler Q1-Q17 DR25 Supplemental KOI table subset.")
    download_parser.add_argument("--output", default="data/raw/koi_dr25.csv")
    download_parser.add_argument("--timeout", type=int, default=90)

    prepare_parser = subparsers.add_parser("prepare", help="Prepare numeric features and the DR25 disposition target.")
    prepare_parser.add_argument("--input", default="data/raw/koi_dr25.csv")
    prepare_parser.add_argument("--output", default="data/processed/koi_prepared.csv")

    run_parser = subparsers.add_parser("run", help="Run grouped cross-validation and write reproducible reports.")
    run_parser.add_argument("--input", default="data/processed/koi_prepared.csv")
    run_parser.add_argument("--output", default="reports/run-01")
    run_parser.add_argument("--folds", type=int, default=5)
    run_parser.add_argument("--seed", type=int, default=17)
    run_parser.add_argument("--max-samples", type=int, default=None, help="Optional reproducible row cap for a quick pilot.")
    run_parser.add_argument("--confidence-threshold", type=float, default=0.85)
    run_parser.add_argument("--max-budget", type=float, default=5.4)
    run_parser.add_argument("--include-ollama", action="store_true", help="Add a small optional local Ollama-agent evaluation.")
    run_parser.add_argument("--ollama-model", default="qwen2.5:3b")
    run_parser.add_argument("--ollama-sample-limit", type=int, default=50)
    run_parser.add_argument("--ollama-base-url", default="http://localhost:11434")
    run_parser.add_argument("--ollama-prompt", choices=["neutral", "cost_aware"], default="neutral",
                            help="neutral: v0.1 prompt; cost_aware: also states that evidence should be bought only when worth its cost.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.command == "download":
        manifest = download_dataset(args.output, timeout=args.timeout)
        print(json.dumps(manifest, indent=2))
    elif args.command == "prepare":
        manifest = prepare_dataset(args.input, args.output)
        print(json.dumps(manifest, indent=2))
    elif args.command == "run":
        frame = load_prepared_dataset(args.input)
        outputs = run_experiment(
            frame=frame,
            output_dir=args.output,
            folds=args.folds,
            seed=args.seed,
            max_samples=args.max_samples,
            confidence_threshold=args.confidence_threshold,
            max_budget=args.max_budget,
            include_ollama=args.include_ollama,
            ollama_model=args.ollama_model,
            ollama_sample_limit=args.ollama_sample_limit,
            ollama_base_url=args.ollama_base_url,
            ollama_prompt=args.ollama_prompt,
            input_sha256=sha256_file(Path(args.input)),
        )
        print(json.dumps(outputs, indent=2))
        print("\nMetrics:")
        print(Path(outputs["metrics"]).read_text(encoding="utf-8"))

if __name__ == "__main__":
    main()
