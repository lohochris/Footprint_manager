"""Pytest configuration and shared fixtures for Footprint Manager."""

import pytest


@pytest.fixture
def api_client():
    """Return a DRF API client for integration tests."""
    from rest_framework.test import APIClient

    return APIClient()
