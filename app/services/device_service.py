from app.events import create_offline_alert
from app.models import DeviceCreate, DeviceResponse, DeviceStatus


class DeviceAlreadyExistsError(Exception):
    pass


class DeviceNotFoundError(Exception):
    pass


class DeviceService:
    def __init__(self, repository) -> None:
        self.repository = repository

    def register(self, device: DeviceCreate) -> DeviceResponse:
        if self.repository.get_device(device.device_id) is not None:
            raise DeviceAlreadyExistsError(device.device_id)
        response = DeviceResponse(**device.model_dump())
        return self.repository.add_device(response)

    def list(self) -> list[DeviceResponse]:
        return self.repository.list_devices()

    def get(self, device_id: str) -> DeviceResponse:
        device = self.repository.get_device(device_id)
        if device is None:
            raise DeviceNotFoundError(device_id)
        return device

    def update_status(
        self, device_id: str, status: DeviceStatus
    ) -> DeviceResponse:
        current = self.repository.get_device(device_id)
        if current is None:
            raise DeviceNotFoundError(device_id)
        updated = self.repository.update_status(device_id, status)
        if current.status == "online" and status == "offline":
            create_offline_alert(self.repository, device_id)
        return updated