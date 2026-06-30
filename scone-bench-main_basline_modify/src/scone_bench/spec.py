import math
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Grade:
    subscores: dict
    weights: dict
    metadata: Optional[dict] = None

    @property
    def score(self) -> float:
        assert self.subscores.keys() == self.weights.keys(), (
            f"subscores keys {set(self.subscores)} != weights keys {set(self.weights)}"
        )
        assert math.isclose(sum(self.weights.values()), 1.0), f"weights sum to {sum(self.weights.values())}"
        assert min(self.subscores.values()) >= 0
        assert max(self.subscores.values()) <= 1

        score = sum(self.subscores[k] * self.weights[k] for k in self.subscores)
        assert 0 <= score <= 1
        return score

    @property
    def precision(self) -> float:
        return float(self.metadata.get("precision", "0.0")) if self.metadata else 0.0

    @property
    def recall(self) -> float:
        return float(self.metadata.get("recall", "0.0")) if self.metadata else 0.0

    @property
    def f1(self) -> float:
        return float(self.metadata.get("f1_score", "0.0")) if self.metadata else 0.0

    def to_dict(self) -> dict:
        return {
            "subscores": self.subscores,
            "weights": self.weights,
            "metadata": self.metadata,
            "score": self.score,
            "precision": self.precision,
            "recall": self.recall,
            "f1_score": self.f1,
        }
