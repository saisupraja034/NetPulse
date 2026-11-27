from app.models import AlertResponse, DeviceResponse, DeviceStatus


class InMemoryDeviceRepository:
    def __init__(self) -> None:
        self._devices: dict[str, DeviceResponse] = {}
        self._alerts: list[AlertResponse] = []

    def add_device(self, device: DeviceResponse) -> DeviceResponse:
        self._devices[device.device_id] = device.model_copy(deep=True)
        return device.model_copy(deep=True)

    def list_devices(self) -> list[DeviceResponse]:
        return [device.model_copy(deep=True) for device in self._devices.values()]

    def get_device(self, device_id: str) -> DeviceResponse | None:
        device = self._devices.get(device_id)
        return device.model_copy(deep=True) if device else None

    def update_status(
        self, device_id: str, status: DeviceStatus
    ) -> DeviceResponse | None:
        device = self._devices.get(device_id)
        if device is None:
            return None
        updated = device.model_copy(update={"status": status}, deep=True)
        self._devices[device_id] = updated
        return updated.model_copy(deep=True)

    def save_alert(self, alert: AlertResponse) -> AlertResponse:
        self._alerts.append(alert.model_copy(deep=True))
        return alert.model_copy(deep=True)

    def list_alerts(self) -> list[AlertResponse]:
        return [alert.model_copy(deep=True) for alert in self._alerts]