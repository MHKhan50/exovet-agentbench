import pytest

from exovet_agentbench.ollama_agent import OllamaDecisionAgent


def test_parse_request_action():
    response = '{"action":"request","group":"stellar_context"}'
    assert OllamaDecisionAgent.parse_action(response, ["stellar_context"]) == "stellar_context"


def test_parse_stop_action():
    assert OllamaDecisionAgent.parse_action('{"action":"stop"}', ["stellar_context"]) is None


def test_parse_rejects_unavailable_group():
    with pytest.raises(ValueError):
        OllamaDecisionAgent.parse_action('{"action":"request","group":"hidden_data"}', ["stellar_context"])


def test_parse_rejects_non_json():
    with pytest.raises(ValueError):
        OllamaDecisionAgent.parse_action("I think we should inspect the star.", ["stellar_context"])


def test_cost_aware_prompt_adds_objective_only_in_that_condition():
    from exovet_agentbench.ollama_agent import COST_AWARE_OBJECTIVE, OllamaDecisionAgent

    args = (["transit_geometry"], ["signal_metrics"], 3.0, 0.97, {"koi_model_snr": 12.0})
    neutral = OllamaDecisionAgent(prompt_style="neutral").build_prompt(*args)
    cost_aware = OllamaDecisionAgent(prompt_style="cost_aware").build_prompt(*args)
    assert not set(COST_AWARE_OBJECTIVE) & set(neutral["rules"])
    assert cost_aware["rules"][:len(COST_AWARE_OBJECTIVE)] == COST_AWARE_OBJECTIVE
    assert {k: v for k, v in neutral.items() if k != "rules"} == {k: v for k, v in cost_aware.items() if k != "rules"}


def test_unknown_prompt_style_is_rejected():
    import pytest
    from exovet_agentbench.ollama_agent import OllamaDecisionAgent

    with pytest.raises(ValueError):
        OllamaDecisionAgent(prompt_style="friendly")
