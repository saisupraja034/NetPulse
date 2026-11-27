import ipaddress
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, field_validator


DeviceType = Literal["router", "switch", "server"]
DeviceStatus = Literal["online", "offline"]


class DeviceCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "device_id": "RTR-101",
                    "name": "Branch Router",
                    "device_type": "router",
                    "ip_address": "192.168.10.1",
                    "location": "Branch Office",
                    "status": "online",
                }
            ]
        }
    )

    device_id: str
    name: str
    device_type: DeviceType
    ip_address: str
    location: str | None = None
    status: DeviceStatus = "online"

    @field_validator("ip_address")
    @classmethod
    def validate_ipv4(cls, value: str) -> str:
        try:
            address = ipaddress.ip_address(value)
        except ValueError as exc:
            raise ValueError("ip_address must be a valid IPv4 address") from exc
        if not isinstance(address, ipaddress.IPv4Address):
            raise ValueError("ip_address must be a valid IPv4 address")
        return value


class DeviceResponse(BaseModel):
    device_id: str
    name: str
    device_type: DeviceType
    ip_address: str
    location: str | None = None
    status: DeviceStatus


class StatusUpdate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={"examples": [{"status": "offline"}]}
    )

    status: DeviceStatus


class AlertResponse(BaseModel):
    device_id: str
    message: str
    timestamp: datetime