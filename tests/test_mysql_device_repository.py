from datetime import datetime, timezone
from typing import Iterator

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db.models import Base
from app.models import AlertResponse, DeviceResponse
from app.repositories.mysql_device_repository import MySqlDeviceRepository
from app.services.device_service import DeviceAlreadyExistsError


@pytest.fixture
def repository() -> Iterator[MySqlDeviceRepository]:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        yield MySqlDeviceRepository(session)
    engine.dispose()


def make_device() -> DeviceResponse:
    return DeviceResponse(
        device_id="RTR-101",
        name="Branch Router",
        device_type="router",
        ip_address="192.168.10.1",
        status="online",
    )


def test_device_repository_round_trip_and_returns_domain_copies(
    repository: MySqlDeviceRepository,
) -> None:
    added = repository.add_device(make_device())
    added.name = "Changed outside repository"

    stored = repository.get_device("RTR-101")
    assert stored is not None
    assert stored.name == "Branch Router"
    assert repository.list_devices() == [stored]

    updated = repository.update_status("RTR-101", "offline")
    assert updated is not None
    assert updated.status == "offline"
    assert repository.update_status("MISSING", "offline") is None


def test_duplicate_device_raises_domain_error_and_rolls_back(
    repository: MySqlDeviceRepository,
) -> None:
    repository.add_device(make_device())

    with pytest.raises(DeviceAlreadyExistsError):
        repository.add_device(make_device())

    assert repository.get_device("RTR-101") is not None


def test_alert_repository_round_trip(
    repository: MySqlDeviceRepository,
) -> None:
    repository.add_device(make_device())
    alert = AlertResponse(
        device_id="RTR-101",
        message="Device RTR-101 changed from online to offline.",
        timestamp=datetime.now(timezone.utc),
    )

    saved = repository.save_alert(alert)

    assert saved == alert
    assert repository.list_alerts() == [alert]