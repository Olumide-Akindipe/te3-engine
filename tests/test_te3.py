"""Automated regression tests for TE3 Engine Version 1 [FIX M5].
Expected values follow te3-verification-checklist.md (Rev 1.4, C22 profiles). Run: pytest -q"""
from conftest import metrics


def test_v09_shaving_capped_at_facility_peak(run_app):
    at = run_app("Municipal Office Building", 500, battery=True, shaving=True)
    assert not at.exception
    assert metrics(at)["Battery Peak Shaving"] == "$21,580.20/yr"  # min(200, 95) x 18.93 x 12


def test_v12_water_plant_dr(run_app):
    at = run_app("Water Treatment Plant", 100, battery=True, dr=True)
    m = metrics(at)
    assert m["NYISO DR Market Revenue"] == "$500.00/yr"
    assert m["Estimated DR Load Reduction"] == "25.0 kW"


def test_v29_library_dr_capped(run_app):
    at = run_app("Public Library", 300, battery=True, dr=True)
    m = metrics(at)
    assert m["NYISO DR Market Revenue"] == "$1,880.00/yr"
    assert m["Estimated DR Load Reduction"] == "94.0 kW"


def test_v34_police_no_modules(run_app):
    at = run_app("Police Station", 130)
    m = metrics(at)
    assert m["Estimated Annual Savings"] == "$12,828.90 / yr"
    assert m["Simple Payback Period"] == "17.7 Years"


def test_v37_school_sc3(run_app):
    at = run_app("Public School Facility", 200, battery=True, hours=4, shaving=True, dr=True)
    m = metrics(at)
    assert m["Battery Peak Shaving"] == "$14,995.20/yr"
    assert m["NYISO DR Market Revenue"] == "$2,000.00/yr"


def test_l3_sc3_fixed_block(run_app):
    # School 209 kW; 500 kW solar shaves min(200, 209) = 200 kW, but only 209 - 40 = 169 kW is billed per kW
    at = run_app("Public School Facility", 500, battery=True, shaving=True)
    assert metrics(at)["Battery Peak Shaving"] == "$31,677.36/yr"  # 169 x 15.62 x 12


def test_v25_full_stack_eoc(run_app):
    at = run_app("Emergency Operations Center (EOC)", 200, battery=True, hours=4, nem=True, shaving=True,
                 dr=True, island=True)
    assert not at.exception
    m = metrics(at)
    assert m["NYISO DR Market Revenue"] == "$0.00/yr"
    assert m["Battery Peak Shaving"] == "$13,629.60/yr"


def test_h1_api_key_never_displayed(run_app):
    for mode in ("error", "http403"):
        at = run_app("Municipal Office Building", 50, solar_mode=mode)
        shown = " ".join(e.value for e in at.error) + " ".join(w.value for w in at.warning)
        assert "TEST_KEY_DO_NOT_USE" not in shown
        assert "Solar resource data unavailable" in shown


def test_m1_geocoder_errors(run_app):
    at = run_app("Municipal Office Building", 50, geo_mode="error")
    assert any("Location lookup failed" in e.value for e in at.error)
    at = run_app("Municipal Office Building", 50, geo_mode="empty")
    assert any("was not found" in e.value for e in at.error)


def test_v04_out_of_state_blocked(run_app):
    at = run_app("Municipal Office Building", 50, zip_code="56567", state_code="US-MN")
    assert any("outside New York State" in w.value for w in at.warning)
    assert not at.metric


def test_pdf_generates_for_every_facility(run_app):
    # The PDF is built on every successful run; an exception here would appear in at.exception
    from facility_profiles import FACILITY_PROFILES
    for facility in FACILITY_PROFILES:
        at = run_app(facility, 100, battery=True, hours=4, nem=True, shaving=True, dr=True, island=True)
        assert not at.exception, facility
        assert at.metric, facility


def test_p43_pdf_unicode_place_name(run_app, monkeypatch):
    # A place name outside Latin-1 must not stop PDF generation
    import conftest
    original = conftest.fake_get_factory

    def factory(*args, **kwargs):
        inner = original(*args, **kwargs)

        def fake_get(url, *a, **k):
            if "nominatim" in url:
                return conftest.FakeResponse([{"lat": "42.7", "lon": "-73.8",
                                               "address": {"village": "\u014ctsu \u2013 Test", "state": "New York",
                                                           "ISO3166-2-lvl4": "US-NY"}}])
            return inner(url, *a, **k)
        return fake_get
    monkeypatch.setattr(conftest, "fake_get_factory", factory)
    at = run_app("Municipal Office Building", 50)
    assert not at.exception
    assert at.metric
