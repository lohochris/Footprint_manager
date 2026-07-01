
from django.core.exceptions import ValidationError

# ---------- Status Transition Validation ----------

STATUS_TRANSITIONS = {
    "draft": ["open", "archived"],
    "open": ["in_progress", "on_hold", "closed", "archived"],
    "in_progress": ["on_hold", "completed", "closed", "archived"],
    "on_hold": ["in_progress", "closed", "archived"],
    "escalated": ["in_progress", "closed", "archived"],
    "under_review": ["completed", "closed", "archived"],
    "completed": ["closed", "archived"],
    "closed": [],
    "archived": [],
}


def validate_status_transition(current: str, target: str) -> None:
    """Validate that ``target`` is an allowed next status from ``current``.

    Raises:
        ValidationError: If the transition is not permitted.
    """
    allowed = STATUS_TRANSITIONS.get(current, [])
    if target not in allowed:
        raise ValidationError(
            f"Invalid status transition from '{current}' to '{target}'. Allowed: {allowed}"
        )


# ---------- Priority Validation ----------

ALLOWED_PRIORITIES = {"critical", "high", "medium", "low"}


def validate_priority(value: str) -> None:
    if value not in ALLOWED_PRIORITIES:
        raise ValidationError(f"Invalid priority '{value}'. Must be one of {ALLOWED_PRIORITIES}.")


# ---------- Tag Validation ----------

def validate_tags(tags: list[str]) -> None:
    if not isinstance(tags, list):
        raise ValidationError("Tags must be a list of strings.")
    for tag in tags:
        if not isinstance(tag, str) or not tag.strip():
            raise ValidationError("Each tag must be a non‑empty string.")
        if len(tag) > 50:
            raise ValidationError("Tag length must not exceed 50 characters.")

"""Utility validators for Investigation domain. All functions are side‑effect free.
"""
