from fastapi.testclient import TestClient

from app.main import app
from app.repositories.device_repository import InMemoryDeviceRepository
from app.routes import devices
from app.services.device_service import DeviceService


def test_api_contract(monkeypatch):
    monkeypatch.setattr(devices, "service", DeviceService(InMemoryDeviceRepository()))
    client = TestClient(app)
    device = {
        "device_id": "RTR-101",
        "name": "Branch Router",
        "device_type": "router",
        "ip_address": "192.168.10.1",
        "status": "online",
    }
    assert client.get("/health").json() == {"status": "ok"}
    assert client.post("/devices", json=device).status_code == 201
    assert client.post("/devices", json=device).status_code == 409
    assert len(client.get("/devices").json()) == 1
    assert client.get("/devices/RTR-101").status_code == 200
    assert client.get("/devices/missing").status_code == 404
    assert client.patch("/devices/missing/status", json={"status": "offline"}).status_code == 404
    for _ in range(2):
        response = client.patch("/devices/RTR-101/status", json={"status": "offline"})
        assert response.status_code == 200
        assert response.json()["status"] == "offline"
    alerts = client.get("/alerts").json()
    assert len(alerts) == 1
    assert alerts[0]["device_id"] == "RTR-101"
    for invalid in ({"ip_address": "::1"}, {"device_type": "firewall"}, {"status": "unknown"}):
        assert client.post("/devices", json={**device, **invalid}).status_code == 422
    assert client.patch("/devices/RTR-101/status", json={"status": "unknown"}).status_code == 422
    paths = client.get("/openapi.json").json()["paths"]
    assert sum(len(methods) for methods in paths.values()) == 6
    assert "409" in paths["/devices"]["post"]["responses"]
    assert "404" in paths["/devices/{device_id}"]["get"]["responses"]
    assert "404" in paths["/devices/{device_id}/status"]["patch"]["responses"]