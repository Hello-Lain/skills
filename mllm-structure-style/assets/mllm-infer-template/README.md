# {{PROJECT_NAME}}

Hydra + torchrun + strategy-method MLLM inference template.

## Quick Start

```bash
uv sync
uv run torchrun --nproc_per_node=1 src/infer.py
uv run torchrun --nproc_per_node=2 src/infer.py
uv run torchrun --nproc_per_node=1 src/infer.py experiment=mock_smoke debug=default
uv run pytest -q
```

## Hydra Configs

The template uses composable Hydra config groups inspired by Lightning-Hydra, without adopting
Lightning Trainer or callbacks. Useful overrides:

```bash
uv run torchrun --nproc_per_node=1 src/infer.py experiment=mock_smoke
uv run torchrun --nproc_per_node=1 src/infer.py logger=jsonl tags='[paper_x,ablation]'
uv sync --extra tracking && uv run torchrun --nproc_per_node=1 src/infer.py logger=wandb
uv sync --extra sweeper && uv run python src/eval.py -m hparams_search=method_optuna
```

Copy `configs/local/default.yaml.example` to `configs/local/default.yaml` for machine-specific
paths or API endpoints. The real local config is ignored by git.

## Add A Method

1. Add `src/methods/paper_xyz.py` and inherit `BaseMethod`.
2. Add `configs/method/paper_xyz.yaml` with `_target_: methods.paper_xyz.PaperXyzMethod`.
3. Run:

```bash
uv run torchrun --nproc_per_node=2 src/infer.py method=paper_xyz
```

Do not modify `src/infer.py` for method-specific logic.

## Evaluate With VLMEvalKit

`src/eval.py` keeps evaluation separate from pure inference. VLMEvalKit handles benchmark
datasets, prompts, prediction files, and metrics; this project keeps model loading and method
logic under Hydra control.

The compatible dependency set is pinned in `pyproject.toml`:
`hydra-core==1.3.2`, `omegaconf==2.3.0`, `transformers>=4.41,<4.52`, and
`ms-vlmeval==0.0.19`.
Install the evaluation extra before running benchmarks:

```bash
uv sync --extra eval
```

Do not blindly upgrade to `ms-vlmeval==0.0.20`; it requires `omegaconf>=2.4.0.dev4`
and `antlr4-python3-runtime==4.11.1`, which conflicts with the stable Hydra 1.3 stack.
Do not upgrade to `transformers>=4.52` with `ms-vlmeval==0.0.19`; that VLMEvalKit
release still imports `AutoModelForVision2Seq`.

```bash
uv run torchrun --nproc_per_node=2 src/eval.py eval_tasks.datasets='[MMBench_DEV_EN]' model=hf
```

Use `OPENAI_API_KEY` or `eval_tasks.judge` only for benchmarks that require an LLM judge.
