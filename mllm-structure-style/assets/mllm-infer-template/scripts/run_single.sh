#!/usr/bin/env bash
set -euo pipefail

uv run torchrun --nproc_per_node=1 src/infer.py "$@"
