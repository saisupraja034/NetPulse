from __future__ import annotations

from app.events import create_offline_alert
from app.models import AlertResponse, DeviceCreate, DeviceResponse, DeviceStatus
from app.repositories.device_repository import InMemoryDeviceRepository


class DeviceAlreadyExistsError(Exception):
    pass


class DeviceNotFoundError(Exception):
    pass


class DeviceService:
    def __init__(self, repository: InMemoryDeviceRepository):
        self.repository = repository

    def register(self, device: DeviceCreate) -> DeviceResponse:
        if self.repository.get_device(device.device_id) is not None:
            raise DeviceAlreadyExistsError(device.device_id)
        return self.repository.add_device(DeviceResponse(**device.model_dump()))

    def list(self) -> list[DeviceResponse]:
        return self.repository.list_devices()

    def get(self, device_id: str) -> DeviceResponse:
        device = self.repository.get_device(device_id)
        if device is None:
            raise DeviceNotFoundError(device_id)
        return device

    def update_status(self, device_id: str, status: DeviceStatus) -> DeviceResponse:
        previous = self.get(device_id)
        updated = self.repository.update_status(device_id, status)
        if previous.status == "online" and updated.status == "offline":
            create_offline_alert(self.repository, device_id)
        return updated

    def list_alerts(self) -> list[AlertResponse]:
        return self.repository.list_alerts()