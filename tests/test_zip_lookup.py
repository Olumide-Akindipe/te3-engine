"""Tests for the offline ZIP lookup."""
# Copyright (c) 2026 Stephen Olumide Akindipe
# SPDX-License-Identifier: MIT

import os

import pytest

from zip_lookup import DEFAULT_ZIP_TABLE, lookup_zip


def test_table_present():
    assert os.path.exists(DEFAULT_ZIP_TABLE)


def test_albany_zip():
    loc = lookup_zip("12205", path=DEFAULT_ZIP_TABLE)
    assert loc["state_code"] == "US-NY" and loc["state"] == "New York"
    assert loc["display_name"] == "Albany, New York"
    assert 42.5 < loc["lat"] < 43.0 and -74.1 < loc["lon"] < -73.6


def test_leading_zero_zip():
    loc = lookup_zip("00501", path=DEFAULT_ZIP_TABLE)
    assert loc is not None and loc["state_code"] == "US-NY"


def test_out_of_state_zip_keeps_its_state():
    loc = lookup_zip("56567", path=DEFAULT_ZIP_TABLE)  # New York Mills, Minnesota
    assert loc["state"] == "Minnesota" and loc["state_code"] == "US-MN"


def test_unknown_zip_returns_none():
    assert lookup_zip("99999", path=DEFAULT_ZIP_TABLE) is None


@pytest.mark.parametrize("path", ["", "does/not/exist.csv"])
def test_table_off_or_missing_returns_none(path):
    assert lookup_zip("12205", path=path) is None
