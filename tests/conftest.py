"""
Shared test fixtures for the FastAPI application.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Provides a TestClient instance for testing the FastAPI application.
    
    This fixture creates a fresh client for each test, ensuring test isolation.
    """
    return TestClient(app)
