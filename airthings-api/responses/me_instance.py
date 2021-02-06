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
#     result = me_instance_from_dict(json.loads(json_string))

from dataclasses import dataclass
from uuid import UUID
from datetime import datetime
from typing import Any, Dict, List, TypeVar, Callable, Type, cast
import dateutil.parser


T = TypeVar("T")


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_bool(x: Any) -> bool:
    assert isinstance(x, bool)
    return x


def from_datetime(x: Any) -> datetime:
    return dateutil.parser.parse(x)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


def from_float(x: Any) -> float:
    assert isinstance(x, (float, int)) and not isinstance(x, bool)
    return float(x)


def to_float(x: Any) -> float:
    assert isinstance(x, float)
    return x


def from_dict(f: Callable[[Any], T], x: Any) -> Dict[str, T]:
    assert isinstance(x, dict)
    return { k: f(v) for (k, v) in x.items() }


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


@dataclass
class Group:
    id_: UUID
    group_name: str
    genesis: bool
    role: str
    created_by_user_id: UUID
    created_at: datetime
    updated_at: datetime
    display_subscription: bool

    @staticmethod
    def from_dict(obj: Any) -> 'Group':
        assert isinstance(obj, dict)
        id_ = UUID(obj.get("id"))
        group_name = from_str(obj.get("groupName"))
        genesis = from_bool(obj.get("genesis"))
        role = from_str(obj.get("role"))
        created_by_user_id = UUID(obj.get("createdByUserId"))
        created_at = from_datetime(obj.get("createdAt"))
        updated_at = from_datetime(obj.get("updatedAt"))
        display_subscription = from_bool(obj.get("displaySubscription"))
        return Group(id_, group_name, genesis, role, created_by_user_id, created_at, updated_at, display_subscription)

    def to_dict(self) -> dict:
        result: dict = {}
        result["id"] = str(self.id_)
        result["groupName"] = from_str(self.group_name)
        result["genesis"] = from_bool(self.genesis)
        result["role"] = from_str(self.role)
        result["createdByUserId"] = str(self.created_by_user_id)
        result["createdAt"] = self.created_at.isoformat()
        result["updatedAt"] = self.updated_at.isoformat()
        result["displaySubscription"] = from_bool(self.display_subscription)
        return result


@dataclass
class Threshold:
    default_high: int
    default_low: int
    min_selectable_value: int
    max_selectable_value: int
    unit: str
    threshold_delta: float

    @staticmethod
    def from_dict(obj: Any) -> 'Threshold':
        assert isinstance(obj, dict)
        default_high = from_int(obj.get("defaultHigh"))
        default_low = from_int(obj.get("defaultLow"))
        min_selectable_value = from_int(obj.get("minSelectableValue"))
        max_selectable_value = from_int(obj.get("maxSelectableValue"))
        unit = from_str(obj.get("unit"))
        threshold_delta = from_float(obj.get("thresholdDelta"))
        return Threshold(default_high, default_low, min_selectable_value, max_selectable_value, unit, threshold_delta)

    def to_dict(self) -> dict:
        result: dict = {}
        result["defaultHigh"] = from_int(self.default_high)
        result["defaultLow"] = from_int(self.default_low)
        result["minSelectableValue"] = from_int(self.min_selectable_value)
        result["maxSelectableValue"] = from_int(self.max_selectable_value)
        result["unit"] = from_str(self.unit)
        result["thresholdDelta"] = to_float(self.threshold_delta)
        return result


@dataclass
class Notifications:
    thresholds: Dict[str, Threshold]

    @staticmethod
    def from_dict(obj: Any) -> 'Notifications':
        assert isinstance(obj, dict)
        thresholds = from_dict(Threshold.from_dict, obj.get("thresholds"))
        return Notifications(thresholds)

    def to_dict(self) -> dict:
        result: dict = {}
        result["thresholds"] = from_dict(lambda x: to_class(Threshold, x), self.thresholds)
        return result


@dataclass
class MeInstance:
    name: str
    email: str
    date_format: str
    measurement_unit: str
    is_pro_user: bool
    notifications: Notifications
    rf_region: str
    is_demo_user: bool
    groups: List[Group]
    language: str
    intercom_user_hash: str
    user_id: UUID

    @staticmethod
    def from_dict(obj: Any) -> 'MeInstance':
        assert isinstance(obj, dict)
        name = from_str(obj.get("name"))
        email = from_str(obj.get("email"))
        date_format = from_str(obj.get("dateFormat"))
        measurement_unit = from_str(obj.get("measurementUnit"))
        is_pro_user = from_bool(obj.get("isProUser"))
        notifications = Notifications.from_dict(obj.get("notifications"))
        rf_region = from_str(obj.get("rfRegion"))
        is_demo_user = from_bool(obj.get("isDemoUser"))
        groups = from_list(Group.from_dict, obj.get("groups"))
        language = from_str(obj.get("language"))
        intercom_user_hash = from_str(obj.get("intercomUserHash"))
        user_id = UUID(obj.get("userId"))
        return MeInstance(name, email, date_format, measurement_unit, is_pro_user, notifications, rf_region, is_demo_user, groups, language, intercom_user_hash, user_id)

    def to_dict(self) -> dict:
        result: dict = {}
        result["name"] = from_str(self.name)
        result["email"] = from_str(self.email)
        result["dateFormat"] = from_str(self.date_format)
        result["measurementUnit"] = from_str(self.measurement_unit)
        result["isProUser"] = from_bool(self.is_pro_user)
        result["notifications"] = to_class(Notifications, self.notifications)
        result["rfRegion"] = from_str(self.rf_region)
        result["isDemoUser"] = from_bool(self.is_demo_user)
        result["groups"] = from_list(lambda x: to_class(Group, x), self.groups)
        result["language"] = from_str(self.language)
        result["intercomUserHash"] = from_str(self.intercom_user_hash)
        result["userId"] = str(self.user_id)
        return result


def me_instance_from_dict(s: Any) -> MeInstance:
    return MeInstance.from_dict(s)


def me_instance_to_dict(x: MeInstance) -> Any:
    return to_class(MeInstance, x)
