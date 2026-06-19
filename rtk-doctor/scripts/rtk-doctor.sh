#!/usr/bin/env bash
set -euo pipefail

cmd="${1:-check}"
shift || true
rtk_bin="${RTK_BIN:-$(command -v rtk 2>/dev/null || true)}"
skill_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
known_issues="$skill_dir/references/known-issues.md"

die() {
  printf 'ERROR: %s\n' "$*" >&2
  exit 1
}

info() {
  printf '%s\n' "$*"
}

is_wrapper() {
  [[ -n "${rtk_bin:-}" ]] && [[ -f "$rtk_bin" ]] && grep -Eq 'RTK_DOCTOR_WRAPPER|^rtk_real=' "$rtk_bin" 2>/dev/null
}

real_bin() {
  if [[ -n "${RTK_REAL:-}" ]]; then
    printf '%s\n' "$RTK_REAL"
    return
  fi
  if is_wrapper; then
    local line value
    line="$(awk '/^rtk_real=/{print; exit}' "$rtk_bin")"
    value="${line#rtk_real=}"
    value="${value%\"}"
    value="${value#\"}"
    if [[ "$value" == '${RTK_REAL:-'*'}' ]]; then
      value="${value#\$\{RTK_REAL:-}"
      value="${value%\}}"
    fi
    printf '%s\n' "$value"
    return
  fi
  printf '%s.real\n' "$rtk_bin"
}

ensure_rtk() {
  [[ -n "${rtk_bin:-}" ]] || die "rtk not found on PATH"
  [[ -e "$rtk_bin" ]] || die "rtk path does not exist: $rtk_bin"
}

make_fixture() {
  fixture="$(mktemp -d)"
  mkdir -p "$fixture/dir"
  printf 'alpha\n' > "$fixture/dir/a.txt"
  printf 'beta\n' > "$fixture/dir/b.md"
  printf '%s\n' "$fixture"
}

check_find_path() {
  local fixture raw_count rtk_out
  fixture="$(make_fixture)"
  raw_count="$(find "$fixture/dir" -maxdepth 2 -type f -print | wc -l | tr -d ' ')"
  rtk_out="$("$rtk_bin" find "$fixture/dir" 2>&1 || true)"
  rm -rf "$fixture"

  if [[ "$rtk_out" == 0\ for\ * ]]; then
    info "FAIL find-existing-path: rtk treated path as pattern"
    return 1
  fi
  if [[ "$raw_count" != "2" ]]; then
    info "FAIL fixture: raw find expected 2 files, got $raw_count"
    return 1
  fi
  info "PASS find-existing-path"
}

looks_like_git_summary() {
  local output="$1"
  [[ "$output" == *"Modified:"* ]] && return 0
  [[ "$output" == *"Untracked:"* ]] && return 0
  [[ "$output" == *"git status"* ]] && return 0
  [[ "$output" == *"Changes not staged"* ]] && return 0
  return 1
}

line_snippet_advice() {
  info "DIAG line-snippet-reader: avoid nl|sed pipelines through rtk/tool filters for source snippets; prefer CodeGraph file mode, ctx_read lines:N-M, or another raw file reader."
}

check_line_snippet_pipeline() {
  local fixture file raw_out rtk_proxy_out rtk_nl_out rtk_sed_out rtk_both_out
  fixture="$(mktemp -d)"
  file="$fixture/snippet.txt"
  cat > "$file" <<'EOF'
rtk-doctor-line-01
rtk-doctor-line-02
rtk-doctor-line-03
rtk-doctor-line-04
rtk-doctor-line-05
EOF

  raw_out="$(nl -ba "$file" | sed -n '2,4p' 2>&1 || true)"
  rtk_proxy_out="$("$rtk_bin" proxy bash -lc 'nl -ba "$1" | sed -n "2,4p"' _ "$file" 2>&1 || true)"
  rtk_nl_out="$("$rtk_bin" nl -ba "$file" 2>&1 | sed -n '2,4p' 2>&1 || true)"
  rtk_sed_out="$(nl -ba "$file" 2>&1 | "$rtk_bin" sed -n '2,4p' 2>&1 || true)"
  rtk_both_out="$("$rtk_bin" nl -ba "$file" 2>&1 | "$rtk_bin" sed -n '2,4p' 2>&1 || true)"
  rm -rf "$fixture"

  if [[ "$raw_out" != *"rtk-doctor-line-02"* || "$raw_out" != *"rtk-doctor-line-04"* ]]; then
    info "FAIL line-snippet-pipeline: raw nl|sed did not return sentinel lines"
    line_snippet_advice
    return 1
  fi
  check_snippet_output "rtk proxy nl|sed" "$rtk_proxy_out" || return 1
  check_snippet_output "rtk nl | sed" "$rtk_nl_out" || return 1
  check_snippet_output "nl | rtk sed" "$rtk_sed_out" || return 1
  check_snippet_output "rtk nl | rtk sed" "$rtk_both_out" || return 1
  info "PASS line-snippet-pipeline"
}

check_snippet_output() {
  local label output
  label="$1"
  output="$2"
  if looks_like_git_summary "$output" && [[ "$output" != *"rtk-doctor-line-02"* ]]; then
    info "FAIL line-snippet-pipeline: $label returned unrelated git summary"
    line_snippet_advice
    return 1
  fi
  if [[ "$output" != *"rtk-doctor-line-02"* || "$output" != *"rtk-doctor-line-04"* ]]; then
    info "FAIL line-snippet-pipeline: $label did not return sentinel lines"
    line_snippet_advice
    return 1
  fi
}

check_exec() {
  if [[ ! -x "$rtk_bin" ]]; then
    info "FAIL executable-bit: $rtk_bin is not executable"
    return 1
  fi
  "$rtk_bin" --version >/dev/null 2>&1 || {
    info "FAIL version: rtk --version failed"
    return 1
  }
  info "PASS executable-version"
}

check_wrapper() {
  if is_wrapper; then
    local rb
    rb="$(real_bin)"
    if [[ -x "$rb" ]]; then
      info "PASS wrapper: $rtk_bin -> $rb"
    else
      info "FAIL wrapper-real: missing/non-executable $rb"
      return 1
    fi
  else
    info "INFO wrapper: not installed"
  fi
}

write_wrapper() {
  local rb
  rb="$(real_bin)"

  if is_wrapper; then
    [[ -x "$rb" ]] || die "wrapper exists but real binary is missing/non-executable: $rb"
    cp "$rtk_bin" "$rtk_bin.bak"
    info "repair: refreshing existing wrapper; backup=$rtk_bin.bak"
  else
    [[ -f "$rtk_bin" ]] || die "cannot wrap missing file: $rtk_bin"
    [[ ! -e "$rb" ]] || die "refusing to overwrite existing real binary: $rb"
    mv "$rtk_bin" "$rb"
  fi
  cat > "$rtk_bin" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail

# RTK_DOCTOR_WRAPPER
rtk_real="${RTK_REAL:-__RTK_REAL__}"

if [[ "${1:-}" == "find" ]]; then
  shift
  has_native_flag=0
  for arg in "$@"; do
    case "$arg" in
      -*) has_native_flag=1 ;;
    esac
  done

  if [[ $has_native_flag -eq 0 && $# -eq 1 && -e "$1" ]]; then
    exec "$rtk_real" find "$1" -maxdepth 2
  fi

  exec "$rtk_real" find "$@"
fi

if [[ "${1:-}" == "test" ]]; then
  shift
  for arg in "$@"; do
    case "$arg" in
      *' '*|*'='*)
        exec "$rtk_real" proxy "$@"
        ;;
    esac
  done
  exec "$rtk_real" test "$@"
fi

case "${1:-}" in
  nl|sed)
    cmd="$1"
    shift
    system_cmd="$(command -v "$cmd" 2>/dev/null || true)"
    [[ -n "$system_cmd" ]] || {
      printf 'ERROR: %s not found on PATH\n' "$cmd" >&2
      exit 127
    }
    if [[ "${RTK_DOCTOR_DIAG:-0}" == "1" ]]; then
      printf '%s\n' "DIAG line-snippet-reader: rtk doctor is bypassing rtk compression for $cmd and executing $system_cmd directly." >&2
    fi
    exec "$system_cmd" "$@"
    ;;
esac

if [[ "${RTK_DOCTOR_DIAG:-0}" == "1" ]]; then
  case "${1:-}" in
    nl|sed)
      printf '%s\n' "DIAG line-snippet-reader: prefer CodeGraph file mode, ctx_read lines:N-M, or another raw file reader for source snippets." >&2
      ;;
  esac
fi

exec "$rtk_real" "$@"
EOF
  sed -i "s#__RTK_REAL__#$rb#g" "$rtk_bin"
  chmod +x "$rtk_bin"
  info "repair: installed wrapper $rtk_bin -> $rb"
}

run_check() {
  ensure_rtk
  info "rtk_bin=$rtk_bin"
  "$rtk_bin" --version 2>/dev/null || true
  check_exec
  check_wrapper
  check_find_path
  check_line_snippet_pipeline
}

run_repair() {
  ensure_rtk
  if [[ ! -x "$rtk_bin" ]]; then
    chmod +x "$rtk_bin"
    info "repair: chmod +x $rtk_bin"
  fi
  if is_wrapper; then
    write_wrapper
  elif ! check_find_path >/dev/null 2>&1; then
    write_wrapper
  else
    info "repair: find-existing-path already healthy"
  fi
  run_check
}

run_record() {
  local title symptom command raw root repair verification
  title="${1:-}"
  [[ -n "$title" ]] || die "usage: $0 record <title> [symptom] [rtk-command] [raw-command] [root-cause] [repair] [verification]"
  symptom="${2:-TBD}"
  command="${3:-TBD}"
  raw="${4:-TBD}"
  root="${5:-TBD}"
  repair="${6:-TBD}"
  verification="${7:-TBD}"

  cat >> "$known_issues" <<EOF

## $title

Symptom:

\`\`\`text
$symptom
\`\`\`

RTK command:

\`\`\`bash
$command
\`\`\`

Raw comparison:

\`\`\`bash
$raw
\`\`\`

Root cause:

$root

Repair:

$repair

Verification:

\`\`\`bash
$verification
\`\`\`
EOF
  info "recorded: $known_issues"
}

case "$cmd" in
  check) run_check ;;
  repair) run_repair ;;
  record) run_record "$@" ;;
  *) die "usage: $0 check|repair|record" ;;
esac
