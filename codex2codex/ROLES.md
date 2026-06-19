# codex2codex Roles

Role definitions are managed in `roles/*.yaml`.

- Defaults, allowed efforts/context profiles, fallback routing, and global skill policy: `roles/_defaults.yaml`
- Worker roles: `roles/coding.yaml`, `roles/test.yaml`, `roles/review.yaml`, `roles/sa.yaml`, `roles/consult.yaml`
- Lead-only role: `roles/fullstack.yaml`
- Runtime loader: `scripts/roles.py`

Edit the YAML files, not this index. `scripts/roles.py` loads those files and exposes aliases, caps, effort, sandbox, context profile, role prompt text, preferred skills, and non-worker role guards to the rest of codex2codex.

`--profile role` is the wave default and resolves to each worker YAML `context_profile`. Role YAML may use `minimal`, `standard`, or `full`; `role` is only a CLI sentinel.
