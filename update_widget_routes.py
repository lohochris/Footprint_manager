import os
import re

base = r"C:\Users\Loho Christopher\Desktop\Footprint_manager\frontend\src\features\dashboard\components\widgets"
import_line = "import { routes } from '@/router/routes';\n"

# Map of hardcoded path fragments → routes.xxx() replacement
replacements = [
    # order matters — longer patterns first
    (r"`/workspace/${workspaceId}/investigations`", "routes.investigations(workspaceId)"),
    (r"`/workspace/${workspaceId}/intelligence`",   "routes.intelligence(workspaceId)"),
    (r"`/workspace/${workspaceId}/identity`",        "routes.identity(workspaceId)"),
    (r"`/workspace/${workspaceId}/evidence`",        "routes.evidence(workspaceId)"),
    (r"`/workspace/${workspaceId}/graph`",           "routes.graph(workspaceId)"),
    (r"`/workspace/${workspaceId}/timeline`",        "routes.timeline(workspaceId)"),
]

for fname in os.listdir(base):
    if not fname.endswith(".tsx"):
        continue
    path = os.path.join(base, fname)
    with open(path, encoding="utf-8") as f:
        content = f.read()

    changed = False
    for pattern, replacement in replacements:
        if pattern in content:
            content = content.replace(pattern, replacement)
            changed = True

    if changed:
        # Add routes import if not already present
        if "from '@/router/routes'" not in content:
            # Insert after last import line
            lines = content.split("\n")
            last_import_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("import "):
                    last_import_idx = i
            lines.insert(last_import_idx + 1, import_line.rstrip())
            content = "\n".join(lines)

        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Updated: {fname}")

print("Done.")
