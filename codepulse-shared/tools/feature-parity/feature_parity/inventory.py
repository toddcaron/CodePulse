"""Bounded, read-only repository traversal without following links."""

import hashlib
import os
import stat
from pathlib import Path

from pathspec import PathSpec

EXCLUDED_DIRECTORIES = frozenset({
    ".git", ".svn", ".hg", "bin", "obj", "node_modules", "packages",
    "dist", "build", "generated", "vendor", ".venv", "__pycache__",
})
SENSITIVE_SUFFIXES = frozenset({".pfx", ".p12", ".pem", ".key", ".cer", ".crt"})
LANGUAGES = {
    ".cs": "csharp", ".vb": "visual-basic", ".vue": "vue", ".js": "javascript",
    ".ts": "typescript", ".cfm": "coldfusion", ".cfc": "coldfusion",
    ".sql": "sql", ".json": "json", ".md": "markdown", ".txt": "text",
    ".html": "html", ".htm": "html",
}


class InventoryPolicyError(ValueError):
    pass


def source_root(source):
    root = Path(source).resolve(strict=True)
    if not root.is_dir():
        raise InventoryPolicyError("Finder source must be a local directory")
    return root


def is_sensitive(path):
    name = path.name.casefold()
    return (
        path.suffix.casefold() in SENSITIVE_SUFFIXES or name.startswith(".env")
        or name.startswith("appsettings") or name in {"web.config", "app.config"}
        or any(word in name for word in ("secret", "credential", "password", "token"))
    )


def is_link(path):
    attributes = getattr(path.lstat(), "st_file_attributes", 0)
    return path.is_symlink() or bool(attributes & getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0))


def inventory_repository(source, max_file_bytes=1024 * 1024, max_entries=20000, max_depth=64,
                         include_patterns=(), exclude_patterns=(), forbidden_patterns=()):
    root = source_root(source)
    includes = PathSpec.from_lines("gitwildmatch", include_patterns)
    excludes = PathSpec.from_lines("gitwildmatch", exclude_patterns)
    forbidden = PathSpec.from_lines("gitwildmatch", forbidden_patterns)
    records = []
    issues = []
    entry_count = 0

    def visit(directory, depth):
        nonlocal entry_count
        if depth > max_depth:
            issues.append("Directory depth limit reached")
            return
        try:
            with os.scandir(directory) as iterator:
                entries = []
                for entry in iterator:
                    entry_count += 1
                    if entry_count > max_entries:
                        raise InventoryPolicyError("Repository entry limit exceeded")
                    entries.append(Path(entry.path))
        except OSError:
            issues.append("An unreadable directory was not inventoried")
            return
        for path in sorted(entries, key=lambda item: item.name):
            location = path.relative_to(root).as_posix()
            record = {
                "path": location, "fileType": path.suffix.casefold(), "size": None,
                "language": LANGUAGES.get(path.suffix.casefold(), "unknown"),
                "contentHash": None, "adapter": "generic", "exclusionReason": None,
            }
            try:
                if is_link(path):
                    record["exclusionReason"] = "link-or-junction"
                    issues.append("Linked paths were excluded; their capabilities are unverified")
                elif not path.resolve(strict=True).is_relative_to(root):
                    raise InventoryPolicyError("Path escaped the authorized source root")
                elif forbidden.match_file(location + ("/" if path.is_dir() else "")):
                    record["exclusionReason"] = "forbidden-path-policy"
                elif excludes.match_file(location + ("/" if path.is_dir() else "")):
                    record["exclusionReason"] = "configured-exclusion"
                elif path.is_dir():
                    if path.name.casefold() in EXCLUDED_DIRECTORIES:
                        record["exclusionReason"] = "dependency-or-generated-directory"
                    else:
                        visit(path, depth + 1)
                        continue
                elif not path.is_file():
                    record["exclusionReason"] = "non-regular-file"
                elif is_sensitive(path):
                    record["exclusionReason"] = "sensitive-file-policy"
                elif path.name.casefold().endswith((".g.cs", ".g.i.cs", ".designer.cs", ".generated.cs")):
                    record["exclusionReason"] = "generated-file"
                elif path.name == "codepulse.config.json":
                    record["exclusionReason"] = "configuration-input"
                elif include_patterns and not includes.match_file(location):
                    record["exclusionReason"] = "outside-includes"
                else:
                    record["size"] = path.stat().st_size
                    if record["size"] > max_file_bytes:
                        record["exclusionReason"] = "file-size-limit"
                        issues.append("Oversized files were excluded")
                    else:
                        with path.open("rb") as handle:
                            content = handle.read(max_file_bytes + 1)
                        if len(content) > max_file_bytes:
                            record["exclusionReason"] = "file-size-limit"
                            issues.append("A file grew beyond the read limit")
                        else:
                            record["contentHash"] = hashlib.sha256(content).hexdigest()
                            if b"\x00" in content:
                                record["exclusionReason"] = "binary-file"
                            else:
                                try:
                                    content.decode("utf-8-sig")
                                except UnicodeError:
                                    record["exclusionReason"] = "unsupported-encoding"
                                    issues.append("Non-UTF-8 files were excluded")
            except OSError:
                record["exclusionReason"] = "unreadable-file"
                issues.append("An unreadable file was excluded")
            records.append(record)

    visit(root, 0)
    return sorted(records, key=lambda item: item["path"]), sorted(set(issues))