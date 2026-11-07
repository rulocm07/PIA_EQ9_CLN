import os
import pytest
from src.infrastructure.repository import SQLiteRepository
from src.application.services import HotelService
from src.api.main import app, get_service

@pytest.fixture
def service(tmp_path):
    return HotelService(SQLiteRepository(str(tmp_path / 'hotel_test.db')))

@pytest.fixture
def client(service):
    from fastapi.testclient import TestClient
    app.dependency_overrides[get_service] = lambda: service
    try:
        with TestClient(app) as c: yield c
    finally:
        app.dependency_overrides.clear()
