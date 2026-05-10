"""Tests for the WarDragon dataclass models."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from wardragon_models import Drone, Kit, Signal  # type: ignore[import-not-found]

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_kit_round_trip() -> None:
    kit = Kit.from_attrs_payload(_load_fixture("system_attrs.json"))
    assert kit is not None
    assert kit.kit_id == "wardragon-G6PA14100J63"
    assert kit.cpu_usage == 23.4
    assert kit.gps_fix is True
    assert kit.has_position
    assert kit.pluto_temp_c == 48.7


def test_drone_round_trip_dji_o4() -> None:
    drone = Drone.from_drone_payload(_load_fixture("dji_o4.json"))
    assert drone is not None
    assert drone.drone_id == "drone-F6Q8D244C00CL2KF"
    assert drone.description == "DJI O4 (Decrypted)"
    assert drone.protocol_family == "O4"
    assert drone.freq_band == "5.8GHz"
    assert drone.has_position
    assert drone.has_pilot
    assert drone.has_home
    assert drone.seen_by == "wardragon-G6PA14100J63"
    assert drone.rssi_by_kit == {"wardragon-G6PA14100J63": -117.0}


def test_drone_round_trip_wifi_beacon() -> None:
    drone = Drone.from_drone_payload(_load_fixture("wifi_beacon.json"))
    assert drone is not None
    assert drone.protocol_family == "WiFi-Beacon"
    assert drone.freq_band == "2.4GHz"
    assert drone.ua_type_name == "Helicopter or Multirotor"
    assert drone.has_pilot
    assert not drone.has_home  # 0.0/0.0 sentinel filtered to None
    assert drone.caa_id == "FAA-12345"
    assert drone.rid_lookup_attempted is True
    assert drone.rid_lookup_success is False


def test_drone_no_fix_filtered() -> None:
    payload = {"id": "drone-X", "track_type": "drone", "lat": 0.0, "lon": 0.0, "rssi": -90.0}
    drone = Drone.from_drone_payload(payload)
    assert drone is not None
    assert drone.has_position is False
    assert drone.latitude is None
    assert drone.longitude is None


def test_drone_partial_payload_accepted() -> None:
    payload = {"id": "drone-Y", "track_type": "drone"}
    drone = Drone.from_drone_payload(payload)
    assert drone is not None
    assert drone.drone_id == "drone-Y"
    assert drone.has_position is False
    assert drone.protocol_family is None


def test_drone_missing_id_dropped() -> None:
    assert Drone.from_drone_payload({"track_type": "drone"}) is None
    assert Drone.from_drone_payload({"id": "", "track_type": "drone"}) is None


def test_drone_wrong_track_type_dropped() -> None:
    assert Drone.from_drone_payload({"id": "x", "track_type": "aircraft"}) is None


def test_drone_non_dict_dropped() -> None:
    assert Drone.from_drone_payload(None) is None  # type: ignore[arg-type]
    assert Drone.from_drone_payload("not a dict") is None  # type: ignore[arg-type]


def test_kit_missing_id_dropped() -> None:
    assert Kit.from_attrs_payload({"cpu_usage": 1.0}) is None


def test_kit_no_fix_position_filtered() -> None:
    payload = {"id": "wardragon-test", "latitude": 0.0, "longitude": 0.0, "gps_fix": False}
    kit = Kit.from_attrs_payload(payload)
    assert kit is not None
    assert kit.has_position is False


def test_drone_protocol_family_o3() -> None:
    payload = {"id": "drone-Z", "track_type": "drone", "description": "DJI Mini 3 (O3)"}
    drone = Drone.from_drone_payload(payload)
    assert drone is not None
    assert drone.protocol_family == "O3"


def test_drone_freq_band_900mhz() -> None:
    payload = {"id": "drone-W", "track_type": "drone", "freq_mhz": 915.0}
    drone = Drone.from_drone_payload(payload)
    assert drone is not None
    assert drone.freq_band == "900MHz"


def test_drone_freq_band_unknown() -> None:
    payload = {"id": "drone-W", "track_type": "drone", "freq_mhz": 1000.0}
    drone = Drone.from_drone_payload(payload)
    assert drone is not None
    assert drone.freq_band is None


def test_drone_merge_takes_best_rssi_position() -> None:
    a = Drone.from_drone_payload({
        "id": "drone-M",
        "track_type": "drone",
        "lat": 10.0, "lon": 20.0,
        "rssi": -90.0,
        "seen_by": "wardragon-A",
    })
    b = Drone.from_drone_payload({
        "id": "drone-M",
        "track_type": "drone",
        "lat": 10.5, "lon": 20.5,
        "rssi": -60.0,
        "seen_by": "wardragon-B",
    })
    assert a is not None and b is not None
    merged = a.merged_with(b)
    assert merged.latitude == 10.5
    assert merged.longitude == 20.5
    assert merged.rssi == -60.0
    assert merged.seen_by == "wardragon-B"
    assert merged.rssi_by_kit == {"wardragon-A": -90.0, "wardragon-B": -60.0}


def test_drone_merge_keeps_position_when_newer_lacks_fix() -> None:
    a = Drone.from_drone_payload({
        "id": "drone-N",
        "track_type": "drone",
        "lat": 10.0, "lon": 20.0,
        "rssi": -70.0,
        "seen_by": "wardragon-A",
    })
    b = Drone.from_drone_payload({
        "id": "drone-N",
        "track_type": "drone",
        "lat": 0.0, "lon": 0.0,
        "rssi": -50.0,
        "seen_by": "wardragon-B",
    })
    assert a is not None and b is not None
    merged = a.merged_with(b)
    assert merged.has_position
    assert merged.latitude == 10.0


def test_kit_with_availability() -> None:
    kit = Kit(kit_id="wardragon-x")
    assert kit.available is True
    offline = kit.with_availability(False)
    assert offline.available is False
    assert offline.kit_id == "wardragon-x"


def test_signal_round_trip() -> None:
    signal = Signal.from_payload(_load_fixture("signal_fpv.json"))
    assert signal is not None
    assert signal.uid == "signal-fpv-5810-001"
    assert signal.signal_type == "fpv"
    assert signal.center_mhz == 5810.0
    assert signal.bandwidth_mhz == 27.0
    assert signal.has_position
    assert signal.seen_by == "wardragon-G6PA14100J63"


def test_signal_missing_uid_dropped() -> None:
    assert Signal.from_payload({"signal_type": "fpv"}) is None
    assert Signal.from_payload({"uid": "", "signal_type": "fpv"}) is None


def test_signal_no_fix_filtered() -> None:
    signal = Signal.from_payload({
        "uid": "signal-x", "signal_type": "fpv", "lat": 0.0, "lon": 0.0, "rssi": -70.0,
    })
    assert signal is not None
    assert signal.has_position is False


def test_drone_merge_three_kits() -> None:
    a = Drone.from_drone_payload({
        "id": "drone-K", "track_type": "drone",
        "lat": 10.0, "lon": 20.0, "rssi": -90.0, "seen_by": "wardragon-A",
    })
    b = Drone.from_drone_payload({
        "id": "drone-K", "track_type": "drone",
        "lat": 10.5, "lon": 20.5, "rssi": -75.0, "seen_by": "wardragon-B",
    })
    c = Drone.from_drone_payload({
        "id": "drone-K", "track_type": "drone",
        "lat": 11.0, "lon": 21.0, "rssi": -55.0, "seen_by": "wardragon-C",
    })
    assert a is not None and b is not None and c is not None
    merged = a.merged_with(b).merged_with(c)
    assert merged.rssi == -55.0
    assert merged.latitude == 11.0
    assert merged.seen_by == "wardragon-C"
    assert merged.rssi_by_kit == {
        "wardragon-A": -90.0,
        "wardragon-B": -75.0,
        "wardragon-C": -55.0,
    }
