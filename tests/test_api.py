from __future__ import annotations

from fastapi.testclient import TestClient

from cscode.server.app import app


def test_get_config():
    with TestClient(app) as client:
        response = client.get("/api/config")
        assert response.status_code == 200
        data = response.json()
        assert "provider" in data
        assert "model" in data


def test_create_session():
    with TestClient(app) as client:
        response = client.post("/api/sessions", json={"title": "Test Session"})
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["title"] == "Test Session"
