from __future__ import annotations

from typing import TypeVar

from hydra.utils import instantiate

T = TypeVar("T")


def instantiate_from_config(config: object) -> T:
    return instantiate(config)
