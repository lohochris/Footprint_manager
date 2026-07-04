import pathlib
import re

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]

def normalize_file(file_path: pathlib.Path) -> bool:
    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception:
        return False

    modified = False

    # 1. replace 'from backend.apps.xxx' with 'from backend.apps.xxx'
    new_content, count1 = re.subn(r'\bfrom\s+apps\.', 'from backend.apps.', content)
    if count1 > 0:
        content = new_content
        modified = True

    # 2. replace 'import backend.apps.xxx' with 'import backend.apps.xxx'
    new_content, count2 = re.subn(r'\bimport\s+apps\.', 'import backend.apps.', content)
    if count2 > 0:
        content = new_content
        modified = True

    if modified:
        file_path.write_text(content, encoding="utf-8")
        return True
    return False

def main():
    changed = []
    for path in REPO_ROOT.rglob("*.py"):
        if "migrations" in path.parts:
            continue
        if "venv" in path.parts or ".venv" in path.parts:
            continue
        if normalize_file(path):
            changed.append(str(path.relative_to(REPO_ROOT)))

    print(f"Normalized imports in {len(changed)} files:")
    for f in changed:
        print(f"  - {f}")

if __name__ == "__main__":
    main()
