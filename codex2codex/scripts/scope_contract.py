#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path, PurePosixPath


def normalize_contract_path(path_text: str, repo_root: Path | None = None) -> str:
    text = path_text.strip()
    if "\t" in text:
        text = text.split("\t", 1)[0].strip()
    if text in {"/dev/null", "dev/null"}:
        return ""
    if text.startswith(("a/", "b/")):
        text = text[2:]
    path = Path(text)
    if repo_root is not None:
        try:
            if path.is_absolute():
                path = path.resolve().relative_to(repo_root.resolve())
                text = path.as_posix()
        except (OSError, ValueError):
            pass
    if "\\" in text:
        raise ValueError(f"path uses backslashes: `{text}`")
    posix = PurePosixPath(text)
    if posix.is_absolute():
        raise ValueError(f"path is absolute: `{text}`")
    if ".." in posix.parts:
        raise ValueError(f"path uses path traversal: `{text}`")
    parts = [part for part in posix.parts if part and part != "."]
    return PurePosixPath(*parts).as_posix() if parts else ""


def scope_entries(repo_root: Path, raw_scope: list[str]) -> tuple[tuple[str, bool], ...]:
    entries: list[tuple[str, bool]] = []
    seen: set[tuple[str, bool]] = set()
    for raw_path in raw_scope:
        explicit_dir = raw_path.strip().endswith("/")
        scope = normalize_contract_path(raw_path, repo_root)
        allow_child = explicit_dir or (repo_root / scope).is_dir()
        entry = (scope, allow_child)
        if scope and entry not in seen:
            entries.append(entry)
            seen.add(entry)
    return tuple(entries)


def path_in_scope(path_text: str, entries: tuple[tuple[str, bool], ...], repo_root: Path) -> bool:
    path = normalize_contract_path(path_text, repo_root).rstrip("/")
    return any(
        path == scope.rstrip("/") or (allow_child and path.startswith(scope.rstrip("/") + "/"))
        for scope, allow_child in entries
    )
