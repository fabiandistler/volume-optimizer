from fastapi.testclient import TestClient

from src.api import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health_check")
    assert response.status_code == 200
    assert response.json() == {"message": "Everything is working fine!"}
