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
#     result = locations_instance_from_dict(json.loads(json_string))

from dataclasses import dataclass
from typing import List, Any, Optional, TypeVar, Callable, Type, cast
from uuid import UUID
from datetime import datetime
import dateutil.parser


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_none(x: Any) -> Any:
    assert x is None
    return x


def from_union(fs, x):
    for f in fs:
        try:
            return f(x)
        except:
            pass
    assert False


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


@dataclass
class CurrentSensorValue:
    type_: str
    value: float
    provided_unit: str
    preferred_unit: str
    is_alert: bool
    thresholds: List[int]

    @staticmethod
    def from_dict(obj: Any) -> 'CurrentSensorValue':
        assert isinstance(obj, dict)
        type_ = from_str(obj.get("type"))
        value = from_float(obj.get("value"))
        provided_unit = from_str(obj.get("providedUnit"))
        preferred_unit = from_str(obj.get("preferredUnit"))
        is_alert = from_bool(obj.get("isAlert"))
        thresholds = from_list(from_int, obj.get("thresholds"))
        return CurrentSensorValue(type_, value, provided_unit, preferred_unit, is_alert, thresholds)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = from_str(self.type_)
        result["value"] = to_float(self.value)
        result["providedUnit"] = from_str(self.provided_unit)
        result["preferredUnit"] = from_str(self.preferred_unit)
        result["isAlert"] = from_bool(self.is_alert)
        result["thresholds"] = from_list(from_int, self.thresholds)
        return result


@dataclass
class Device:
    serial_number: str
    location_name: str
    location_id: UUID
    room_name: str
    publicly_available: bool
    segment_id: UUID
    segment_start: datetime
    current_sensor_values: List[CurrentSensorValue]
    type_: str
    latest_sample: Optional[datetime] = None
    battery_percentage: Optional[int] = None
    rssi: Optional[int] = None
    relay_device: Optional[str] = None
    is_hub_connection_lost: Optional[bool] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Device':
        assert isinstance(obj, dict)
        serial_number = from_str(obj.get("serialNumber"))
        location_name = from_str(obj.get("locationName"))
        location_id = UUID(obj.get("locationId"))
        room_name = from_str(obj.get("roomName"))
        publicly_available = from_bool(obj.get("publiclyAvailable"))
        segment_id = UUID(obj.get("segmentId"))
        segment_start = from_datetime(obj.get("segmentStart"))
        current_sensor_values = from_list(
            CurrentSensorValue.from_dict, obj.get("currentSensorValues"))
        type_ = from_str(obj.get("type"))
        latest_sample = from_union(
            [from_datetime, from_none], obj.get("latestSample"))
        battery_percentage = from_union(
            [from_int, from_none], obj.get("batteryPercentage"))
        rssi = from_union([from_int, from_none], obj.get("rssi"))
        relay_device = from_union(
            [from_str, from_none], obj.get("relayDevice"))
        is_hub_connection_lost = from_union(
            [from_bool, from_none], obj.get("isHubConnectionLost"))
        return Device(serial_number, location_name, location_id, room_name, publicly_available, segment_id, segment_start, current_sensor_values, type_, latest_sample, battery_percentage, rssi, relay_device, is_hub_connection_lost)

    def to_dict(self) -> dict:
        result: dict = {}
        result["serialNumber"] = from_str(self.serial_number)
        result["locationName"] = from_str(self.location_name)
        result["locationId"] = str(self.location_id)
        result["roomName"] = from_str(self.room_name)
        result["publiclyAvailable"] = from_bool(self.publicly_available)
        result["segmentId"] = str(self.segment_id)
        result["segmentStart"] = self.segment_start.isoformat()
        result["currentSensorValues"] = from_list(lambda x: to_class(
            CurrentSensorValue, x), self.current_sensor_values)
        result["type"] = from_str(self.type_)
        result["latestSample"] = from_union(
            [lambda x: x.isoformat(), from_none], self.latest_sample)
        result["batteryPercentage"] = from_union(
            [from_int, from_none], self.battery_percentage)
        result["rssi"] = from_union([from_int, from_none], self.rssi)
        result["relayDevice"] = from_union(
            [from_str, from_none], self.relay_device)
        result["isHubConnectionLost"] = from_union(
            [from_bool, from_none], self.is_hub_connection_lost)
        return result


@dataclass
class UsageHours:
    pass

    @staticmethod
    def from_dict(obj: Any) -> 'UsageHours':
        assert isinstance(obj, dict)
        return UsageHours()

    def to_dict(self) -> dict:
        result: dict = {}
        return result


@dataclass
class Location:
    id_: UUID
    name: str
    lat: float
    lng: float
    devices: List[Device]
    low_battery_count: int
    device_count: int
    floorplans: List[Any]
    usage_hours: UsageHours
    address: Optional[str] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Location':
        assert isinstance(obj, dict)
        id_ = UUID(obj.get("id"))
        name = from_str(obj.get("name"))
        lat = from_float(obj.get("lat"))
        lng = from_float(obj.get("lng"))
        devices = from_list(Device.from_dict, obj.get("devices"))
        low_battery_count = from_int(obj.get("lowBatteryCount"))
        device_count = from_int(obj.get("deviceCount"))
        floorplans = from_list(lambda x: x, obj.get("floorplans"))
        usage_hours = UsageHours.from_dict(obj.get("usageHours"))
        address = from_union([from_str, from_none], obj.get("address"))
        return Location(id_, name, lat, lng, devices, low_battery_count, device_count, floorplans, usage_hours, address)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id_)
        result["name"] = from_str(self.name)
        result["lat"] = to_float(self.lat)
        result["lng"] = to_float(self.lng)
        result["devices"] = from_list(
            lambda x: to_class(Device, x), self.devices)
        result["lowBatteryCount"] = from_int(self.low_battery_count)
        result["deviceCount"] = from_int(self.device_count)
        result["floorplans"] = from_list(lambda x: x, self.floorplans)
        result["usageHours"] = to_class(UsageHours, self.usage_hours)
        result["address"] = from_union([from_str, from_none], self.address)
        return result


@dataclass
class LocationsInstance:
    locations: List[Location]

    @staticmethod
    def from_dict(obj: Any) -> 'LocationsInstance':
        assert isinstance(obj, dict)
        locations = from_list(Location.from_dict, obj.get("locations"))
        return LocationsInstance(locations)

    def to_dict(self) -> dict:
        result: dict = {}
        result["locations"] = from_list(
            lambda x: to_class(Location, x), self.locations)
        return result


def locations_instance_from_dict(s: Any) -> LocationsInstance:
    return LocationsInstance.from_dict(s)


def locations_instance_to_dict(x: LocationsInstance) -> Any:
    return to_class(LocationsInstance, x)
