"""Tests for topic parsing helpers in const.py."""

from __future__ import annotations

from wardragon_const import parse_service_topic, parse_system_topic  # type: ignore[import-not-found]


def test_parse_system_topic_attrs() -> None:
    assert parse_system_topic("wardragon", "wardragon/system/wardragon-G6PA14100J63/attrs") == (
        "wardragon-G6PA14100J63",
        "attrs",
    )


def test_parse_system_topic_availability() -> None:
    assert parse_system_topic("wardragon", "wardragon/system/wardragon-A/availability") == (
        "wardragon-A",
        "availability",
    )


def test_parse_system_topic_state() -> None:
    assert parse_system_topic("wardragon", "wardragon/system/wardragon-A/state") == (
        "wardragon-A",
        "state",
    )


def test_parse_system_topic_slashed_prefix() -> None:
    assert parse_system_topic("site/wardragon", "site/wardragon/system/wardragon-A/attrs") == (
        "wardragon-A",
        "attrs",
    )


def test_parse_system_topic_wrong_prefix() -> None:
    assert parse_system_topic("wardragon", "other/system/kit-1/attrs") is None


def test_parse_system_topic_too_short() -> None:
    assert parse_system_topic("wardragon", "wardragon/system") is None
    assert parse_system_topic("wardragon", "wardragon/system/wardragon-A") is None


def test_parse_system_topic_empty_kit_id() -> None:
    assert parse_system_topic("wardragon", "wardragon/system//attrs") is None


def test_parse_service_topic() -> None:
    assert (
        parse_service_topic("wardragon", "wardragon/service/wardragon-A/availability")
        == "wardragon-A"
    )


def test_parse_service_topic_slashed_prefix() -> None:
    assert (
        parse_service_topic("site/wardragon", "site/wardragon/service/kit-X/availability")
        == "kit-X"
    )


def test_parse_service_topic_wrong_suffix() -> None:
    assert parse_service_topic("wardragon", "wardragon/service/kit-A/state") is None


def test_parse_service_topic_empty_kit_id() -> None:
    assert parse_service_topic("wardragon", "wardragon/service//availability") is None
