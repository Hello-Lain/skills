# Validation Scenarios

Required scenario gates:

1. Python semantic edit -> `ast-grep`
2. JS/TS migration -> `jscodeshift`
3. JSON key/value update -> `jq`
4. YAML path update -> `yq`
5. Markdown section rewrite -> `remark`
6. Tiny unique prose fix -> strict text fallback allowed
7. Required structural tool missing -> policy remains `BLOCK`
8. Java migration without valid OpenRewrite context -> `BLOCK`
9. Generated file mutation -> generator-owned route
10. Old `edit-orchestration` invocation -> compatibility shell redirect

Validation commands:

```bash
python3 structural-edit/scripts/validate_structural_routes.py
python3 structural-edit/scripts/self_check_structural_tools.py --tool ast-grep --json
python3 structural-edit/scripts/prepare_structural_tools.py --list
python3 structural-edit/scripts/manifest_report.py --summary
```
