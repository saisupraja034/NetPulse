from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import AlertResponse, DeviceCreate, DeviceResponse, StatusUpdate
from app.repositories.mysql_device_repository import MySqlDeviceRepository
from app.services.device_service import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    DeviceService,
)


router = APIRouter()


def get_device_repository(
    session: Session = Depends(get_db),
) -> MySqlDeviceRepository:
    return MySqlDeviceRepository(session)


def get_device_service(
    repository: MySqlDeviceRepository = Depends(get_device_repository),
) -> DeviceService:
    return DeviceService(repository)


@router.post(
    "/devices",
    response_model=DeviceResponse,
    status_code=status.HTTP_201_CREATED,
    responses={409: {"description": "A device with this ID already exists."}},
)
def register_device(
    device: DeviceCreate,
    device_service: DeviceService = Depends(get_device_service),
) -> DeviceResponse:
    try:
        return device_service.register(device)
    except DeviceAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail="Device already exists") from exc


@router.get("/devices", response_model=list[DeviceResponse])
def list_devices(
    device_service: DeviceService = Depends(get_device_service),
) -> list[DeviceResponse]:
    return device_service.list()


@router.get(
    "/devices/{device_id}",
    response_model=DeviceResponse,
    responses={404: {"description": "Device not found."}},
)
def get_device(
    device_id: str,
    device_service: DeviceService = Depends(get_device_service),
) -> DeviceResponse:
    try:
        return device_service.get(device_id)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Device not found") from exc


@router.patch(
    "/devices/{device_id}/status",
    response_model=DeviceResponse,
    responses={404: {"description": "Device not found."}},
)
def update_device_status(
    device_id: str,
    update: StatusUpdate,
    device_service: DeviceService = Depends(get_device_service),
) -> DeviceResponse:
    try:
        return device_service.update_status(device_id, update.status)
    except DeviceNotFoundError as exc:
        raise HTTPException(status_code=404, detail="Device not found") from exc


@router.get("/alerts", response_model=list[AlertResponse])
def list_alerts(
    repository: MySqlDeviceRepository = Depends(get_device_repository),
) -> list[AlertResponse]:
    return repository.list_alerts()


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}