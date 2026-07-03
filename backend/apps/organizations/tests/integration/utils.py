
def assert_problem_detail(response, status_code, title=None, type_=None):
    """Assert that a response follows RFC 9457 Problem Details format."""
    assert response.status_code == status_code, f"Expected {status_code}, got {response.status_code}"
    data = response.json()
    assert "detail" in data, "Problem Details must contain 'detail'"
    if title:
        assert data.get("title") == title, f"Expected title {title}, got {data.get('title')}"
    if type_:
        assert data.get("type") == type_, f"Expected type {type_}, got {data.get('type')}"

def assert_paginated(response, expected_count):
    """Validate DRF pagination structure and object count."""
    assert response.status_code == 200
    data = response.json()
    assert "results" in data, "Paginated response must contain 'results'"
    assert len(data["results"]) == expected_count, f"Expected {expected_count} items, got {len(data['results'])}"
    assert "count" in data
    assert data["count"] >= expected_count

def extract_audit_log(entry):
    """Placeholder to retrieve audit log entries for a model instance."""
    from backend.apps.audit.models import AuditLog
    return AuditLog.objects.filter(object_id=entry.id).order_by('-timestamp')
