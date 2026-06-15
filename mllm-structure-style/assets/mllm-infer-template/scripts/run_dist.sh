#!/usr/bin/env bash
set -euo pipefail

NPROC_PER_NODE="${NPROC_PER_NODE:-2}"
uv run torchrun --nproc_per_node="${NPROC_PER_NODE}" src/infer.py "$@"
