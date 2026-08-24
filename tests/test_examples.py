"""Smoke tests for the runnable examples shipped with the package."""

from __future__ import annotations

from examples import basic_usage


def test_examples_use_the_public_api(monkeypatch) -> None:
    monkeypatch.setattr(basic_usage.time, "sleep", lambda _seconds: None)

    basic_usage.example_track()
    basic_usage.example_range()
    basic_usage.example_context()
