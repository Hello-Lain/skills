from __future__ import annotations

from unittest.mock import MagicMock, patch

import torch

from models.hf import HFMLLMWrapper


def test_hf_wrapper_uses_lazy_low_memory_loading_and_to_device() -> None:
    model = MagicMock()
    model.to.return_value = model
    device = torch.device("cpu")
    wrapper = HFMLLMWrapper(
        path="~/tmp/nonexistent-model",
        torch_dtype="bfloat16",
        attn_implementation="flash_attention_2",
        low_cpu_mem_usage=True,
        device_map=None,
        trust_remote_code=True,
    )

    with (
        patch("models.hf.AutoProcessor.from_pretrained") as processor_loader,
        patch("models.hf.AutoModelForCausalLM.from_pretrained", return_value=model) as model_loader,
    ):
        wrapper.setup(device)

    processor_loader.assert_called_once_with(
        "~/tmp/nonexistent-model",
        trust_remote_code=True,
    )
    model_loader.assert_called_once_with(
        "~/tmp/nonexistent-model",
        torch_dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
        low_cpu_mem_usage=True,
        device_map=None,
        trust_remote_code=True,
    )
    model.to.assert_called_once_with(device)
    model.eval.assert_called_once_with()


def test_hf_wrapper_rejects_unknown_dtype() -> None:
    try:
        HFMLLMWrapper(
            path="~/tmp/nonexistent-model",
            torch_dtype="int8",
            attn_implementation="flash_attention_2",
            low_cpu_mem_usage=True,
            device_map=None,
            trust_remote_code=True,
        )
    except ValueError as exc:
        assert "Unsupported torch_dtype" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported dtype.")
