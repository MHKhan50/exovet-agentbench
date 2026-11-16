from exovet_agentbench.evaluate import run_experiment


def test_tiny_end_to_end_experiment_writes_outputs(toy_frame, tmp_path):
    outputs = run_experiment(
        frame=toy_frame,
        output_dir=str(tmp_path / "run"),
        folds=2,
        seed=13,
        confidence_threshold=0.8,
        max_budget=5.4,
    )
    for key in ("metrics", "predictions", "traces", "metadata", "summary"):
        assert outputs[key]
        assert __import__("pathlib").Path(outputs[key]).exists()
