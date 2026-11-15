"""
TE3 Engine: Facility archetype profiles (location-aware)

The tool resolves inputs from a ZIP code. This module derives each archetype's
annual demand, peak demand, rate and tariff class for the ZIP's location
instead of hard-coding one utility (National Grid) for all of New York.

Backward compatibility
    FACILITY_PROFILES            New York default (Northeast region, National
                                 Grid labels and sourced rates). Same keys
                                 as the previous build.
    get_facility_profiles(zip)   Location-aware version. Use this in the app.

Structure
    SECTION 1  Location resolution (ZIP -> state, census region, utility, rate)
    SECTION 2  Sourced constants (CBECS by subcategory and region, water, lighting, signals)
    SECTION 3  Archetype inputs (areas, load factors, assumptions)
    SECTION 4  Tariff classification (generic class -> utility label)
    SECTION 5  Derivation functions
    SECTION 6  Descriptions and output

Note: "base_kw" holds the estimated ANNUAL PEAK demand in kW, not a baseload.
The key name is kept only for compatibility; consider renaming to "peak_kw".
"""

import csv
import os

HOURS_PER_YEAR = 8760

# ---------------------------------------------------------------------------
# SECTION 1: Location resolution
#
# Utility and average commercial rate by ZIP come from the NREL/OpenEI dataset
# "U.S. Electric Utility Companies and Rates: Look-up by Zipcode", built from
# EIA Form 861. Download the latest year (IOU and non-IOU CSV files) from
# https://catalog.data.gov/dataset/u-s-electric-utility-companies-and-rates-look-up-by-zipcode-2023
# and place them in ./data/. Verify column names against the downloaded file;
# the loader expects: zip, eiaid, utility_name, state, ownership, comm_rate.
#
# comm_rate is the utility's average commercial revenue per kWh, which already
# blends energy, delivery and demand charges. That matches how the tool uses a
# single average $/kWh rate. It does NOT capture demand-charge savings from
# batteries; model those separately from tariff demand rates.
# ---------------------------------------------------------------------------
UTILITY_ZIP_FILES = [
    "data/iou_zipcodes_2023.csv",
    "data/non_iou_zipcodes_2023.csv",
]

# U.S. Census Bureau regions (the geography CBECS reports by)
CENSUS_REGION = {
    "Northeast": ["CT", "ME", "MA", "NH", "RI", "VT", "NJ", "NY", "PA"],
    "Midwest": ["IL", "IN", "MI", "OH", "WI", "IA", "KS", "MN", "MO", "NE", "ND", "SD"],
    "South": ["DE", "DC", "FL", "GA", "MD", "NC", "SC", "VA", "WV", "AL", "KY", "MS",
              "TN", "AR", "LA", "OK", "TX"],
    "West": ["AZ", "CO", "ID", "MT", "NV", "NM", "UT", "WY", "AK", "CA", "HI", "OR", "WA"],
}
STATE_TO_REGION = {st: reg for reg, states in CENSUS_REGION.items() for st in states}

_ZIP_INDEX = None


def _load_zip_index():
    """Index the OpenEI ZIP files. Where a ZIP has several utilities, prefer
    the investor-owned utility, since it serves most commercial accounts."""
    global _ZIP_INDEX
    if _ZIP_INDEX is not None:
        return _ZIP_INDEX
    _ZIP_INDEX = {}
    for path in UTILITY_ZIP_FILES:
        if not os.path.exists(path):
            continue
        with open(path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                z = str(row.get("zip", "")).zfill(5)
                try:
                    rate = float(row.get("comm_rate") or 0)
                except ValueError:
                    rate = 0
                rec = {
                    "utility_name": row.get("utility_name", ""),
                    "eiaid": row.get("eiaid", ""),
                    "state": row.get("state", ""),
                    "ownership": row.get("ownership", ""),
                    "comm_rate": rate if rate > 0 else None,
                }
                current = _ZIP_INDEX.get(z)
                is_iou = "investor" in rec["ownership"].lower()
                if current is None or (is_iou and "investor" not in current["ownership"].lower()):
                    _ZIP_INDEX[z] = rec
    return _ZIP_INDEX


def resolve_location(zip_code, state=None):
    """Return state, census region, utility and average commercial rate for a ZIP.
    Falls back to New York defaults when the ZIP files are not present."""
    z = str(zip_code).zfill(5)
    rec = _load_zip_index().get(z)
    st = (rec or {}).get("state") or state or "NY"
    return {
        "zip": z,
        "state": st,
        "census_region": STATE_TO_REGION.get(st, "Northeast"),
        "utility_name": (rec or {}).get("utility_name") or "Niagara Mohawk Power Corp. (National Grid)",
        "eiaid": (rec or {}).get("eiaid"),
        "comm_rate": (rec or {}).get("comm_rate"),   # None -> DEFAULT_RATE
        "rate_source": "OpenEI ZIP look-up (EIA-861)" if rec and rec.get("comm_rate")
                       else DEFAULT_RATE_SOURCE,
    }

# ---------------------------------------------------------------------------
# SECTION 2: Sourced constants
# ---------------------------------------------------------------------------

# EIA CBECS 2018 electricity intensity (kWh per sq ft per year).
# National: Table C14  https://www.eia.gov/consumption/commercial/data/2018/ce/pdf/c14.pdf
# Regional: Table C15  https://www.eia.gov/consumption/commercial/data/2018/ce/pdf/c15.pdf
# None = withheld by EIA (Q: RSE > 50% or < 20 sample buildings) -> national value used.
CBECS_KWH_PER_SQFT = {
    #                          National  Northeast Midwest  South  West
    "Office":                  {"National": 13.6, "Northeast": 13.8, "Midwest": 12.0, "South": 15.4, "West": 12.5},
    "Public order and safety": {"National": 13.9, "Northeast": None, "Midwest": None, "South": 16.7, "West": 11.6},
    "Public assembly":         {"National": 12.1, "Northeast": 9.6,  "Midwest": 11.6, "South": 15.1, "West": 9.4},
    "Education":               {"National": 9.4,  "Northeast": 7.9,  "Midwest": 8.1,  "South": 11.4, "West": 9.0},
    "Service":                 {"National": 7.2,  "Northeast": 7.3,  "Midwest": 5.7,  "South": 9.0,  "West": 7.6},
}

# [FIX C22] EIA CBECS 2018 Table C22: electricity intensity by building activity SUBCATEGORY
# (kWh per sq ft per year, national only). Used when an archetype names a subcategory, so that
# intensity and floor area (Table B16, same subcategories) describe the same building population.
# Table C22 has no regional breakdown; C15 above remains the fallback for archetypes without a
# matching subcategory (EOC) and the regional reference for the national version.
# https://www.eia.gov/consumption/commercial/data/2018/ce/pdf/c22.pdf
CBECS_C22_KWH_PER_SQFT = {
    "Government":                      12.8,   # Office subcategory            (RSE 6.1)
    "Fire or police station":          12.8,   # Public order and safety       (RSE 12.6)
    "Library":                         15.7,   # Public assembly               (RSE 8.1)
    "Social or meeting":               10.3,   # Public assembly               (RSE 9.1)
    "K-12":                             9.1,   # Education
    "Vehicle storage or maintenance":   5.1,   # Service                       (RSE 10.8)
}

# Water supply: EPRI average ~1,824 kWh/MG (via ACEEE 2005). National, rounded.
# https://www.aceee.org/files/proceedings/2005/data/papers/SS05_Panel05_Paper05.pdf
WATER_KWH_PER_MG = {"default": 1800}

# Wastewater: NYSERDA ~1,700 kWh/MG for New York; EPRI national ~1,200 kWh/MG (via ACEEE 2009).
# https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Publications/Research/Environmental/Energy-Efficiency-Municipal-WWTP.pdf
# https://www.aceee.org/files/proceedings/2009/data/papers/6_83.pdf
WASTEWATER_KWH_PER_MG = {"NY": 1700, "default": 1200}

# Street lighting: equivalent full-load hours per year.
# Verified value: 4,169 hr/yr (load factor 0.476) calculated from National Grid's
# 2026 unitized Street Lighting class load shape (stlght26a.xlsx, EDI codes
# 1SC2L/1SC3L/1SC5L/1SC6L). Rounded to 4,170.
# https://www.nationalgridus.com/Upstate-NY-Business/Supply-Costs/Load-Profiles
# Cross-check: dusk-to-dawn lights burn ~4,000 hr/yr in utility tariffs
# https://interchange.puc.texas.gov/Documents/53719_508_1293872.PDF
STREETLIGHT_HOURS = 4170

# Traffic signals: ~2,000 kWh per LED intersection per year (triangulated estimate)
# https://assets.new.siemens.com/siemens/assets/api/uuid:d3061609-0903-4f20-b92d-40082626c622/background-traffic-light-e.pdf
TRAFFIC_KWH_PER_INTERSECTION = 2000

# ---------------------------------------------------------------------------
# SECTION 3: Archetype inputs (not location-specific)
#   area_sqft     CBECS 2018 Table B16, total floorspace / number of buildings (national)
#                 https://www.eia.gov/consumption/commercial/data/2018/bc/pdf/b16.pdf
#   load_factor   U.S. Navy UFC 3-501-03N (2004) ranges, applied with the Navy's
#                 selection guides, unless marked ASSUMPTION
#                 https://everyspec.com/DoD/DoD-UFC/ufc_3_501_03n-16jan2004_3797/
#                 (tables: https://cdn.ez-pdh.com/course-material/EE910-Introduction-to-Electric-Power-Requirements-for-Buildings2.pdf)
#                 Bound check: National Grid 2026 class load shapes give class
#                 load factors of 0.58 (SC-2 Demand) and 0.64 (SC-3 Secondary).
#                 Single buildings sit below their class, so building values
#                 above ~0.58 are implausible. Full basis: te3-load-factor-basis.md
#   tariff_class  generic class, mapped to the utility's label in Section 4
#   data_quality  "benchmark" | "provisional" (assumed input) | "low" (source conflict)
# ---------------------------------------------------------------------------
ARCHETYPE_INPUTS = {
    "Municipal Office Building": {
        "method": "building", "cbecs_category": "Office", "cbecs_subcategory": "Government",
        "area_sqft": 19600, "load_factor": 0.30,     # Navy admin office 20-35%, upper half
        "data_quality": "benchmark",
    },
    "Police Station": {
        "method": "building", "cbecs_category": "Public order and safety", "cbecs_subcategory": "Fire or police station",
        "area_sqft": 9600, "load_factor": 0.25,      # Navy police 20-25%, upper end (multi-shift)
        "data_quality": "benchmark",
    },
    "Fire Station": {
        "method": "building", "cbecs_category": "Public order and safety", "cbecs_subcategory": "Fire or police station",
        "area_sqft": 9600, "load_factor": 0.17,      # Navy fire 13-17%, upper end (multi-shift)
        "data_quality": "low",                       # Peak density ~9 W/sq ft fails sanity check
    },
    "Public Library": {
        "method": "building", "cbecs_category": "Public assembly", "cbecs_subcategory": "Library",
        "area_sqft": 17300, "load_factor": 0.33,     # Navy library 30-35%, midpoint
        "data_quality": "benchmark",
    },
    "Public School Facility": {
        "method": "building", "cbecs_category": "Education", "cbecs_subcategory": "K-12",
        "area_sqft": 40200, "load_factor": 0.20,     # Resolved via Navy academic peak density 5.55 W/sq ft
        "data_quality": "benchmark",
    },
    "Community Center": {
        "method": "building", "cbecs_category": "Public assembly", "cbecs_subcategory": "Social or meeting",
        "area_sqft": 11200, "load_factor": 0.25,     # Navy gymnasium 20-45%, lower half (intermittent)
        "data_quality": "benchmark",
    },
    "Water Treatment Plant": {
        "method": "water", "process": "water", "flow_mgd": 1.0,       # ASSUMPTION
        "load_factor": 0.60,                                           # ASSUMPTION (below Eugene 0.77)
        "data_quality": "provisional",
    },
    "Wastewater Treatment Plant": {
        "method": "water", "process": "wastewater", "flow_mgd": 1.0,  # ASSUMPTION
        "load_factor": 0.60,                                           # ASSUMPTION
        "data_quality": "provisional",
    },
    "Public Works Facility": {
        "method": "building", "cbecs_category": "Service", "cbecs_subcategory": "Vehicle storage or maintenance",
        "area_sqft": 7600, "load_factor": 0.20,      # Navy auto repair 15-20%; vehicle maintenance example 25%
        "data_quality": "benchmark",
    },
    "Smart Street Lighting System": {
        "method": "streetlight", "fixtures": 1000,   # ASSUMPTION; make user input
        "watts_per_fixture": 75,                     # ASSUMPTION; LED cobra heads ~40-150 W
        "data_quality": "provisional",
    },
    "Traffic Signal Network": {
        "method": "traffic", "intersections": 50,    # ASSUMPTION; make user input
        "load_factor": 1.0,                          # Verified: National Grid 2026 Traffic Signals class shape is flat (LF 1.00)
        "data_quality": "provisional",               # Intersection count and kWh/intersection remain assumptions
    },
    "Emergency Operations Center (EOC)": {
        "method": "building", "cbecs_category": "Public order and safety",
        "area_sqft": 15000, "load_factor": 0.40,     # ASSUMPTION area; Navy underground admin 35-40%
        "data_quality": "provisional",
    },
}

# ---------------------------------------------------------------------------
# SECTION 4: Tariff classification
#
# Each utility names and sizes its commercial classes differently, so the tool
# classifies archetypes into generic classes and only shows utility labels
# where they have been verified. The 100 kW split is National Grid's SC-2/SC-3
# boundary; it is used as a generic screening threshold elsewhere until each
# utility's thresholds are added.
# ---------------------------------------------------------------------------
LARGE_COMMERCIAL_KW = 100

UTILITY_TARIFF_LABELS = {
    # Verified: PSC No. 220 (SC-2, SC-3) and PSC No. 214 Outdoor Lighting.
    # Traffic signals: PSC No. 214 SC-4, inferred from National Grid load profile
    # EDI code 1SC4L ("L" codes are the lighting tariff). CONFIRM in PSC No. 214.
    "national grid": {"small_commercial": "SC-2", "large_commercial": "SC-3",
                      "outdoor_lighting": "PSC-214", "traffic_signal": "PSC-214 SC-4"},
    "niagara mohawk": {"small_commercial": "SC-2", "large_commercial": "SC-3",
                       "outdoor_lighting": "PSC-214", "traffic_signal": "PSC-214 SC-4"},
}

GENERIC_LABELS = {"small_commercial": "Small Commercial",
                  "large_commercial": "Large Commercial",
                  "outdoor_lighting": "Outdoor Lighting",
                  "traffic_signal": "Traffic Signal Service"}

# Default average commercial rate ($/kWh) when no OpenEI ZIP rate files are loaded.
# Source: U.S. EIA, 2024 Utility Bundled Retail Sales, Commercial (Form EIA-861, Table 7):
# Niagara Mohawk Power Corp. (National Grid) commercial revenue $413,300.7 thousand /
# sales 3,963,116 MWh = 10.43 cents/kWh (all-in: supply, delivery and demand charges).
# https://www.eia.gov/electricity/sales_revenue_price/pdf/table_7.pdf
# One utility-wide commercial average is applied to every tariff class. 2024 is the latest
# published table; EIA-861 2025 final data (released Oct 2026) should replace it.
DEFAULT_RATE = 0.1043
DEFAULT_RATE_SOURCE = "EIA-861 2024, Niagara Mohawk commercial average (Table 7)"

# Delivery demand charges ($/kW-month) used for battery peak shaving.
# Source: National Grid Upstate NY Business, Service Rates (PSC No. 220), accessed 2026-10-22:
#   SC-2 Demand: $18.93 per kW. SC-3 Secondary: $624.80 for the first 40 kW, then $15.62
#   per kW over 40 kW (the marginal rate avoided by shaving). Neither class has a per-kWh
#   delivery charge. PSC No. 214 lighting classes bill no demand charge.
# https://www.nationalgridus.com/Upstate-NY-Business/Rates/Service-Rates
UTILITY_DEMAND_CHARGES = {
    "national grid": {"small_commercial": 18.93, "large_commercial": 15.62,
                      "outdoor_lighting": 0.0, "traffic_signal": 0.0},
    "niagara mohawk": {"small_commercial": 18.93, "large_commercial": 15.62,
                       "outdoor_lighting": 0.0, "traffic_signal": 0.0},
}

LIGHTING_TARIFF_CLASSES = ("outdoor_lighting", "traffic_signal")


def tariff_class(inp, peak_kw):
    if inp["method"] == "streetlight":
        return "outdoor_lighting"
    if inp["method"] == "traffic":
        return "traffic_signal"
    # Annual peak is a summer maximum; a peak just over the threshold may not
    # sustain it for 12 months. A 5% margin is applied before assigning large commercial.
    return "large_commercial" if peak_kw > LARGE_COMMERCIAL_KW * 1.05 else "small_commercial"


def tariff_label(cls, utility_name):
    name = (utility_name or "").lower()
    for key, labels in UTILITY_TARIFF_LABELS.items():
        if key in name:
            return labels[cls]
    return GENERIC_LABELS[cls]


def average_commercial_rate(cls, loc):
    # The OpenEI value is a single utility-wide commercial average (EIA-861).
    # Without it, the documented New York default applies to every class.
    if loc["comm_rate"]:
        return round(loc["comm_rate"], 4)
    return DEFAULT_RATE


def demand_charge(cls, utility_name):
    """Delivery demand charge ($/kW-month) for the class, or None if not documented
    for this utility. Lighting tariffs return 0 (no demand charge)."""
    if cls in LIGHTING_TARIFF_CLASSES:
        return 0.0
    name = (utility_name or "").lower()
    for key, charges in UTILITY_DEMAND_CHARGES.items():
        if key in name:
            return charges[cls]
    return None

# ---------------------------------------------------------------------------
# SECTION 5: Derivation functions
# ---------------------------------------------------------------------------
def kwh_per_sqft(category, region):
    val = CBECS_KWH_PER_SQFT[category].get(region)
    if val is None:
        return CBECS_KWH_PER_SQFT[category]["National"], "CBECS 2018 Table C14 (national; regional value withheld)"
    return val, f"CBECS 2018 Table C15 ({region})"


def derive_annual_kwh(inp, loc):
    m = inp["method"]
    if m == "building":
        sub = inp.get("cbecs_subcategory")
        if sub:  # [FIX C22] subcategory intensity, national
            intensity, src = CBECS_C22_KWH_PER_SQFT[sub], f"CBECS 2018 Table C22 ({sub}, national)"
        else:
            intensity, src = kwh_per_sqft(inp["cbecs_category"], loc["census_region"])
        return inp["area_sqft"] * intensity, src
    if m == "water":
        table = WATER_KWH_PER_MG if inp["process"] == "water" else WASTEWATER_KWH_PER_MG
        kwh_mg = table.get(loc["state"], table["default"])
        return inp["flow_mgd"] * 365 * kwh_mg, f"{kwh_mg:,} kWh/MG"
    if m == "streetlight":
        return inp["fixtures"] * inp["watts_per_fixture"] / 1000 * STREETLIGHT_HOURS, "Fixtures x W x 4,170 hr"
    if m == "traffic":
        return inp["intersections"] * TRAFFIC_KWH_PER_INTERSECTION, "2,000 kWh per intersection"
    raise ValueError(f"Unknown method: {m}")


def derive_peak_kw(inp, annual_kwh):
    if inp["method"] == "streetlight":
        return 0          # Outdoor lighting tariffs bill per fixture, no demand charge
    return annual_kwh / (HOURS_PER_YEAR * inp["load_factor"])


def connected_kw(inp):
    if inp["method"] == "streetlight":
        return inp["fixtures"] * inp["watts_per_fixture"] / 1000
    return None

# ---------------------------------------------------------------------------
# SECTION 6: Descriptions and output
# ---------------------------------------------------------------------------
DESCRIPTIONS = {
    "Municipal Office Building": {
        "desc_simple": "Office buildings use most of their electricity during the day, making them strong candidates for solar systems that can directly reduce annual electricity costs.",
        "desc_technical": "Daytime-operated municipal facility. A benchmark load factor of about 0.30 indicates a pronounced weekday peak, and estimated peak demand sits near the 100 kW small/large commercial boundary. Solar generation aligns well with the occupied-hours load; demand charge exposure depends on whether the account is demand-metered.",
    },
    "Police Station": {
        "desc_simple": "Police stations operate around the clock, with a constant overnight load and higher daytime peaks. Solar and battery systems can reduce electricity costs while providing critical backup power during outages.",
        "desc_technical": "24-hour public safety facility. Despite continuous occupancy, a benchmark load factor of about 0.25 indicates peaks well above the overnight baseline. Strong candidate for solar cost offset and for battery-backed islanding to maintain operational continuity during grid disruptions.",
    },
    "Fire Station": {
        "desc_simple": "Fire stations have moderate energy use with high reliability requirements. Solar and storage can lower costs while ensuring backup power for emergency response readiness.",
        "desc_technical": "Public safety facility with high uptime requirements and a highly variable load (benchmark load factor about 0.17). Primary DER value lies in resilience: battery storage enables islanding to maintain critical systems and apparatus readiness during grid outages. Benchmark energy use is uncertain for this archetype; validate against utility bills.",
    },
    "Public Library": {
        "desc_simple": "Libraries operate during daytime hours with steady lighting and HVAC loads, making them well-suited for solar systems that directly offset electricity costs.",
        "desc_technical": "Daytime-operated public assembly facility with predictable occupancy-driven load patterns. Strong alignment between solar generation profile and building load schedule supports high self-consumption rates and meaningful electricity cost reduction.",
    },
    "Public School Facility": {
        "desc_simple": "Schools have high energy use during the day and seasonal swings, creating strong opportunities to reduce both electricity bills and peak demand costs using solar and battery systems.",
        "desc_technical": "Schools are associated with high daytime and seasonal load variability driven by student and staff occupancy schedules. Significant opportunity for both volumetric energy cost reduction and demand charge mitigation through integrated solar generation and battery-enabled peak shaving.",
    },
    "Community Center": {
        "desc_simple": "Community centers serve residents through scheduled programs and events, creating daytime and evening loads that solar systems can partly offset.",
        "desc_technical": "Public assembly facility with scheduled programming (CBECS median about 40 operating hours per week) and intermittent high-occupancy events. Solar provides cost offset during daytime use; battery storage adds value by reducing demand peaks during events.",
    },
    "Water Treatment Plant": {
        "desc_simple": "Water systems require constant energy with occasional spikes from pumping. Solar and storage can help reduce peak costs and improve system reliability.",
        "desc_technical": "Essential public utility asset with continuous baseline demand and periodic high-load pumping cycles. Offers strong potential for demand charge mitigation and resilience enhancement through coordinated solar generation and battery dispatch strategies.",
    },
    "Wastewater Treatment Plant": {
        "desc_simple": "Wastewater plants run 24/7 and consume large amounts of energy. The main benefit of this system is improving reliability and protecting operations during power outages while stabilizing long-term energy costs.",
        "desc_technical": "Energy-intensive critical infrastructure operating continuously, with aeration and pumping as the dominant loads. Primary value lies in resilience enhancement and long-term energy cost stabilization, given constant demand and operational risk exposure during grid disruptions.",
    },
    "Public Works Facility": {
        "desc_simple": "Public works yards house equipment storage, vehicle maintenance, and municipal operations with mostly daytime energy use.",
        "desc_technical": "Vehicle storage and maintenance facility with daytime-weighted load. Benchmark energy use excludes fleet EV charging; add charging load separately where applicable, as it materially changes demand and solar sizing.",
    },
    "Smart Street Lighting System": {
        "desc_simple": "Street lighting uses energy only at night, so solar panels cannot power it directly. Savings come from crediting daytime solar generation against the lighting bill.",
        "desc_technical": "Nighttime-only load billed under the utility's outdoor lighting tariff, typically per fixture with no demand charge. On-site solar cannot offset this load in real time; value depends on remote crediting mechanisms. Solar-plus-storage at individual fixtures is generally not cost-effective for utility-owned lighting.",
    },
    "Traffic Signal Network": {
        "desc_simple": "Traffic signals use relatively little energy but must stay operational at all times. The main value of this system is ensuring reliability and safety during outages.",
        "desc_technical": "Low-load but mission-critical infrastructure requiring continuous uptime. Primary value of DER integration lies in resilience, enabling localized backup power and microgrid isolation capabilities to ensure uninterrupted operation.",
    },
    "Emergency Operations Center (EOC)": {
        "desc_simple": "Emergency centers must stay operational at all times. Solar and battery systems help reduce costs while ensuring backup power during grid outages.",
        "desc_technical": "Mission-critical municipal facility requiring 100% operational continuity. It requires highest priority for resilience planning, with DER systems providing both cost mitigation and essential backup power through microgrid islanding capabilities.",
    },
}


def get_facility_profiles(zip_code=None, state=None):
    """Build all archetype profiles for a ZIP code. Without a ZIP (or without the
    OpenEI files), returns New York / National Grid defaults."""
    loc = resolve_location(zip_code or "12205", state=state)
    profiles = {}
    for name, inp in ARCHETYPE_INPUTS.items():
        annual, demand_src = derive_annual_kwh(inp, loc)
        peak = derive_peak_kw(inp, annual)
        cls = tariff_class(inp, peak)
        profiles[name] = {
            # Backward-compatible keys
            "demand": int(annual / 1000 + 0.5) * 1000,     # half-up rounding
            "base_kw": int(peak + 0.5),                    # ANNUAL PEAK kW
            "rate": average_commercial_rate(cls, loc),
            "tariff": tariff_label(cls, loc["utility_name"]),
            "desc_simple": DESCRIPTIONS[name]["desc_simple"],
            "desc_technical": DESCRIPTIONS[name]["desc_technical"],
            # New keys (safe to ignore in existing code)
            "tariff_class": cls,
            "demand_charge": demand_charge(cls, loc["utility_name"]),  # $/kW-month; None = not documented
            "load_factor": inp.get("load_factor") if inp["method"] != "streetlight"
                           else round(STREETLIGHT_HOURS / HOURS_PER_YEAR, 3),  # 0.476 (operating hours / 8,760)
            "connected_kw": connected_kw(inp),
            "data_quality": inp["data_quality"],
            "demand_source": demand_src,
            "rate_source": loc["rate_source"],
            "utility": loc["utility_name"],
            "census_region": loc["census_region"],
        }
    return profiles


# New York default, for code that still imports the constant
FACILITY_PROFILES = get_facility_profiles()


if __name__ == "__main__":
    import sys
    z = sys.argv[1] if len(sys.argv) > 1 else "12205"
    st = sys.argv[2] if len(sys.argv) > 2 else None
    profs = get_facility_profiles(z, st)
    first = next(iter(profs.values()))
    print(f"ZIP {z} | {first['census_region']} | {first['utility']}")
    print(f"{'Archetype':36} {'kWh/yr':>10} {'Peak kW':>8} {'Tariff':>17} {'Rate':>7}  Demand source")
    for n, p in profs.items():
        print(f"{n:36} {p['demand']:>10,} {p['base_kw']:>8} {p['tariff']:>17} {p['rate']:>7}  {p['demand_source']}")
