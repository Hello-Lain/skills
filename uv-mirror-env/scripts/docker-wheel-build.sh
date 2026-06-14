#!/usr/bin/env bash
set -euo pipefail

IMAGE="docker.1ms.run/pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel"
PYTHON_TAG="cp311"
UV_CACHE_HOME="${UV_CACHE_DIR:-$HOME/.cache/uv}"
WHEELHOUSE="${UV_MIRROR_WHEELHOUSE:-$UV_CACHE_HOME/wheelhouse}"
MIRROR="${UV_MIRROR:-https://pypi.tuna.tsinghua.edu.cn/simple}"
USE_GPUS=1
BUILD_DEPS=0
PACKAGES=()

usage() {
  cat <<'EOF'
Usage:
  docker-wheel-build.sh [options] PACKAGE...

Options:
  --image IMAGE          Build image. Default: docker.1ms.run/pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel
  --python-tag TAG       Wheel ABI note only, e.g. cp311. Default: cp311
  --wheelhouse DIR       Output dir. Default: ${UV_CACHE_DIR:-$HOME/.cache/uv}/wheelhouse
  --mirror URL           PyPI mirror. Default: Tsinghua
  --gpus                 Expose GPUs to the build container. Default.
  --no-gpus              Do not pass --gpus all to Docker.
  --deps                 Allow pip to resolve package dependencies. Default: off.
  --no-deps              Build only requested packages. Default.

Example:
  docker-wheel-build.sh --image docker.1ms.run/pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel flash-attn==2.6.3
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --image) IMAGE="${2:-}"; shift 2 ;;
    --python-tag) PYTHON_TAG="${2:-}"; shift 2 ;;
    --wheelhouse) WHEELHOUSE="${2:-}"; shift 2 ;;
    --mirror) MIRROR="${2:-}"; shift 2 ;;
    --gpus) USE_GPUS=1; shift ;;
    --no-gpus) USE_GPUS=0; shift ;;
    --deps) BUILD_DEPS=1; shift ;;
    --no-deps) BUILD_DEPS=0; shift ;;
    -h|--help) usage; exit 0 ;;
    --) shift; break ;;
    -*) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
    *) PACKAGES+=("$1"); shift ;;
  esac
done

while [[ $# -gt 0 ]]; do
  PACKAGES+=("$1")
  shift
done

if [[ "${#PACKAGES[@]}" -eq 0 ]]; then
  usage >&2
  exit 2
fi

mkdir -p "$WHEELHOUSE" "$HOME/.cache/pip"

docker_cmd() {
  if docker info >/dev/null 2>&1; then
    env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u NO_PROXY \
      -u http_proxy -u https_proxy -u all_proxy -u no_proxy \
      docker "$@"
    return
  fi

  if command -v sg >/dev/null 2>&1 && sg docker -c 'docker info >/dev/null 2>&1'; then
    local quoted=()
    local arg
    local cmd
    for arg in "$@"; do
      quoted+=("$(printf '%q' "$arg")")
    done
    cmd="env -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u NO_PROXY -u http_proxy -u https_proxy -u all_proxy -u no_proxy docker ${quoted[*]}"
    sg docker -c "bash -lc $(printf '%q' "$cmd")"
    return
  fi

  echo "docker daemon unavailable; try adding current user to docker group or run through sg docker" >&2
  exit 13
}

pull_image() {
  local image="$1"
  if docker_cmd pull "$image"; then
    IMAGE="$image"
    return 0
  fi
  return 1
}

if ! pull_image "$IMAGE"; then
  image_tail="${IMAGE#*/}"
  fallbacks=(
    "docker.1ms.run/$image_tail"
    "docker.m.daocloud.io/$image_tail"
    "docker.1panel.live/$image_tail"
    "docker.xuanyuan.run/$image_tail"
  )
  pulled=0
  for fallback in "${fallbacks[@]}"; do
    [[ "$fallback" == "$IMAGE" ]] && continue
    echo "[docker-wheel-build] pull failed for $IMAGE; trying $fallback" >&2
    if pull_image "$fallback"; then
      pulled=1
      break
    fi
  done
  if [[ "$pulled" -ne 1 ]]; then
    echo "[docker-wheel-build] failed to pull any image mirror for $image_tail" >&2
    exit 14
  fi
fi

run_args=(run --rm)
if [[ "$USE_GPUS" -eq 1 ]]; then
  run_args+=(--gpus all -e NVIDIA_VISIBLE_DEVICES=all -e NVIDIA_DRIVER_CAPABILITIES=compute,utility)
fi

docker_cmd "${run_args[@]}" \
  -e "PIP_INDEX_URL=$MIRROR" \
  -e PIP_NO_CACHE_DIR=0 \
  -e "MAX_JOBS=${MAX_JOBS:-8}" \
  -e "NVCC_THREADS=${NVCC_THREADS:-4}" \
  -e "TORCH_CUDA_ARCH_LIST=${TORCH_CUDA_ARCH_LIST:-}" \
  -e CUDA_HOME="${CUDA_HOME:-/usr/local/cuda}" \
  -e "FLASH_ATTENTION_FORCE_BUILD=${FLASH_ATTENTION_FORCE_BUILD:-TRUE}" \
  -e "BUILD_DEPS=$BUILD_DEPS" \
  -e "HOST_UID=$(id -u)" \
  -e "HOST_GID=$(id -g)" \
  -e HTTP_PROXY= -e HTTPS_PROXY= -e ALL_PROXY= -e NO_PROXY= \
  -e http_proxy= -e https_proxy= -e all_proxy= -e no_proxy= \
  -v "$WHEELHOUSE:/wheelhouse" \
  -v "$HOME/.cache/pip:/root/.cache/pip" \
  "$IMAGE" \
  bash -lc '
    set -euo pipefail
    if command -v sed >/dev/null && [[ -f /etc/apt/sources.list ]]; then
      sed -i "s#http://archive.ubuntu.com/ubuntu/#https://mirrors.tuna.tsinghua.edu.cn/ubuntu/#g; s#http://security.ubuntu.com/ubuntu/#https://mirrors.tuna.tsinghua.edu.cn/ubuntu/#g" /etc/apt/sources.list || true
    fi
    if ! command -v git >/dev/null 2>&1 && command -v apt-get >/dev/null 2>&1; then
      export DEBIAN_FRONTEND=noninteractive
      apt-get update
      apt-get install -y --no-install-recommends git ca-certificates
      rm -rf /var/lib/apt/lists/*
    fi
    python -m pip install -U pip setuptools wheel ninja packaging -i "$PIP_INDEX_URL"
    deps_args=()
    if [[ "${BUILD_DEPS:-0}" != "1" ]]; then
      deps_args+=(--no-deps)
    fi
    python -m pip wheel --no-build-isolation "${deps_args[@]}" -w /wheelhouse "$@"
    chown -R "${HOST_UID}:${HOST_GID}" /wheelhouse || true
  ' bash "${PACKAGES[@]}"

echo "[docker-wheel-build] built wheels in $WHEELHOUSE for $PYTHON_TAG" >&2
