import pytest
from django.core.exceptions import ValidationError

from backend.apps.investigations.validators.investigation_validator import (
    validate_priority,
    validate_status_transition,
    validate_tags,
)


def test_validate_status_transition_allowed():
    # draft -> open is allowed
    validate_status_transition('draft', 'open')

def test_validate_status_transition_not_allowed():
    with pytest.raises(ValidationError):
        validate_status_transition('closed', 'open')

def test_validate_priority_valid():
    validate_priority('high')

def test_validate_priority_invalid():
    with pytest.raises(ValidationError):
        validate_priority('unknown')

def test_validate_tags_valid():
    validate_tags(['tag1', 'tag2'])

def test_validate_tags_invalid_type():
    with pytest.raises(ValidationError):
        validate_tags('not a list')

def test_validate_tags_invalid_entry():
    with pytest.raises(ValidationError):
        validate_tags(['', 'valid'])
