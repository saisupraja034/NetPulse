from collections.abc import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Base
from app.models import DeviceCreate
from app.repositories.device_repository import InMemoryDeviceRepository
from app.repositories.mysql_device_repository import MySqlDeviceRepository
from app.services.device_service import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    DeviceService,
)


Repository = InMemoryDeviceRepository | MySqlDeviceRepository


@pytest.fixture(params=["in-memory", "sqlite"])
def service_context(
    request: pytest.FixtureRequest,
) -> Iterator[tuple[Repository, DeviceService]]:
    if request.param == "in-memory":
        repository = InMemoryDeviceRepository()
        yield repository, DeviceService(repository)
        return

    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    try:
        with Session(engine) as session:
            repository = MySqlDeviceRepository(session)
            yield repository, DeviceService(repository)
    finally:
        engine.dispose()


def make_device(status: str = "online") -> DeviceCreate:
    return DeviceCreate(
        device_id="RTR-101",
        name="Branch Router",
        device_type="router",
        ip_address="192.168.10.1",
        status=status,
    )


def test_register_device(
    service_context: tuple[Repository, DeviceService],
) -> None:
    _, service = service_context

    registered = service.register(make_device())

    assert registered.device_id == "RTR-101"
    assert registered.status == "online"


def test_duplicate_registration_raises_error(
    service_context: tuple[Repository, DeviceService],
) -> None:
    _, service = service_context
    service.register(make_device())

    with pytest.raises(DeviceAlreadyExistsError):
        service.register(make_device())


def test_missing_device_raises_error(
    service_context: tuple[Repository, DeviceService],
) -> None:
    _, service = service_context

    with pytest.raises(DeviceNotFoundError):
        service.get("MISSING")


def test_initial_offline_registration_does_not_create_alert(
    service_context: tuple[Repository, DeviceService],
) -> None:
    repository, service = service_context

    service.register(make_device(status="offline"))

    assert repository.list_alerts() == []


def test_online_to_offline_creates_one_alert(
    service_context: tuple[Repository, DeviceService],
) -> None:
    repository, service = service_context
    service.register(make_device())

    service.update_status("RTR-101", "offline")

    alerts = repository.list_alerts()
    assert len(alerts) == 1
    assert alerts[0].device_id == "RTR-101"
    assert "online to offline" in alerts[0].message
    assert alerts[0].timestamp.utcoffset().total_seconds() == 0


def test_repeated_offline_update_does_not_create_another_alert(
    service_context: tuple[Repository, DeviceService],
) -> None:
    repository, service = service_context
    service.register(make_device())

    service.update_status("RTR-101", "offline")
    service.update_status("RTR-101", "offline")

    assert len(repository.list_alerts()) == 1


def test_optional_location_is_preserved(
    service_context: tuple[Repository, DeviceService],
) -> None:
    _, service = service_context
    device = make_device()
    device.location = "Branch Office"

    registered = service.register(device)

    assert registered.location == "Branch Office"