# src/embeddings/cost_tracker.py
"""
Track embedding costs in real-time.
"""

from dataclasses import dataclass, field
from typing import Dict
import time


@dataclass
class CostTracker:
    """Track API costs and usage."""

    # Pricing per 1M tokens
    pricing: Dict[str, float] = field(default_factory=lambda: {
        "text-embedding-3-small": 0.02,
        "text-embedding-3-large": 0.13,
        "text-embedding-ada-002": 0.10,
        "local": 0.0,

    })

    # Running totals
    total_tokens: int = 0
    total_cost: float = 0.0
    total_requests: int = 0

    # Per-model breakdown
    tokens_by_model: Dict[str, int] = field(default_factory=dict)
    cost_by_model: Dict[str, float] = field(default_factory=dict)

    def track_request(
            self,
            model_name: str,
            num_tokens: int
    ) -> float:
        """
        Track single API request.

        Args:
            model_name: OpenAI model used
            num_tokens: Number of tokens embedded

        Returns:
            Cost of this request in USD
        """
        # Calculate cost
        price_per_1m = self.pricing.get(model_name, 0.02)
        cost = (num_tokens / 1_000_000) * price_per_1m

        # Update totals
        self.total_tokens += num_tokens
        self.total_cost += cost
        self.total_requests += 1

        # Update per-model
        self.tokens_by_model[model_name] = \
            self.tokens_by_model.get(model_name, 0) + num_tokens
        self.cost_by_model[model_name] = \
            self.cost_by_model.get(model_name, 0.0) + cost

        return cost

    def get_summary(self) -> str:
        """Get formatted cost summary."""
        lines = [
            "=" * 50,
            "EMBEDDING COST SUMMARY",
            "=" * 50,
            f"Total Requests: {self.total_requests}",
            f"Total Tokens:   {self.total_tokens:,}",
            f"Total Cost:     ${self.total_cost:.6f}",
            "",
            "Per Model:"
        ]

        for model, tokens in self.tokens_by_model.items():
            cost = self.cost_by_model[model]
            lines.append(f"  {model}:")
            lines.append(f"    Tokens: {tokens:,}")
            lines.append(f"    Cost:   ${cost:.6f}")

        return "\n".join(lines)

    def reset(self):
        """Reset all counters."""
        self.total_tokens = 0
        self.total_cost = 0.0
        self.total_requests = 0
        self.tokens_by_model.clear()
        self.cost_by_model.clear()


# Global tracker instance
cost_tracker = CostTracker()