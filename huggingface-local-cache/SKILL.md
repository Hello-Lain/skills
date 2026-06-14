---
name: huggingface-local-cache
description: Use for Hugging Face, huggingface, hugeface, hf, HF Hub, model weights, dataset downloads, local model loading, local dataset loading, cache management, hf mirror downloads, aria2 acceleration, transformers, diffusers, datasets, sentence-transformers, huggingface_hub, timm, or any code/docs/commands that download, cache, load, or search Hugging Face models or datasets. Always enforce model weights and dataset downloads under the configured Hugging Face cache root unless the user explicitly requests another location.
---

# Hugging Face Local Cache

Use this skill whenever a task touches Hugging Face models, datasets, weights, mirrors, cache paths, or local loading.

## Hard Defaults

All Hugging Face model and dataset downloads default to:

```text
${HF_CACHE_ROOT:-../../../.cache/huggingface}/hub
```

Set these env vars before `hf`, `huggingface_hub`, `transformers`, `diffusers`, `datasets`, `sentence-transformers`, `timm`, or related tools:

```bash
export HF_HOME="${HF_CACHE_ROOT:-../../../.cache/huggingface}"
export HF_HUB_CACHE="$HF_HOME/hub"
export HUGGINGFACE_HUB_CACHE="$HF_HOME/hub"
export HF_DATASETS_CACHE="$HF_HOME/hub"
export HF_DATASETS_DOWNLOADED_DATASETS_PATH="$HF_HOME/hub"
export DATASETS_ROOT="$HF_HOME/hub"
```

Prefer local cache first:

```python
cache_dir = "../../../.cache/huggingface/hub"
local_files_only = True
```

Fallback to network only when the cache is missing and the task requires download.

## Commands

Use bundled scripts when practical:

```bash
./scripts/hf-env.sh env
./scripts/hf-download.sh --repo-id Qwen/Qwen2.5-7B-Instruct
./scripts/hf-download.sh --repo-id GAIA-URJC/COCO_2014 --repo-type dataset
```

Before downloading, `hf-download.sh` runs a tool self-check:

```text
python, curl, hf, aria2c
```

If a required tool is missing, it installs automatically in this order:

```text
conda install -c conda-forge ...
python -m pip install -U ...
pip install -U ...
```

If installation still fails, it stops with a clear error instead of silently falling back to a slower or incompatible path.

`hf-download.sh` writes the standard Hugging Face cache layout directly:

```text
models--owner--repo/
  blobs/<etag-or-lfs-sha256>
  refs/<revision>
  snapshots/<commit-sha>/<filename> -> ../../blobs/<etag-or-lfs-sha256>
```

Files >= 100 MiB use bundled `aria2c` with 16 splits by default, while small files use `curl`.
This keeps `huggingface_hub`, `transformers`, and later `hf download` cache hits compatible.

By default `hf-download.sh` benchmarks source/proxy combinations before download:

```text
official + no proxy
mirror + no proxy
official + keep proxy  # only if proxy env exists
mirror + keep proxy    # only if proxy env exists
```

It selects the fastest reachable combination for the current repo/file, then downloads into the configured Hugging Face hub cache.

Default policy is `save-vpn`: direct official/mirror first, proxy/VPN only after direct download fails. All retries use the same HF cache, so partial files continue rather than restart.

For large models on VPN-limited networks:

```bash
./scripts/hf-download.sh \
  --network-policy save-vpn \
  --repo-id Qwen/Qwen2.5-VL-7B-Instruct
```

Policies:

- `fastest`: choose the fastest path, even if it uses proxy/VPN.
- `save-vpn`: try no-proxy official/mirror first; use proxy only after direct download fails.
- `no-vpn`: never use proxy/VPN; fail if direct official/mirror cannot download.

Set a global default for this shell:

```bash
export HF_DOWNLOAD_NETWORK_POLICY=save-vpn
```

Force a source only when the user explicitly asks:

```bash
./scripts/hf-download.sh \
  --source mirror \
  --repo-id GAIA-URJC/COCO_2014 \
  --repo-type dataset \
  annotations_trainval2014.zip train2014.zip val2014.zip
```

Force proxy behavior only when explicitly needed:

```bash
./scripts/hf-download.sh \
  --proxy-mode keep \
  --repo-id Qwen/Qwen2.5-7B-Instruct
```

Use local-dir only when the user explicitly wants a materialized copy outside the Hub cache:

```bash
./scripts/hf-download.sh \
  --repo-id GAIA-URJC/COCO_2014 \
  --repo-type dataset \
  --local-dir ../../../datasets/coco2014 \
  annotations_trainval2014.zip
```

## Python Patterns

For `huggingface_hub`:

```python
from huggingface_hub import snapshot_download

path = snapshot_download(
    repo_id="Qwen/Qwen2.5-7B-Instruct",
    repo_type="model",
    cache_dir="../../../.cache/huggingface/hub",
    local_files_only=True,
)
```

For `transformers`:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

cache_dir = "../../../.cache/huggingface/hub"
model_id = "Qwen/Qwen2.5-7B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_id, cache_dir=cache_dir, local_files_only=True)
model = AutoModelForCausalLM.from_pretrained(model_id, cache_dir=cache_dir, local_files_only=True)
```

For `datasets`:

```python
from datasets import load_dataset

dataset = load_dataset(
    "GAIA-URJC/COCO_2014",
    cache_dir="../../../.cache/huggingface/hub",
)
```

## Safety

- Do not place model weights or dataset archives inside random project folders unless the user explicitly requests a materialized copy.
- Do not pass tokens on the command line; prefer `HF_TOKEN`.
- For gated/private repos, check `hf auth whoami` without printing tokens.
- Before network download, benchmark official vs mirror and proxy vs no-proxy unless the user pins one.
- For large weights under VPN traffic limits, default to `--network-policy save-vpn`; use `--network-policy no-vpn` only when VPN traffic must be zero.
- For mirrors, keep cache paths unchanged; only set `HF_ENDPOINT`.
- For destructive cache actions (`hf cache rm`, prune, delete), require explicit user confirmation.

## Completion Check

- `HF_HOME`, `HF_HUB_CACHE`, `HUGGINGFACE_HUB_CACHE`, `HF_DATASETS_CACHE`, `HF_DATASETS_DOWNLOADED_DATASETS_PATH`, and `DATASETS_ROOT` point to the configured Hugging Face cache root or parent where applicable.
- `hf download` uses `--cache-dir "$HF_HUB_CACHE"`.
- Large model files are downloaded with `aria2c` into HF-compatible `blobs/` and `snapshots/` cache paths.
- The selected official/mirror + proxy/no-proxy path is visible in command output.
- Python code passes the configured hub cache path where supported.
- Existing local cache is checked before network download when practical.
- Docs/examples do not introduce conflicting cache roots.
