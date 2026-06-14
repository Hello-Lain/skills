---
name: uv-mirror-env
description: Use when creating, repairing, syncing, or managing Python environments with uv in no-proxy or VPN-saving networks; use domestic PyPI mirrors, prefer existing compatible uv cache hits for large dependencies such as torch, torchvision, xformers, triton, opencv, decord, vllm, flash-attn, and build special binary packages in one-shot Docker containers using domestic Docker/image/package mirrors.
---

# uv Mirror Env

Use this skill for Python env work when proxy/VPN traffic should be avoided.

## Defaults

- Disable proxy env for every network command.
- Prefer uv cache before downloading large wheels.
- Use a domestic PyPI mirror unless the user requests another source.
- Do not use floating git deps when a compatible PyPI wheel exists.
- Do not delete caches unless explicitly requested.
- For Hugging Face downloads, combine with `huggingface-local-cache`; this skill does not download model weights.
- When running project code, use the project's uv-managed `.venv` by default. Activate it first, or invoke `.venv/bin/python` directly; never fall back to system Python unless explicitly requested.

Default PyPI mirror:

```bash
UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple
```

Common fallback mirrors:

```text
https://mirrors.aliyun.com/pypi/simple
https://pypi.mirrors.ustc.edu.cn/simple
https://mirrors.cloud.tencent.com/pypi/simple
```

## Core Workflow

1. Stop stale downloads/installers before changing env state.
2. Reuse `.venv` if healthy; recreate only if broken or the user asks for clean state.
3. Install large deps by exact compatible pins first, with `--offline` dry/cache hit attempt.
4. If offline fails, install using no-proxy env + mirror.
5. Avoid repo requirements lines such as `git+https://...` unless the project truly needs source-only code.
6. Validate with imports and `uv pip check`.
7. Run project scripts/tests from the same `.venv` used for dependency install.

## Runtime Execution Policy

Before executing Python project code, prefer activating the local uv environment:

```bash
source .venv/bin/activate
python <script-or-module>
```

For one-shot commands, direct invocation is also acceptable:

```bash
.venv/bin/python <script-or-module>
```

Use the same rule for tests, CLIs, notebooks launched from shell, and project validation commands:

```bash
source .venv/bin/activate
pytest
python -m <module>
```

If `.venv` is missing, create or sync it with uv before running project code. If `.venv` exists but commands still resolve to system Python, stop and fix activation/pathing instead of continuing.

## Scripts

Use wrappers when practical:

```bash
./scripts/uv-no-proxy.sh venv --python <python> .venv
./scripts/uv-no-proxy.sh pip install --python .venv/bin/python torch==2.4.0 torchvision==0.19.0 --torch-backend cu121
```

Cache-first install:

```bash
./scripts/uv-cache-first-install.sh \
  --python .venv/bin/python \
  --torch-backend cu121 \
  torch==2.4.0 torchvision==0.19.0 transformers==4.45.2
```

One-shot Docker wheel build:

```bash
./scripts/docker-wheel-build.sh \
  --image docker.1ms.run/pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel \
  --python-tag cp311 \
  flash-attn==2.6.3
```

`--gpus all` is enabled by default for CUDA extension builds. Use `--no-gpus` only when Docker lacks NVIDIA runtime or the package is compile-only and does not need visible devices.

Dependency resolution is disabled by default (`--no-deps`) so packages such as `flash-attn` do not pull a different `torch`/CUDA stack. Use `--deps` only for ordinary packages where dependency wheels are desired.

For H100/A100 builds, limit arch targets to reduce compile time and wheel size:

```bash
TORCH_CUDA_ARCH_LIST=9.0 MAX_JOBS=16 NVCC_THREADS=4 \
  ./scripts/docker-wheel-build.sh flash-attn==2.6.1
```

Default wheel output is under uv's default cache:

```text
${UV_CACHE_DIR:-$HOME/.cache/uv}/wheelhouse
```

Then install built wheels:

```bash
./scripts/uv-no-proxy.sh pip install \
  --python .venv/bin/python \
  --find-links wheelhouse \
  flash-attn==2.6.3
```

## Large Dependency Policy

Pin large packages explicitly:

```bash
torch==2.4.0 torchvision==0.19.0 --torch-backend cu121
transformers==4.45.2
```

For GPU stacks, match these before install/build:

- Python ABI, e.g. `cp311`.
- CUDA runtime, e.g. `cu121`.
- Torch version.
- GCC/CUDA build image.
- Package version constraints from upstream docs or project README.

Try existing cache first:

```bash
uv pip install --offline --python .venv/bin/python <pins>
```

If cache miss, use mirror:

```bash
env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u NO_PROXY \
    -u http_proxy -u https_proxy -u all_proxy -u no_proxy \
    UV_DEFAULT_INDEX=https://pypi.tuna.tsinghua.edu.cn/simple \
    uv pip install --python .venv/bin/python <pins>
```

## Docker Build Policy

Use Docker only for packages that need local binary compilation or have fragile ABI coupling, e.g.:

- `flash-attn`
- custom CUDA extensions
- `xformers` source builds
- packages requiring exact torch/CUDA headers

Docker rules:

- Pull from domestic registry mirrors when possible. Default is `docker.1ms.run/...`; script also tries `docker.m.daocloud.io`, `docker.1panel.live`, and `docker.xuanyuan.run` fallbacks. Some mirrors, such as Xuanyuan, may require `docker login`.
- Use `docker` directly when the current user has socket access; otherwise try `sg docker -c ...`.
- Pass `--gpus all` by default; allow `--no-gpus` as an explicit fallback.
- Mount `${UV_CACHE_DIR:-$HOME/.cache/uv}/wheelhouse` for outputs unless overridden.
- Mount uv/pip cache read-write for reuse.
- Disable proxy env inside the container unless user asks otherwise.
- Use domestic apt/pip mirrors in the container; install `git ca-certificates` when source builds need them.
- Build a wheel, then install that wheel into `.venv`; do not compile repeatedly inside the runtime env.
- Build with `--no-deps` by default for ABI-sensitive CUDA packages; the build image supplies the compatible `torch`/CUDA headers.
- Chown generated wheels back to the host user so Docker root does not poison uv cache permissions.

## Validation

Always run:

```bash
uv pip check --python .venv/bin/python
.venv/bin/python - <<'PY'
import torch
print(torch.__version__, torch.cuda.is_available())
PY
```

For project-specific packages, import the exact symbols required by the app.

## Safety

- Never run `pip install` into system Python unless explicitly requested.
- Never pass secrets/tokens in CLI args.
- Do not remove `.venv`, uv cache, pip cache, Docker images, or wheelhouse without confirming unless the user explicitly asked for a clean rebuild.
- If a model/dataset download starts accidentally, stop it when the user asked for env-only work.
