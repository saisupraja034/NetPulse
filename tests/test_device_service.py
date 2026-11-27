import pytest

from app.models import DeviceCreate
from app.repositories.device_repository import InMemoryDeviceRepository
from app.services.device_service import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    DeviceService,
)


@pytest.fixture
def service():
    return DeviceService(InMemoryDeviceRepository())


@pytest.fixture
def device():
    return DeviceCreate(
        device_id="RTR-101",
        name="Branch Router",
        device_type="router",
        ip_address="192.168.10.1",
    )


def test_registration(service, device):
    registered = service.register(device)
    assert registered.device_id == "RTR-101"
    assert registered.status == "online"
    assert service.get("RTR-101") == registered
    assert service.list() == [registered]


def test_duplicate_registration(service, device):
    service.register(device)
    with pytest.raises(DeviceAlreadyExistsError):
        service.register(device)


def test_missing_device(service):
    with pytest.raises(DeviceNotFoundError):
        service.get("missing")
    with pytest.raises(DeviceNotFoundError):
        service.update_status("missing", "offline")


def test_initial_offline_registration_does_not_alert(service, device):
    service.register(device.model_copy(update={"status": "offline"}))
    assert service.list_alerts() == []


def test_online_to_offline_and_repeated_offline(service, device):
    service.register(device)
    assert service.update_status(device.device_id, "offline").status == "offline"
    alerts = service.list_alerts()
    assert len(alerts) == 1
    assert alerts[0].device_id == device.device_id
    assert alerts[0].timestamp.utcoffset().total_seconds() == 0
    service.update_status(device.device_id, "offline")
    assert service.list_alerts() == alerts
    service.update_status(device.device_id, "online")
    service.update_status(device.device_id, "offline")
    assert len(service.list_alerts()) == 2


def test_repository_returns_copies(service, device):
    registered = service.register(device)
    registered.status = "offline"
    service.list()[0].name = "Changed"
    assert service.get(device.device_id).status == "online"
    assert service.get(device.device_id).name == "Branch Router"
    service.update_status(device.device_id, "offline")
    service.list_alerts()[0].message = "Changed"
    assert service.list_alerts()[0].message != "Changed"