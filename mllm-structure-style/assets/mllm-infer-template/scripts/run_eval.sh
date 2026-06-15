#!/usr/bin/env bash
set -euo pipefail

# Benchmarks that require LLM-as-judge need provider keys, for example:
# export OPENAI_API_KEY="sk-..."

NPROC_PER_NODE="${NPROC_PER_NODE:-2}"
uv run torchrun \
  --standalone \
  --nnodes=1 \
  --nproc_per_node="${NPROC_PER_NODE}" \
  src/eval.py "$@"
