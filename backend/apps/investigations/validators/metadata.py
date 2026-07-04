from django.core.exceptions import ValidationError


def validate_investigation_metadata(value):
    """Validate that metadata holds the correct schema structure."""
    if value is None:
        return
    if not isinstance(value, dict):
        raise ValidationError("Metadata must be a dictionary.")

    for k in value:
        if not isinstance(k, str):
            raise ValidationError("Metadata keys must be strings.")

    if "ai_processed" in value and not isinstance(value["ai_processed"], bool):
        raise ValidationError("ai_processed must be a boolean.")

    if "confidence_score" in value:
        score = value["confidence_score"]
        if not isinstance(score, (int, float)):
            raise ValidationError("confidence_score must be a number.")
        if not (0.0 <= score <= 1.0):
            raise ValidationError("confidence_score must be between 0.0 and 1.0.")

    if "tags" in value:
        tags = value["tags"]
        if not isinstance(tags, list):
            raise ValidationError("tags must be a list.")
        for tag in tags:
            if not isinstance(tag, str):
                raise ValidationError("tags list elements must be strings.")
