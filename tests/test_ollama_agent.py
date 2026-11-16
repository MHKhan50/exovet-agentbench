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
