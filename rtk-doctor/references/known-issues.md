# RTK Known Issues

## `rtk find <existing-path>` reports `0 for '<path>'`

Symptom:

```bash
rtk find /some/existing/dir
# 0 for '/some/existing/dir'
```

Raw comparison:

```bash
find /some/existing/dir -maxdepth 2 -print
```

Root cause:

RTK 0.41.0 parses a single positional argument as RTK's pattern syntax, not as a native `find` search root. Any native find flag, such as `-maxdepth`, makes RTK parse the first argument as the path root.

Repair:

Install a wrapper that intercepts only:

```text
rtk find <one existing path>
```

and forwards it as:

```text
rtk.real find <path> -maxdepth 2
```

Verification:

```bash
rtk find /data/lcq/.codex/skills/teach
rtk find /data/lcq/.codex/skills/teach -maxdepth 2 -type f
find /data/lcq/.codex/skills/teach -maxdepth 2 -type f -print
```

## Wrapper created without executable bit

Symptom:

```text
Permission denied
```

Root cause:

Manual wrapper creation wrote `/data/lcq/.local/bin/rtk` without `chmod +x`.

Repair:

```bash
chmod +x /data/lcq/.local/bin/rtk
```

Verification:

```bash
rtk --version
```

## `rtk test <command with quoted args>` splits arguments

Symptom:

`rtk test python script.py --interface "key=value with spaces"` can split the quoted value and pass extra words as arguments.

Root cause:

`rtk test` is optimized for test-output filtering, not complex shell-like quoted argument preservation.

Repair:

For commands where argument fidelity matters while debugging `rtk`, use raw command execution or `rtk proxy <cmd>` if proxy preserves the exact argv shape needed.

Verification:

Compare the target command under raw execution and `rtk proxy`.

## `nl|sed` line snippets return unrelated git summaries

Symptom:

```text
nl -ba file | sed -n '120,150p'
# returns a compact git status/diff-style summary instead of the requested lines
```

RTK command:

```bash
rtk proxy bash -lc 'nl -ba "$1" | sed -n "120,150p"' _ file
```

Raw comparison:

```bash
nl -ba file | sed -n '120,150p'
```

Root cause:

Some tool layers classify `nl|sed` source-snippet output as compressible command output and replace it with an unrelated summary. This can affect both rtk-wrapped and raw pipelines, so it is not a normal RTK binary filter bug.

Repair:

Run `rtk-doctor.sh repair`. The managed wrapper bypasses `rtk.real` compression for direct `rtk nl ...` and `rtk sed ...` calls by executing system `nl`/`sed` directly. This preserves normal pipeline behavior for `rtk nl -ba file | rtk sed -n '120,150p'`. `RTK_DOCTOR_DIAG=1` also emits a diagnostic when the bypass is used.

For patching or debugging source snippets, CodeGraph file mode, `ctx_read` line ranges, `rtk read`, or another raw file reader are still safer than `nl|sed` pipelines through tool layers.

Verification:

```bash
/data/lcq/.codex/skills/rtk-doctor/scripts/rtk-doctor.sh check
```

The check covers:

```bash
rtk proxy bash -lc 'nl -ba "$1" | sed -n "2,4p"' _ file
rtk nl -ba file | sed -n '2,4p'
nl -ba file | rtk sed -n '2,4p'
rtk nl -ba file | rtk sed -n '2,4p'
```
