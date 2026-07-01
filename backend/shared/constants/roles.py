"""Role constants used across the project.

These constants are imported by services and permission checks to avoid
stringly‑typed role handling.
"""

ROLE_OWNER = "owner"
ROLE_ADMIN = "admin"
ROLE_MANAGER = "manager"
ROLE_ANALYST = "analyst"
ROLE_MEMBER = "member"
ROLE_VIEWER = "viewer"

__all__ = [
    "ROLE_OWNER",
    "ROLE_ADMIN",
    "ROLE_MANAGER",
    "ROLE_ANALYST",
    "ROLE_MEMBER",
    "ROLE_VIEWER",
]
