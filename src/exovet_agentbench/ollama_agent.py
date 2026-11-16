"""Optional local Ollama policy adapter. No remote model service is used."""

from __future__ import annotations

import json
import re
from typing import Dict, Iterable, Optional
from urllib.request import Request, urlopen

from .config import FEATURE_GROUPS, GROUP_COSTS


class OllamaDecisionAgent:
    def __init__(self, model: str = "qwen2.5:3b", base_url: str = "http://localhost:11434", timeout: int = 45):
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @staticmethod
    def parse_action(response_text: str, allowed_groups: Iterable[str]) -> Optional[str]:
        """Parse a strict JSON action; None means stop, invalid actions raise ValueError."""
        text = response_text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.IGNORECASE).strip()
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end < start:
            raise ValueError("No JSON object found in Ollama response.")
        try:
            payload = json.loads(text[start:end + 1])
        except json.JSONDecodeError as exc:
            raise ValueError("Ollama response did not contain valid JSON.") from exc
        if not isinstance(payload, dict):
            raise ValueError("Ollama action must be a JSON object.")
        action = payload.get("action")
        if action == "stop":
            return None
        if action != "request":
            raise ValueError("Action must be 'request' or 'stop'.")
        group = payload.get("group")
        if not isinstance(group, str) or group not in set(allowed_groups):
            raise ValueError("Requested evidence group is not available.")
        return group

    def choose_next_group(
        self,
        available_groups,
        acquired_groups,
        remaining_budget,
        current_probability,
        visible_features: Dict[str, Optional[float]],
    ) -> Optional[str]:
        prompt_payload = {
            "task": "Choose the next evidence group for a Kepler candidate-vetting benchmark.",
            "allowed_actions": ["request", "stop"],
            "available_groups": list(available_groups),
            "available_group_costs": {group: float(GROUP_COSTS[group]) for group in available_groups},
            "available_group_fields": {group: FEATURE_GROUPS[group] for group in available_groups},
            "already_acquired_groups": list(acquired_groups),
            "remaining_normalized_budget": round(float(remaining_budget), 4),
            "current_probability_of_DR25_candidate_label": round(float(current_probability), 6),
            "visible_features_only": visible_features,
            "rules": [
                "Use only visible_features_only; do not assume values for unrequested groups.",
                "Request exactly one group from available_groups, or stop.",
                "Do not exceed the remaining budget; the environment enforces this independently.",
                "This is a research benchmark label, not an astronomical confirmation decision.",
                'Return JSON only: {"action":"request","group":"..."} or {"action":"stop"}.',
            ],
        }
        request_body = json.dumps({
            "model": self.model,
            "prompt": json.dumps(prompt_payload),
            "stream": False,
            "format": "json",
            "options": {"temperature": 0},
        }).encode("utf-8")
        request = Request(
            self.base_url + "/api/generate",
            data=request_body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=self.timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
        return self.parse_action(str(result.get("response", "")), available_groups)
