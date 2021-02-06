# To use this code, make sure you
#
#     import json
#
# and then, to convert JSON from a string, do
#
#     result = thresholds_instance_from_dict(json.loads(json_string))

from enum import Enum
from dataclasses import dataclass
from typing import Optional, Any, List, TypeVar, Type, Callable, cast


T = TypeVar("T")
EnumT = TypeVar("EnumT", bound=Enum)


def from_int(x: Any) -> int:
    assert isinstance(x, int) and not isinstance(x, bool)
    return x


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


def to_enum(c: Type[EnumT], x: Any) -> EnumT:
    assert isinstance(x, c)
    return x.value


def from_str(x: Any) -> str:
    assert isinstance(x, str)
    return x


def from_list(f: Callable[[Any], T], x: Any) -> List[T]:
    assert isinstance(x, list)
    return [f(y) for y in x]


def to_class(c: Type[T], x: Any) -> dict:
    assert isinstance(x, c)
    return cast(Any, x).to_dict()


class Rating(Enum):
    FAIR = "FAIR"
    GOOD = "GOOD"
    POOR = "POOR"


@dataclass
class Co2Range:
    rating: Rating
    to: Optional[int] = None
    range_from: Optional[int] = None

    @staticmethod
    def from_dict(obj: Any) -> 'Co2Range':
        assert isinstance(obj, dict)
        rating = Rating(obj.get("rating"))
        to = from_union([from_int, from_none], obj.get("to"))
        range_from = from_union([from_int, from_none], obj.get("from"))
        return Co2Range(rating, to, range_from)

    def to_dict(self) -> dict:
        result: dict = {}
        result["rating"] = to_enum(Rating, self.rating)
        result["to"] = from_union([from_int, from_none], self.to)
        result["from"] = from_union([from_int, from_none], self.range_from)
        return result


@dataclass
class Co2:
    type_: str
    unit: str
    ranges: List[Co2Range]

    @staticmethod
    def from_dict(obj: Any) -> 'Co2':
        assert isinstance(obj, dict)
        type_ = from_str(obj.get("type"))
        unit = from_str(obj.get("unit"))
        ranges = from_list(Co2Range.from_dict, obj.get("ranges"))
        return Co2(type_, unit, ranges)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = from_str(self.type_)
        result["unit"] = from_str(self.unit)
        result["ranges"] = from_list(
            lambda x: to_class(Co2Range, x), self.ranges)
        return result


@dataclass
class PressureRange:
    rating: Rating

    @staticmethod
    def from_dict(obj: Any) -> 'PressureRange':
        assert isinstance(obj, dict)
        rating = Rating(obj.get("rating"))
        return PressureRange(rating)

    def to_dict(self) -> dict:
        result: dict = {}
        result["rating"] = to_enum(Rating, self.rating)
        return result


@dataclass
class Pressure:
    type_: str
    unit: str
    ranges: List[PressureRange]

    @staticmethod
    def from_dict(obj: Any) -> 'Pressure':
        assert isinstance(obj, dict)
        type_ = from_str(obj.get("type"))
        unit = from_str(obj.get("unit"))
        ranges = from_list(PressureRange.from_dict, obj.get("ranges"))
        return Pressure(type_, unit, ranges)

    def to_dict(self) -> dict:
        result: dict = {}
        result["type"] = from_str(self.type_)
        result["unit"] = from_str(self.unit)
        result["ranges"] = from_list(
            lambda x: to_class(PressureRange, x), self.ranges)
        return result


@dataclass
class Thresholds:
    temp: Co2
    humidity: Co2
    voc: Co2
    co2: Co2
    radon_short_term_avg: Co2
    pressure: Pressure
    mold: Co2
    virus_risk: Co2

    @staticmethod
    def from_dict(obj: Any) -> 'Thresholds':
        assert isinstance(obj, dict)
        temp = Co2.from_dict(obj.get("temp"))
        humidity = Co2.from_dict(obj.get("humidity"))
        voc = Co2.from_dict(obj.get("voc"))
        co2 = Co2.from_dict(obj.get("co2"))
        radon_short_term_avg = Co2.from_dict(obj.get("radonShortTermAvg"))
        pressure = Pressure.from_dict(obj.get("pressure"))
        mold = Co2.from_dict(obj.get("mold"))
        virus_risk = Co2.from_dict(obj.get("virusRisk"))
        return Thresholds(temp, humidity, voc, co2, radon_short_term_avg, pressure, mold, virus_risk)

    def to_dict(self) -> dict:
        result: dict = {}
        result["temp"] = to_class(Co2, self.temp)
        result["humidity"] = to_class(Co2, self.humidity)
        result["voc"] = to_class(Co2, self.voc)
        result["co2"] = to_class(Co2, self.co2)
        result["radonShortTermAvg"] = to_class(Co2, self.radon_short_term_avg)
        result["pressure"] = to_class(Pressure, self.pressure)
        result["mold"] = to_class(Co2, self.mold)
        result["virusRisk"] = to_class(Co2, self.virus_risk)
        return result


@dataclass
class ThresholdsInstance:
    thresholds: Thresholds

    @staticmethod
    def from_dict(obj: Any) -> 'ThresholdsInstance':
        assert isinstance(obj, dict)
        thresholds = Thresholds.from_dict(obj.get("thresholds"))
        return ThresholdsInstance(thresholds)

    def to_dict(self) -> dict:
        result: dict = {}
        result["thresholds"] = to_class(Thresholds, self.thresholds)
        return result


def thresholds_instance_from_dict(s: Any) -> ThresholdsInstance:
    return ThresholdsInstance.from_dict(s)


def thresholds_instance_to_dict(x: ThresholdsInstance) -> Any:
    return to_class(ThresholdsInstance, x)
