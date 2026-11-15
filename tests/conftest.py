"""Shared fixtures for the TE3 AppTest suite. API calls are mocked; no network or API key is needed."""
import os
import sys
from unittest import mock

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("NREL_API_KEY", "TEST_KEY_DO_NOT_USE")

APP = os.path.join(ROOT, "app.py")
SOLRAD = 4.5316  # kWh/m2/day; reproduces 184,917 kWh for 130 kW (verification checklist V-34)


class FakeResponse:
    def __init__(self, payload, status=200):
        self._payload = payload
        self.status_code = status

    def json(self):
        return self._payload


def fake_get_factory(solar_mode="ok", geo_mode="ok", state_code="US-NY"):
    import requests

    def fake_get(url, *args, **kwargs):
        if "nominatim" in url:
            if geo_mode == "error":
                raise requests.ConnectionError("simulated outage")
            if geo_mode == "empty":
                return FakeResponse([])
            return FakeResponse([{"lat": "42.7", "lon": "-73.8",
                                  "address": {"village": "Village of Colonie", "state": "New York" if state_code == "US-NY" else "Minnesota",
                                              "ISO3166-2-lvl4": state_code}}])
        if solar_mode == "error":
            raise requests.ConnectionError(f"Max retries exceeded with url: {url}?api_key=TEST_KEY_DO_NOT_USE")
        if solar_mode == "http403":
            return FakeResponse({"errors": ["API_KEY_INVALID"]}, status=403)
        return FakeResponse({"outputs": {"solrad_annual": SOLRAD}})
    return fake_get


@pytest.fixture
def run_app():
    """Run the app with a given configuration and return the AppTest object."""
    from streamlit.testing.v1 import AppTest
    import streamlit as st

    def _run(facility, kw, battery=False, hours=2, nem=False, shaving=False, dr=False, island=False,
             zip_code="12205", solar_mode="ok", geo_mode="ok", state_code="US-NY"):
        st.cache_data.clear()
        with mock.patch("requests.get", side_effect=fake_get_factory(solar_mode, geo_mode, state_code)):
            at = AppTest.from_file(APP, default_timeout=60)
            at.run()
            at.sidebar.text_input[0].set_value(zip_code)
            at.sidebar.selectbox[0].set_value(facility)
            at.sidebar.slider[0].set_value(kw)
            at.run()
            boxes = {c.label: c for c in at.sidebar.checkbox}
            if battery:
                boxes["Battery Storage (BESS)"].check()
                at.run()
                if hours == 4:
                    at.sidebar.selectbox[1].set_value(4)
                    at.run()
            boxes = {c.label: c for c in at.sidebar.checkbox}
            if nem:
                boxes["Net Energy Metering (NEM)"].check()
            if shaving and not boxes["Battery Peak Shaving"].disabled:
                boxes["Battery Peak Shaving"].check()
            if dr and not boxes["NYISO Demand Response (SCR)"].disabled:
                boxes["NYISO Demand Response (SCR)"].check()
            if island and not boxes["Microgrid Islanding (Backup Power)"].disabled:
                boxes["Microgrid Islanding (Backup Power)"].check()
            at.run()
            at.sidebar.button[0].click()
            at.run()
        return at
    return _run


def metrics(at):
    return {m.label: m.value for m in at.metric}
