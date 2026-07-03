#!/usr/bin/env python
"""Normalize imports across the repository to use the canonical `backend.apps.*` namespace.

This script walks through all `.py` files (excluding migrations) and rewrites import statements
that do not already start with `backend.apps.`. It handles:
- Absolute imports like `from organizations.models import X`
- Legacy `apps.` imports like `from backend.apps.organizations.models import X`
- Relative imports (e.g. `from ..models import X`)

It uses `libcst` for safe, syntax‑preserving transformations.
"""

import pathlib

import libcst as cst

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
BACKEND_APPS_ROOT = REPO_ROOT / "backend" / "apps"

def is_standard_lib(module: str) -> bool:
    # Very small heuristic – treat anything without a dot as possible stdlib
    return "." not in module and not module.startswith("backend")

class ImportNormalizer(cst.CSTTransformer):
    def __init__(self, file_path: pathlib.Path):
        self.file_path = file_path
        relative = file_path.relative_to(REPO_ROOT)
        parts = list(relative.parts)
        parts.pop()  # remove filename
        if parts[:2] == ["backend", "apps"]:
            self.package_prefix = "backend.apps"
            if len(parts) > 2:
                self.package_prefix += "." + ".".join(parts[2:])
        else:
            self.package_prefix = ""

    def _make_absolute(self, module: str, level: int) -> str:
        pkg_parts = self.package_prefix.split(".")
        if level > 0:
            pkg_parts = pkg_parts[:-level]
        if module:
            pkg_parts.append(module)
        return ".".join(pkg_parts)

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        if original_node.relative is not None:
            level = len(original_node.relative)
            new_module = self._make_absolute(
                original_node.module.value if isinstance(original_node.module, cst.Name) else "",
                level,
            )
            return updated_node.with_changes(module=cst.Name(value=new_module), relative=None)
        if original_node.module is None:
            return updated_node
        module_name = original_node.module.value if isinstance(original_node.module, cst.Name) else ""
        if module_name.startswith("backend.apps.") or is_standard_lib(module_name):
            return updated_node
        if module_name.startswith("apps."):
            module_name = "backend.apps" + module_name[4:]
        elif not module_name.startswith("backend") and not module_name.startswith("django"):
            parts = module_name.split(".")
            if parts[0] in {p.name for p in BACKEND_APPS_ROOT.iterdir() if p.is_dir()}:
                module_name = f"backend.apps.{module_name}"
        return updated_node.with_changes(module=cst.Name(value=module_name))

def process_file(file_path: pathlib.Path) -> bool:
    try:
        source = file_path.read_text(encoding="utf-8")
    except Exception:
        return False
    try:
        module = cst.parse_module(source)
    except Exception:
        return False
    transformer = ImportNormalizer(file_path)
    new_tree = module.visit(transformer)
    new_code = new_tree.code
    if new_code != source:
        file_path.write_text(new_code, encoding="utf-8")
        return True
    return False

def main() -> None:
    python_files: list[pathlib.Path] = []
    for path in REPO_ROOT.rglob("*.py"):
        if "migrations" in path.parts:
            continue
        python_files.append(path)
    changed = []
    for py_file in python_files:
        if process_file(py_file):
            changed.append(str(py_file.relative_to(REPO_ROOT)))
    print("Import normalization complete. Modified files:")
    for f in changed:
        print(f" - {f}")

if __name__ == "__main__":
    main()
