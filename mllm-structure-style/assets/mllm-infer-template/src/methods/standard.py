from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import torch

from methods.base_method import BaseMethod
from models.base import BaseMLLMWrapper


class StandardInferMethod(BaseMethod):
    """Default autoregressive-style method contract using the model wrapper API."""

    def __init__(self, max_new_tokens: int, temperature: float) -> None:
        self.max_new_tokens = max_new_tokens
        self.temperature = temperature
        self.model: BaseMLLMWrapper | None = None
        self.device: torch.device | None = None

    def setup(self, model: BaseMLLMWrapper, device: torch.device) -> None:
        self.model = model
        self.device = device

    def generate(self, batch: Mapping[str, Any]) -> list[dict[str, Any]]:
        if self.model is None or self.device is None:
            raise RuntimeError("StandardInferMethod.setup(model, device) must be called first.")

        records = batch.get("records")
        if not isinstance(records, list):
            raise TypeError("Batch must contain a list under key 'records'.")

        outputs: list[dict[str, Any]] = []
        for record in records:
            if not isinstance(record, dict):
                raise TypeError("Each batch record must be a dict.")
            prompt = str(record["prompt"])
            image_path = record.get("image_path")
            response = self.model.generate_response(
                prompt=prompt,
                image_path=str(image_path) if image_path is not None else None,
            )
            outputs.append(
                {
                    "id": record["id"],
                    "prompt": prompt,
                    "prediction": response,
                    "method": self.__class__.__name__,
                    "max_new_tokens": self.max_new_tokens,
                    "temperature": self.temperature,
                }
            )
        return outputs
