"""Generate Django app boilerplate for Footprint Manager Sprint 0."""

from pathlib import Path

APPS = [
    ("accounts", "Accounts"),
    ("organizations", "Organizations"),
    ("rbac", "RBAC"),
    ("audit", "Audit"),
    ("notifications", "Notifications"),
    ("dashboard", "Dashboard"),
]

SUBDIRS = [
    "admin",
    "api",
    "models",
    "selectors",
    "services",
    "permissions",
    "tasks",
    "tests",
    "migrations",
]

ROOT = Path(__file__).resolve().parent.parent / "apps"

APP_TEMPLATE = '''"""Footprint Manager {label} application."""

from django.apps import AppConfig


class {class_name}Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.{name}"
    verbose_name = "{label}"
'''

INIT = '"""{label} {subdir} module."""\n'

for name, label in APPS:
    app_dir = ROOT / name
    app_dir.mkdir(parents=True, exist_ok=True)
    class_name = label.replace(" ", "")
    (app_dir / "apps.py").write_text(
        APP_TEMPLATE.format(name=name, label=label, class_name=class_name),
        encoding="utf-8",
    )
    (app_dir / "__init__.py").write_text(
        f'"""Footprint Manager {label} app."""\n', encoding="utf-8"
    )
    for subdir in SUBDIRS:
        sub_path = app_dir / subdir
        sub_path.mkdir(parents=True, exist_ok=True)
        (sub_path / "__init__.py").write_text(
            INIT.format(label=label, subdir=subdir),
            encoding="utf-8",
        )

print("Apps scaffolded.")
