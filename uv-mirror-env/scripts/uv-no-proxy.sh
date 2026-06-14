#!/usr/bin/env bash
set -euo pipefail

MIRROR="${UV_MIRROR:-https://pypi.tuna.tsinghua.edu.cn/simple}"

exec env \
  -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY -u NO_PROXY \
  -u http_proxy -u https_proxy -u all_proxy -u no_proxy \
  UV_DEFAULT_INDEX="${UV_DEFAULT_INDEX:-$MIRROR}" \
  "$@"
