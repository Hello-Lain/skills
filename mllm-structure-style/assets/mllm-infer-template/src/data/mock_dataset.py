from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

from torch.utils.data import Dataset


class MockDataset(Dataset[dict[str, Any]]):
    """Return raw records only; no tokenizer or processor work belongs here."""

    def __init__(self, samples: Sequence[Mapping[str, Any]]) -> None:
        self._samples = [dict(sample) for sample in samples]

    def __len__(self) -> int:
        return len(self._samples)

    def __getitem__(self, index: int) -> dict[str, Any]:
        return dict(self._samples[index])
