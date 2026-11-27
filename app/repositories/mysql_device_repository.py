from datetime import timezone

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.db.models import Alert, Device
from app.models import AlertResponse, DeviceResponse, DeviceStatus
from app.services.device_service import DeviceAlreadyExistsError


class MySqlDeviceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add_device(self, device: DeviceResponse) -> DeviceResponse:
        record = Device(
            device_id=device.device_id,
            name=device.name,
            device_type=device.device_type,
            ip_address=device.ip_address,
            location=device.location,
            status=device.status,
        )
        try:
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
        except IntegrityError as exc:
            self.session.rollback()
            raise DeviceAlreadyExistsError(device.device_id) from exc
        except Exception:
            self.session.rollback()
            raise
        return self._to_device_response(record)

    def list_devices(self) -> list[DeviceResponse]:
        records = self.session.scalars(select(Device).order_by(Device.id)).all()
        return [self._to_device_response(record) for record in records]

    def get_device(self, device_id: str) -> DeviceResponse | None:
        record = self.session.scalar(
            select(Device).where(Device.device_id == device_id)
        )
        return self._to_device_response(record) if record is not None else None

    def update_status(
        self, device_id: str, status: DeviceStatus
    ) -> DeviceResponse | None:
        record = self.session.scalar(
            select(Device).where(Device.device_id == device_id)
        )
        if record is None:
            return None

        record.status = status
        try:
            self.session.commit()
            self.session.refresh(record)
        except Exception:
            self.session.rollback()
            raise
        return self._to_device_response(record)

    def save_alert(self, alert: AlertResponse) -> AlertResponse:
        timestamp = alert.timestamp
        if timestamp.tzinfo is not None:
            timestamp = timestamp.astimezone(timezone.utc).replace(tzinfo=None)
        record = Alert(
            device_id=alert.device_id,
            message=alert.message,
            timestamp=timestamp,
        )
        try:
            self.session.add(record)
            self.session.commit()
            self.session.refresh(record)
        except Exception:
            self.session.rollback()
            raise
        return self._to_alert_response(record)

    def list_alerts(self) -> list[AlertResponse]:
        records = self.session.scalars(select(Alert).order_by(Alert.id)).all()
        return [self._to_alert_response(record) for record in records]

    @staticmethod
    def _to_device_response(record: Device) -> DeviceResponse:
        return DeviceResponse(
            device_id=record.device_id,
            name=record.name,
            device_type=record.device_type,
            ip_address=record.ip_address,
            location=record.location,
            status=record.status,
        )

    @staticmethod
    def _to_alert_response(record: Alert) -> AlertResponse:
        timestamp = record.timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return AlertResponse(
            device_id=record.device_id,
            message=record.message,
            timestamp=timestamp,
        )