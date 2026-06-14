#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${1:-$SCRIPT_DIR/../datasets/coco2014}"

mkdir -p "$DATA_DIR"

extract_if_missing() {
  local archive="$1"
  local marker="$2"
  if [[ -e "$DATA_DIR/$marker" ]]; then
    printf 'skip extract: %s\n' "$archive"
    return
  fi
  unzip -q "$DATA_DIR/$archive" -d "$DATA_DIR"
}

"$SCRIPT_DIR/hf-download.sh" \
  --mirror \
  --repo-id "GAIA-URJC/COCO_2014" \
  --repo-type dataset \
  --local-dir "$DATA_DIR" \
  "annotations_trainval2014.zip" \
  "train2014.zip" \
  "val2014.zip"

extract_if_missing "annotations_trainval2014.zip" "annotations"
extract_if_missing "train2014.zip" "train2014"
extract_if_missing "val2014.zip" "val2014"

printf 'COCO 2014 is ready under: %s\n' "$DATA_DIR"
