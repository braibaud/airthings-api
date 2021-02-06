# This code parses date/times, so please
#
#     pip install python-dateutil
#
# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = relay_devices_instance_from_dict(json.loads(json_string))

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any, TypeVar, Callable, Type, cast
from uuid import UUID
import dateutil.parser


T = TypeVar("T")


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_dict(f: Callable[[Any], T], x: Any) -> Dict[str, T]:
    assert isinstance(x, dict)
    return {k: f(v) for (k, v) in x.items()}


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class MetaData:
    last_seen: datetime
    ble_firmware_version: str
    sub_firmware_version: str
    st_firmware_version: str
    last_seen_devices: List[str]
    devices: Dict[str, int]
    region: str
    cell: bool

    @staticmethod
    def from_dict(obj: Any) -> 'MetaData':
        assert isinstance(obj, dict)
        last_seen = from_datetime(obj.get("lastSeen"))
        ble_firmware_version = from_str(obj.get("bleFirmwareVersion"))
        sub_firmware_version = from_str(obj.get("subFirmwareVersion"))
        st_firmware_version = from_str(obj.get("stFirmwareVersion"))
        last_seen_devices = from_list(from_str, obj.get("lastSeenDevices"))
        devices = from_dict(from_int, obj.get("devices"))
        region = from_str(obj.get("region"))
        cell = from_bool(obj.get("cell"))
        return MetaData(last_seen, ble_firmware_version, sub_firmware_version, st_firmware_version, last_seen_devices, devices, region, cell)

    def to_dict(self) -> dict:
        result: dict = {}
        result["lastSeen"] = self.last_seen.isoformat()
        result["bleFirmwareVersion"] = from_str(self.ble_firmware_version)
        result["subFirmwareVersion"] = from_str(self.sub_firmware_version)
        result["stFirmwareVersion"] = from_str(self.st_firmware_version)
        result["lastSeenDevices"] = from_list(from_str, self.last_seen_devices)
        result["devices"] = from_dict(from_int, self.devices)
        result["region"] = from_str(self.region)
        result["cell"] = from_bool(self.cell)
        return result


@dataclass
class Hub:
    serial_number: str
    device_type: str
    location_id: UUID
    name: str
    meta_data: MetaData

    @staticmethod
    def from_dict(obj: Any) -> 'Hub':
        assert isinstance(obj, dict)
        serial_number = from_str(obj.get("serialNumber"))
        device_type = from_str(obj.get("deviceType"))
        location_id = UUID(obj.get("locationId"))
        name = from_str(obj.get("name"))
        meta_data = MetaData.from_dict(obj.get("metaData"))
        return Hub(serial_number, device_type, location_id, name, meta_data)

    def to_dict(self) -> dict:
        result: dict = {}
        result["serialNumber"] = from_str(self.serial_number)
        result["deviceType"] = from_str(self.device_type)
        result["locationId"] = str(self.location_id)
        result["name"] = from_str(self.name)
        result["metaData"] = to_class(MetaData, self.meta_data)
        return result


@dataclass
class RelayDevicesInstance:
    hubs: List[Hub]

    @staticmethod
    def from_dict(obj: Any) -> 'RelayDevicesInstance':
        assert isinstance(obj, dict)
        hubs = from_list(Hub.from_dict, obj.get("hubs"))
        return RelayDevicesInstance(hubs)

    def to_dict(self) -> dict:
        result: dict = {}
        result["hubs"] = from_list(lambda x: to_class(Hub, x), self.hubs)
        return result


def relay_devices_instance_from_dict(s: Any) -> RelayDevicesInstance:
    return RelayDevicesInstance.from_dict(s)


def relay_devices_instance_to_dict(x: RelayDevicesInstance) -> Any:
    return to_class(RelayDevicesInstance, x)
