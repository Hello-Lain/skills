from __future__ import annotations

import torch

from methods.standard import StandardInferMethod
from models.mock import MockMLLMWrapper


def test_standard_method_contract() -> None:
    device = torch.device("cpu")
    model = MockMLLMWrapper(
        path="mock://mllm",
        dtype="bfloat16",
        attn_implementation="flash_attention_2",
        low_cpu_mem_usage=True,
    )
    method = StandardInferMethod(max_new_tokens=8, temperature=0.0)

    model.setup(device)
    method.setup(model, device)
    outputs = method.generate(
        {
            "records": [
                {
                    "id": "sample-001",
                    "image_path": "mock://image-001",
                    "prompt": "Describe the scene.",
                }
            ]
        }
    )

    assert outputs[0]["id"] == "sample-001"
    assert outputs[0]["method"] == "StandardInferMethod"
    assert "mock_response" in outputs[0]["prediction"]
