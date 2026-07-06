import os
import re

files_to_fix = [
    r"backend\apps\realtime\api\permissions.py",
    r"backend\apps\realtime\api\views.py",
    r"backend\apps\observability\api\views.py",
    r"backend\apps\integrations\api\views.py",
    r"backend\apps\collaboration\api\views.py",
    r"backend\apps\collaboration\api\permissions.py",
    r"backend\apps\decision_engine\api\views.py",
]

base_dir = r"C:\Users\Loho Christopher\Desktop\Footprint_manager"

for rel_path in files_to_fix:
    path = os.path.join(base_dir, rel_path)
    if not os.path.exists(path):
        continue

    with open(path, encoding="utf-8") as f:
        content = f.read()

    # Add import if needed
    if "get_tenant_id_for_user" not in content and ("request.user.tenant_id" in content):
        content = "from backend.shared.utils.tenant_resolver import get_tenant_id_for_user\n" + content

    # Replacements for `self.request.user.tenant_id` inside QuerySets
    content = content.replace(
        "tenant_id=self.request.user.tenant_id",
        "tenant_id=get_tenant_id_for_user(self.request.user)"
    )

    # Replacements for direct variable assignment: `tenant_id = request.user.tenant_id`
    content = content.replace(
        "request.user.tenant_id",
        "get_tenant_id_for_user(request.user)"
    )

    # Permissions check
    content = content.replace(
        "hasattr(request.user, \"tenant_id\") and request.user.tenant_id is not None",
        "get_tenant_id_for_user(request.user) is not None"
    )

    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

print("Backend refactor done.")
