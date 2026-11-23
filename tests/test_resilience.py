"""Tests for retries and the optional solar table."""
# Copyright (c) 2026 Stephen Olumide Akindipe
# SPDX-License-Identifier: MIT

from unittest import mock

import pytest
import requests

import te3_resilience as r


class Resp:
    def __init__(self, status, headers=None):
        self.status_code = status
        self.headers = headers or {}


@pytest.fixture(autouse=True)
def no_wait(monkeypatch):
    monkeypatch.setenv("TE3_RETRY_BASE_DELAY", "0")
    monkeypatch.setattr(r.time, "sleep", lambda s: None)


def test_retries_after_429_then_succeeds():
    with mock.patch("requests.get", side_effect=[Resp(429), Resp(200)]) as g:
        assert r.get_with_retry("https://x", timeout=1).status_code == 200
        assert g.call_count == 2


def test_retries_after_connection_error_then_succeeds():
    with mock.patch("requests.get", side_effect=[requests.ConnectionError("down"), Resp(200)]):
        assert r.get_with_retry("https://x").status_code == 200


def test_returns_last_429_after_all_attempts():
    with mock.patch("requests.get", side_effect=[Resp(429)] * 3) as g:
        assert r.get_with_retry("https://x").status_code == 429
        assert g.call_count == 3


def test_raises_when_never_reached():
    with mock.patch("requests.get", side_effect=requests.ConnectionError("down")):
        with pytest.raises(requests.ConnectionError):
            r.get_with_retry("https://x")


def test_no_retry_on_403():
    with mock.patch("requests.get", side_effect=[Resp(403)]) as g:
        assert r.get_with_retry("https://x").status_code == 403
        assert g.call_count == 1


def test_solar_table(tmp_path):
    t = tmp_path / "solar.csv"
    t.write_text("zip,lat,lon,solrad_annual,retrieved,source\n12205,42.72,-73.82,4.5316,2026-11-18,PVWatts v8\n")
    assert r.lookup_solrad("12205", path=str(t)) == pytest.approx(4.5316)
    assert r.lookup_solrad("10001", path=str(t)) is None
    assert r.lookup_solrad("12205", path="") is None
