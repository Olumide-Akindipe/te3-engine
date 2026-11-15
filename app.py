import os
import re
import html
import datetime
import requests
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF
from fpdf.enums import XPos, YPos

# =====================================================================
# 1. APPLICATION INITIALIZATION & CONFIGURATION
# =====================================================================
load_dotenv()

# [FIX B8] set_page_config must be the first Streamlit command
st.set_page_config(
    page_title="TE3 Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

NREL_API_KEY = os.getenv("NREL_API_KEY")
if not NREL_API_KEY:
    try:
        NREL_API_KEY = st.secrets.get("NREL_API_KEY", None)
    except Exception:  # [FIX B8] no secrets.toml locally
        NREL_API_KEY = None
#✅For API security, dynamically routes to local .env first, then falls back to Streamlit Cloud Secrets
if not NREL_API_KEY:
    st.error("Configuration Error: NREL API key is missing.")
    st.stop() # Halts script compilation execution immediately


# MODERN ENTERPRISE UI STYLING INJECTION (CSS)
# =====================================================================
# 2. BRANDING, THEME, & UI SCALE INJECTION
# =====================================================================
st.markdown("""
    <style>
        /* 🟩 1. GLOBAL TYPOGRAPHY UPGRADE */
        html, body, [class*="css"], .stMarkdown p, .stMarkdown li {
            font-size: 1.15rem !important; /* Increases default prose base text */
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            line-height: 1.6 !important;
        }

        /* 🟩 2. GLOBAL CONTAINER PADDING */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 3rem !important;
        }

        /* 🟩 3. BRANDING HEADER CONTAINER (PRESERVED & SHARPENED) */
        .header-container {
            background: linear-gradient(135deg, #1f3a56 0%, #112233 100%);
            padding: 2.5rem;
            border-radius: 12px;
            color: #ffffff;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        .header-title {
            font-size: 2.5rem !important;
            font-weight: 800 !important;
            margin: 0 !important;
            color: #ffffff !important;
            letter-spacing: -0.5px;
        }
        .header-subtitle {
            font-size: 1.15rem !important;
            font-weight: 700 !important;
            color: #ffc107 !important;
            margin-top: 0.6rem !important;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* 🟩 4. SIDEBAR SCALE & CONTROL LABELS */
        .stSidebar {
            background-color: #f1f5f9 !important;
        }
        [data-testid="stSidebar"] label p {
            font-size: 1.2rem !important; /* Clarifies widget selection labels */
            font-weight: 600 !important;
            color: #1e293b !important;
        }

        /* /* 🟩 5. ENTERPRISE METRIC CARDS OVERHAUL (UPDATED FOR RESPONSIVE ZOOM) */
        div[data-testid="stMetric"] {
            background-color: #ffffff !important; /* Crisp white for card contrast */
            border: 1px solid #e2e8f0 !important;
            border-radius: 12px !important;
            padding: 1.5rem 1.25rem 1.25rem 1.25rem !important; /* Defensive padding against top edge clipping */
            box-shadow: 0 2px 5px rgba(0,0,0,0.02) !important;
            transition: all 0.25s ease-in-out !important;
        }
        div[data-testid="stMetric"]:hover {
            transform: translateY(-4px); /* Interactive vertical raise */
            box-shadow: 0 12px 20px -8px rgba(0, 0, 0, 0.15) !important;
            border-color: #cbd5e1 !important;
        }
        
        /* Metric Numbers & Labels Deep Nesting Targets */
        [data-testid="stMetricValue"] {
            font-size: 2.1rem !important; /* Strong executive data focus */
            font-weight: 700 !important;
            color: #0f172a !important;
            line-height: 1.2 !important;
            white-space: nowrap !important; /* 🟢 FIXED: Prevents numbers and units from clipping/wrapping on zoom */
        }
        [data-testid="stMetricLabel"] p {
            font-size: 1.1rem !important; /* Legible metric titles */
            font-weight: 500 !important;
            color: #475569 !important;
        }
        [data-testid="stMetricLabel"] {
            padding-top: 2px !important;
            margin-bottom: 6px !important;
            line-height: 1.3 !important;
        }
        [data-testid="stMetricLabel"] button {
            vertical-align: middle !important; /* Centers info tooltip icon helper */
        }

        /* 🟩 6. GEOSPATIAL & RESILIENCE BADGES */
        .location-badge {
            background-color: #f0f7ff;
            border-left: 5px solid #1f3a56;
            padding: 1rem;
            border-radius: 0 8px 8px 0;
            margin-bottom: 1.5rem;
            font-size: 1.1rem;
            color: #1e3a8a;
        }
        .resilience-badge {
            background-color: #fff7ed;
            border: 1px solid #ffedd5;
            border-left: 5px solid #ea580c;
            padding: 1.2rem;
            border-radius: 8px;
            margin-top: 1.5rem;
            color: #7c2d12;
            font-size: 1.1rem;
        }
        
        /* 🟩 7. INTERACTIVE INTERFACE BUTTONS */
        .stButton>button {
            border-radius: 8px !important;
            padding: 0.6rem 1.5rem !important;
            font-size: 1.1rem !important;
            font-weight: 600 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Modern, High-Impact Landing Page Hero Banner
st.markdown(
    """
    <div style="
        background-color: #112d4e; 
        padding: 35px 40px; 
        border-radius: 8px; 
        box-shadow: 0 4px 15px rgba(0,0,0,0.15);
        margin-bottom: 25px;
    ">
        <h1 style="
            color: #ffffff; 
            font-size: 42px; 
            font-weight: 800; 
            margin: 0 0 12px 0;
            display: flex;
            align-items: center;
            gap: 15px;
            letter-spacing: -0.5px;
        ">
            <span>⚡</span> TE3 ENGINE
        </h1>
        <p style="
            color: #ffcc00; 
            font-size: 18px; 
            font-weight: 700; 
            text-transform: uppercase;
            letter-spacing: 1.5px;
            margin: 0;
            line-height: 1.4;
        ">
            A Decision Support Tool for Energy Infrastructure Planning and Grid Resilience
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# [FIX R2] FACILITY PROFILES: derived from documented sources in facility_profiles.py (same keys as before:
# demand, base_kw, rate, tariff, desc_simple, desc_technical; plus tariff_class, demand_charge, load_factor,
# data_quality, demand_source, rate_source). New York values for Version 1. facility_profiles.py must be
# deployed in the same folder as this app.
from facility_profiles import FACILITY_PROFILES

# Reference Standards [FIX R2]
# Full source register with links: te3-archetype-data-sources.md. Principal sources:
# [1] U.S. EIA, 2018 CBECS Tables B16 (floor area), C14 and C15 (electricity intensity, national and by Census region).
#     https://www.eia.gov/consumption/commercial/data/2018/index.php
# [2] U.S. DoD, UFC 3-501-03N (2004), load factor ranges by facility type; checked against National Grid 2026 class
#     load shapes. https://everyspec.com/DoD/DoD-UFC/ufc_3_501_03n-16jan2004_3797/ ;
#     tables reproduced: https://cdn.ez-pdh.com/course-material/EE910-Introduction-to-Electric-Power-Requirements-for-Buildings2.pdf ;
#     https://www.nationalgridus.com/Upstate-NY-Business/Supply-Costs/Load-Profiles
# [3] EPRI via ACEEE (water, about 1,824 kWh/MG); NYSERDA (New York wastewater, about 1,700 kWh/MG).
#     https://www.aceee.org/files/proceedings/2005/data/papers/SS05_Panel05_Paper05.pdf
#     https://www.nyserda.ny.gov/-/media/Project/Nyserda/Files/Publications/Research/Environmental/Energy-Efficiency-Municipal-WWTP.pdf
# [4] Energy rate: U.S. EIA, 2024 Utility Bundled Retail Sales, Commercial (Form EIA-861, Table 7), Niagara Mohawk
#     10.43 cents/kWh. https://www.eia.gov/electricity/sales_revenue_price/pdf/table_7.pdf
# [5] Demand charges: National Grid Upstate NY Business Service Rates (PSC No. 220): SC-2 Demand $18.93/kW;
#     SC-3 Secondary $15.62/kW over 40 kW. https://www.nationalgridus.com/Upstate-NY-Business/Rates/Service-Rates
# [6] Tariff classes: National Grid PSC No. 220 and PSC No. 214 statements.
#     https://www.nationalgrid.com/document/598616/download ; https://www.nationalgrid.com/document/598626/download



# DR MARKET CONFIGURATION — NYISO SCR UPSTATE NY REFERENCE RATES
DR_CAPACITY_RATE = 20.00  # $/kW-year for capacity enrolled in NYISO DR programs (subject to market fluctuations and program eligibility) — upstate NY SCR conservative estimate
                           # [FIX R2] Basis: NYCA capacity prices of $2 to $6/kW-month since 2023 (Modo Energy, Nov 2025)
                           # and $5.83 to $6.74/kW-month in May to June 2026 monthly auctions (Rise Energy, May 2026).
                           # At the 2026-27 SCR capacity accreditation factor of 74.17% (NYISO, Rest of State) this
                           # implies about $18 to $53 per enrolled kW-year before aggregator fees; $20 is the low end.
                           # https://modoenergy.com/research/en/nyiso-capacity-market-december-auction-bess-revenues
                           # https://riseenergyservices.com/wp-content/uploads/2026/05/Rise-Energy-Services-May-2026-Market-Update.pdf
                           # https://www.nyiso.com/documents/20142/41593818/Final-Capacity-Accreditation-Factors-for-the-2026-2027-capability-year.pdf/83685470-882d-66d2-e6d8-68ed4d449e44

# [FIX DR] Research-based DR dispatch factors
# Definition: share of battery power (kW) offered to the NYISO Special Case Resources (SCR) program, after
# reserving battery capacity for backup power. Enrolled kW is further limited in the model (Section 4) by:
#   (a) the 4-hour SCR performance obligation: a battery can sustain kW x Min(duration / 4, 1) for 4 hours
#   (b) the facility peak demand: SCR performance is measured as a reduction from the facility's baseline load,
#       so a behind-the-meter battery cannot be credited for more than the load it serves
# Sources:
#   [DR-1] NYISO, "Demand Response: Special Case Resources" (4-hour minimum, 100 kW minimum by aggregation,
#          Average Coincident Load and Customer Baseline Load measurement, Responsible Interface Party enrollment)
#          https://www.nyiso.com/documents/20142/30712914/Demand-Response-Special-Case-Resources.pdf
#   [DR-2] NYISO, "Demand Response Resources," New York Market Orientation Course, March 2025 (SCRs are activated
#          when Operating Reserves are forecast to be short or during an actual Operating Reserve Deficiency)
#          https://www.nyiso.com/documents/20142/3037451/9-Demand-Response.pdf/3d224420-5b44-a282-5cc9-c082f497d112
#   [DR-3] Thompson, Song, Lekov and McKane, "Automated Demand Response Opportunities in Wastewater Treatment
#          Facilities," LBNL-1244E, 2008 (essential process equipment limits load shed)
#          https://www.osti.gov/biblio/944125
# Values marked ASSUMPTION are engineering judgments derived from the sources above, not published factors.
SC3_FIXED_BLOCK_KW = 40  # [FIX L3] National Grid SC-3 Secondary: first 40 kW billed as a block ($624.80), [5] above
SCR_MIN_DURATION_HOURS = 4  # [DR-1] SCR load reduction must be sustainable for at least 4 consecutive hours
# [FIX ITC] One notice text for the app and the PDF. Source: IRS Notice 2025-42; 2025 federal tax law (OBBBA).
# https://www.irs.gov/pub/irs-drop/n-25-42.pdf
ITC_TIMING_NOTE = ("The 30% federal Investment Tax Credit applies to solar only if the project began construction by "
                   "July 4, 2026 or be placed in service by December 31, 2027. Confirm eligibility with a tax expert. "
                   "Without the credit, net capital cost rises by 30% of the gross capital cost.")
DR_DISPATCH_FACTORS = {
    "Municipal Office Building": 1.0,           ## Non-critical load; full battery available (ASSUMPTION)
    "Police Station": 0.0,                      ## Battery reserved for backup; SCR events are called during system emergencies [DR-2]
    "Fire Station": 0.0,                        ## Battery reserved for backup; emergency response readiness [DR-2]
    "Public Library": 1.0,                      ## Non-critical load; full battery available (ASSUMPTION)
    "Public School Facility": 0.5,              ## Summer closure lowers load during summer SCR events, limiting the measured baseline [DR-1] (ASSUMPTION)
    "Community Center": 1.0,                    ## Non-critical load; full battery available (ASSUMPTION)
    "Water Treatment Plant": 0.5,               ## Critical infrastructure; half of battery reserved for backup [DR-3] (ASSUMPTION)
    "Wastewater Treatment Plant": 0.5,          ## Critical infrastructure; essential process loads limit shed [DR-3] (ASSUMPTION)
    "Public Works Facility": 1.0,               ## Non-critical daytime load; full battery available (ASSUMPTION)
    "Smart Street Lighting System": 0.0,        ## Nighttime load, not coincident with summer afternoon SCR events
    "Traffic Signal Network": 0.0,              ## Zero curtailment permitted for public safety
    "Emergency Operations Center (EOC)": 0.0,   ## Mission-critical; battery reserved for backup [DR-2]
}

# =====================================================================
# 2. USER INTERFACE LAYER (SIDEBAR CONTROLS)
# =====================================================================
#Introducing session state to retain user memory
defaults = {
    "simulation_active": False
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

st.markdown(
    """
    <style>
        /* 1. Fix the text input container alignment to stop overlapping */
        div[data-testid="stTextInput"] {
            margin-bottom: 25px !important;
        }
        
        /* 2. */
        section[data-testid="stSidebar"] div[data-testid="stForm"] {
            border: none !important;
            background: transparent !important;
            padding: 0px !important;
            box-shadow: none !important;
            width: 100% !important;
        }


        /* 3. Button core styling */
        button[data-testid="stBaseButton-secondary"] {
            background-color: #218838 !important;  /* Shaded Green */
            border-radius: 8px !important;          /* Rounded modern edge profiles */
            border: none !important;
            padding: 14px 0px !important;           /* Clickable touch-target height */
            width: 100% !important;                 /* Force button to span across full sidebar layout width */
            box-shadow: 0 4px 12px rgba(33, 136, 56, 0.25) !important; /* Soft emerald drop-glow */
            transition: all 0.2s ease-in-out !important;
            display: block !important;
        }

        /* 4. Button Text */
        button[data-testid="stBaseButton-secondary"] p {
            color: #FFFFFF !important;             /* Force pure high-contrast white text */
            font-size: 17px !important;             /* Prominent primary typography scale */
            font-weight: 700 !important;             /* Heavy bold line thickness weight */
            letter-spacing: 0.5px !important;
            margin: 0px !important;
            padding: 0px !important;
            text-align: center !important;
        }

        /* 5. Interactive hover performance states */
        button[data-testid="stBaseButton-secondary"]:hover {
            background-color: #1e7e34 !important;
            box-shadow: 0 6px 18px rgba(30, 126, 52, 0.4) !important;
            transform: translateY(-1px) !important; /* Subtle tactile lift interaction */
        }

        /* 6. Interactive click down execution states */
        button[data-testid="stBaseButton-secondary"]:active {
            transform: translateY(1px) !important;  /* Micro-click compression feedback interaction */
        }
    </style>
    """,
    unsafe_allow_html=True
)


st.sidebar.header("⚙️ System Configuration")
# Section 1: Geographic Input
raw_zip = st.sidebar.text_input("Enter ZIP Code:", value="", max_chars=5, placeholder="e.g., 10001")

# Section 2: Infrastructure Profile
st.sidebar.markdown("---")
st.sidebar.markdown("### 🏢 Infrastructure Profile")
facility_selection = st.sidebar.selectbox("Asset Classification Type:", list(FACILITY_PROFILES.keys()))
system_capacity_kw = st.sidebar.slider("Proposed Solar Capacity (kW):", min_value=10, max_value=500, value=50, step=10)

# Section 3: Interconnection Strategy
st.sidebar.markdown("---")
st.sidebar.markdown("### 🔌 Interconnection Strategy")
enable_battery = st.sidebar.checkbox("Deploy Battery Storage (BESS)", value=False)

bess_duration = 2
if enable_battery:
    bess_duration = st.sidebar.selectbox(
        "BESS Capacity Sizing:",
        options=[2, 4],
        format_func=lambda x: f"{x}-Hour Setup (Battery Peak Shaving Focus)" if x == 2 else f"{x}-Hour Setup (Emergency Reserves Focus)"
    )

# Section 3: Interconnection Strategy (continued)
enable_net_metering = st.sidebar.checkbox("Enable Net Energy Metering (NEM)", value=False)
# [FIX S1] Peak shaving needs a demand charge; lighting tariffs (PSC No. 214) have none
shaving_excluded = not FACILITY_PROFILES[facility_selection].get("demand_charge")
shaving_disabled = (not enable_battery) or shaving_excluded
dr_disabled = not enable_battery
# [FIX UI1] Clear a stored tick before a checkbox is drawn disabled, so a greyed-out box never shows as ticked
if shaving_disabled:
    st.session_state["cb_peak_shaving"] = False
if dr_disabled:
    st.session_state["cb_demand_response"] = False
# [FIX UI2] Hover help explains why an option is greyed out
enable_peak_shaving = st.sidebar.checkbox(
    "Enable Battery Peak Shaving",
    key="cb_peak_shaving",
    disabled=shaving_disabled,
    help=("Unavailable: this facility's tariff has no demand charge." if shaving_excluded
          else "Requires battery storage. Check 'Deploy Battery Storage (BESS)' to enable." if not enable_battery
          else "Uses the battery to lower the facility's monthly peak demand charge.")
)
enable_demand_response = st.sidebar.checkbox(
    "Enable NYISO DR Market VPP",
    key="cb_demand_response",
    disabled=dr_disabled,
    help=("Requires battery storage. Check 'Deploy Battery Storage (BESS)' to enable." if dr_disabled
          else "Enrolls battery capacity in the NYISO Special Case Resources (SCR) program.")
)
# [FIX B6] A disabled checkbox keeps its last value, so battery-dependent options are forced off without a battery
enable_peak_shaving = enable_peak_shaving and enable_battery and not shaving_excluded
if shaving_excluded:
    st.sidebar.caption("Peak shaving unavailable: this facility's tariff has no demand charge.")
enable_demand_response = enable_demand_response and enable_battery

# Islanding disabled for unmetered facility types where base_kw = 0
islanding_excluded = FACILITY_PROFILES[facility_selection]["base_kw"] == 0

if islanding_excluded:  # [FIX UI1]
    st.session_state["cb_islanding"] = False
enable_islanding = st.sidebar.checkbox(
    "Enable Microgrid Islanding (Backup for Grid Outages)",
    key="cb_islanding",
    disabled=islanding_excluded,
    help="Models backup power duration during a grid outage. Requires battery storage."  # [FIX UI2]
)

if islanding_excluded:
    st.sidebar.caption(
        "Islanding unavailable for this facility type. "
        "Unmetered accounts have no defined critical load baseline."
    )
elif enable_islanding and not enable_battery:  # [FIX UI3]
    st.sidebar.caption("Backup duration requires battery storage. Check 'Deploy Battery Storage (BESS)' to model it.")

# Section 4: Submit Button
st.sidebar.markdown("---")
# [FIX L7] After the first run, sidebar changes update results automatically; the button then reads "Update"
run_label = "🔄 Update Evaluation" if st.session_state.simulation_active else "🚀 Run Techno-Economic Evaluation"
try:
    submit_button = st.sidebar.button(label=run_label, width="stretch")  # [FIX M4] Streamlit 1.46+
except TypeError:
    submit_button = st.sidebar.button(label=run_label, use_container_width=True)  # older Streamlit

# Initiating String validation immediately the user clicks submit button

clean_zip = raw_zip.strip()
is_valid_zip = bool(re.match(r"^\d{5}$", clean_zip))

#If the submit button is pushed and the ZIP is valid, set memory lock to True
if submit_button and is_valid_zip:
    st.session_state.simulation_active = True

if submit_button and not is_valid_zip:
    st.sidebar.warning("⚠️ Enter a valid 5-digit ZIP code.")

# If the user submitted the form but the ZIP code is invalid, show a warning message in the sidebar and prevent the model from running until a valid ZIP code is entered. This ensures that the geolocation engine receives proper input and can function correctly.
if not is_valid_zip and clean_zip and not submit_button:
    st.sidebar.warning("⚠️ Enter a valid 5-digit ZIP code.")


# =====================================================================
# 3. DYNAMIC GEOLOCATION ENGINE
# =====================================================================
class GeocodeError(Exception):
    """[FIX M1] Raised for network or service errors, so a temporary failure is not cached for an hour."""


@st.cache_data(ttl=3600)
def get_coordinates_from_zip(zipcode):
    geo_url = "https://nominatim.openstreetmap.org/search"
    params = {"postalcode": zipcode, "country": "United States", "format": "json", "addressdetails": 1}
    # [FIX L5] Nominatim usage policy asks for an identifying User-Agent with a contact
    headers = {"User-Agent": "TE3-Engine/1.0 (municipal energy screening tool; https://github.com/Olumide-Akindipe)"}
    try:
        geo_response = requests.get(geo_url, params=params, headers=headers, timeout=10)
    except requests.RequestException as e:
        raise GeocodeError(f"the location service could not be reached ({type(e).__name__})") from None
    if geo_response.status_code != 200:
        raise GeocodeError(f"the location service returned HTTP {geo_response.status_code}")
    results = geo_response.json()
    if results:
        location_data = results[0]
        address_block = location_data.get("address", {})
        location_name = (
            address_block.get("city") or 
            address_block.get("town") or 
            address_block.get("village") or 
            address_block.get("hamlet") or 
            address_block.get("municipality") or 
            address_block.get("county") or 
            f"Region {zipcode}"
        )
        state = address_block.get("state") or address_block.get("state_code") or ""
        display_name = f"{location_name}, {state}".strip(", ")
        return {
            "lat": float(location_data["lat"]),
            "lon": float(location_data["lon"]),
            "display_name": display_name,
            "state": state,  # [FIX B1]
            "state_code": address_block.get("ISO3166-2-lvl4", "")
        }
    return None  # ZIP code not found (safe to cache)

# =====================================================================
# 4. TECHNO-ECONOMIC MODEL
# =====================================================================
def run_techno_economic_modeling(sun_hours, system_kw, facility_type, battery_active, duration, net_metering_active, shaving_active, dr_active, islanding_active):
    # 🟢 sun_hours extracted from the integrated API dataset is already an annualized resource vector.
    # Solar Generation and Load Matching Calculation (with 14% system losses factored in)
    annual_generation_kwh = system_kw * sun_hours * 0.86 

    # Calculates how much of the facility's annual electricity usage is covered by the new solar array capped at 100%. 
    annual_demand_kwh = FACILITY_PROFILES[facility_type]["demand"]
    grid_displacement_percentage = min((annual_generation_kwh / annual_demand_kwh) * 100, 100.0)
    
    # Average commercial rate for the facility (facility_profiles.py)
    active_rate = FACILITY_PROFILES[facility_type]["rate"]
    
    base_savings = min(annual_generation_kwh, annual_demand_kwh) * active_rate
    excess_generation = max(0.0, annual_generation_kwh - annual_demand_kwh)
    net_metering_revenue = (excess_generation * active_rate) if net_metering_active else 0.0
    
    shaving_savings = 0.0
    if battery_active and shaving_active:
        shaved_kw = min(system_kw * 0.40, FACILITY_PROFILES[facility_type]["base_kw"])  # [FIX A1] cap at facility peak demand
        if FACILITY_PROFILES[facility_type].get("tariff_class") == "large_commercial":
            # [FIX L3] SC-3 Secondary bills the first 40 kW as a fixed block; only kW above 40 is avoided per kW
            shaved_kw = min(shaved_kw, max(0.0, FACILITY_PROFILES[facility_type]["base_kw"] - SC3_FIXED_BLOCK_KW))
        # [FIX R2] Tariff delivery demand charge ($/kW-month) replaces the unsourced $12.00
        shaving_savings = shaved_kw * (FACILITY_PROFILES[facility_type].get("demand_charge") or 0.0) * 12 
        
    dr_revenue = 0.0
    dr_load_reduction_kw = 0.0
    if battery_active and dr_active:
        # [FIX DR] Enrolled kW = battery kW x dispatch factor x 4-hour sustainability, capped at facility peak demand
        scr_duration_factor = min(duration / SCR_MIN_DURATION_HOURS, 1.0)
        dr_load_reduction_kw = min(
            system_kw * DR_DISPATCH_FACTORS.get(facility_type, 0.0) * scr_duration_factor,
            FACILITY_PROFILES[facility_type]["base_kw"],
        )
        dr_revenue = dr_load_reduction_kw * DR_CAPACITY_RATE

    optimized_annual_savings = base_savings + net_metering_revenue + shaving_savings + dr_revenue
    
    #Capital Expenditures (CapEx) and Incentives
    base_capex = system_kw * 2500
    if battery_active:
        base_capex += (system_kw * (600 if duration == 2 else 950))
    if islanding_active and battery_active:  # [FIX A3] islanding hardware cost applies only with storage
        base_capex *= 1.15 
        
    net_capex = base_capex * 0.70 
    payback_years = net_capex / optimized_annual_savings if optimized_annual_savings > 0 else None  # [FIX B2] None = no payback
    
    autonomy_hours= 0.0
    if islanding_active and battery_active:  # [FIX A3] grid-tied solar alone cannot island; backup requires storage
        battery_capacity_kwh = system_kw * duration if battery_active else 0.0
        base_kw = FACILITY_PROFILES[facility_type]["base_kw"]
        annual_demand_kwh = FACILITY_PROFILES[facility_type]["demand"]
        daily_sun_hours = sun_hours / 365

        if base_kw > 0:
            avg_hourly_demand = base_kw
        elif annual_demand_kwh > 0:
            avg_hourly_demand = annual_demand_kwh / 8760
        else:
            avg_hourly_demand = 0.0

        if avg_hourly_demand > 0:
            autonomy_hours = (battery_capacity_kwh / avg_hourly_demand) + ((system_kw * daily_sun_hours * 0.5) / avg_hourly_demand)
        
    return {
        "generation": round(annual_generation_kwh, 1),
        "demand": annual_demand_kwh,
        "displacement": round(grid_displacement_percentage, 1),
        "savings": round(optimized_annual_savings, 2),
        "base_savings": round(base_savings, 2),
        "nem_revenue": round(net_metering_revenue, 2),
        "shaving_savings": round(shaving_savings, 2),
        "dr_revenue": round(dr_revenue, 2),
        "dr_load_reduction": round(dr_load_reduction_kw, 1),
        "capex": round(net_capex, 2),
        "payback": round(payback_years, 1) if payback_years is not None else None,
        "excess": round(excess_generation, 1),
        "gross_capex": round(base_capex, 2),
        "ira_credit": round(base_capex * 0.30, 2),
        "autonomy": round(autonomy_hours, 1)
    }

# =====================================================================
# 5. PDF REPORT (PRE-FEASIBILITY SCREENING REPORT)
# =====================================================================
# [FIX PDF] Report revised for Version 1 release (te3-release-plan-and-pdf-review.md, P1 to P43):
# key results on page 1, facility load and cost breakdown shown, plain terminology, methods stated as the code
# computes them, data vintages, screening notes, Unicode-safe text, fpdf2 new_x/new_y (M4).
TE3_VERSION = "1.0"
REPORT_NAVY = (31, 58, 86)
REPORT_AMBER = (230, 150, 30)
REPORT_BORDER = (203, 213, 225)
REPORT_TEXT = (40, 40, 40)
REPORT_MUTED = (110, 110, 110)

# Characters outside Latin-1 cannot be drawn with the built-in Helvetica font [FIX P43]
_PDF_CHAR_MAP = {"–": "-", "—": "-", "‘": "'", "’": "'", "“": '"', "”": '"',
                 "•": "-", "…": "...", "×": "x", "≤": "<=", "≥": ">=", "→": "->"}


def pdf_safe(text):
    text = "".join(_PDF_CHAR_MAP.get(ch, ch) for ch in str(text))
    return text.encode("latin-1", "replace").decode("latin-1")


def fmt_money(value):
    return f"${value:,.2f}"


class BrandedExecutivePDF(FPDF):
    def normalize_text(self, text):
        return super().normalize_text(pdf_safe(text))  # [FIX P43]

    def header(self):
        # Navy accent stripe down the left margin
        self.set_fill_color(*REPORT_NAVY)
        self.rect(0, 0, 8, 297, "F")
        self.set_left_margin(15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(*REPORT_MUTED)
        self.cell(0, 5, "TE3 Engine | Pre-Feasibility Screening Report", align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        self.set_text_color(0, 0, 0)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | Solar resource: NSRDB via PVWatts v8 (National Laboratory of the Rockies)", align="C")


def _section_title(pdf, text):
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*REPORT_NAVY)
    pdf.cell(0, 7, text, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(1)


def _table_header(pdf, widths, labels):
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(*REPORT_NAVY)
    pdf.set_text_color(255, 255, 255)
    for i, label in enumerate(labels):
        last = i == len(labels) - 1
        pdf.cell(widths[i], 6.5, f" {label}", border=1, fill=True,
                 new_x=XPos.LMARGIN if last else XPos.RIGHT, new_y=YPos.NEXT if last else YPos.TOP)


def _table_rows(pdf, widths, rows, emphasis_from=None, font_size=8.5):
    """Rows of text cells. Each row's height fits its longest cell, so no text is cut off."""
    line_h = 4.2
    for idx, row in enumerate(rows):
        bold = emphasis_from is not None and idx >= emphasis_from
        pdf.set_font("Helvetica", "B" if bold else "", font_size)
        n_lines = max(len(pdf.multi_cell(widths[i], line_h, f" {cell}", align="L", dry_run=True, output="LINES"))
                      for i, cell in enumerate(row))
        row_h = max(6.5, n_lines * line_h + 2.2)
        if pdf.get_y() + row_h > pdf.page_break_trigger:
            pdf.add_page()
        if bold:
            pdf.set_fill_color(254, 247, 234)
            pdf.set_text_color(150, 75, 0)
        else:
            pdf.set_fill_color(*((248, 250, 252) if idx % 2 else (255, 255, 255)))
            pdf.set_text_color(*REPORT_TEXT)
        x0, y0 = pdf.get_x(), pdf.get_y()
        for i, cell in enumerate(row):
            pdf.set_xy(x0 + sum(widths[:i]), y0)
            pdf.cell(widths[i], row_h, "", border=1, fill=True)
            pdf.set_xy(x0 + sum(widths[:i]), y0 + 1.1)
            pdf.multi_cell(widths[i], line_h, f" {cell}", align="L")
        pdf.set_xy(x0, y0 + row_h)
    pdf.set_text_color(0, 0, 0)


def _paragraph(pdf, text, size=9.5, style="", color=REPORT_TEXT, line_h=5):
    pdf.set_font("Helvetica", style, size)
    pdf.set_text_color(*color)
    pdf.multi_cell(0, line_h, text, align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)


def build_screening_notes(sun_hours, capacity, facility, battery, duration, net_meter, shaving, dr, island,
                          results, dr_dispatch_factor):
    """[FIX NOTES] Rule-based screening notes derived from this configuration's own results.
    They state facts and options; they are not design recommendations."""
    profile = FACILITY_PROFILES[facility]
    demand = profile["demand"]
    generation = results["generation"]
    notes = []

    # Array size relative to annual use
    if generation > demand:
        match_kw = max(10, int(round(capacity * demand / generation / 10.0)) * 10)
        surplus_pct = (generation / demand - 1) * 100
        if net_meter:
            notes.append(f"Solar output exceeds the facility's annual use by {surplus_pct:.0f}%. The surplus is credited at the "
                         f"average commercial rate in this model; under New York VDER rules export value may be lower. "
                         f"An array of about {match_kw} kW would match annual use.")
        else:
            notes.append(f"Solar output exceeds the facility's annual use by {surplus_pct:.0f}%, and the surplus earns no credit "
                         f"because net metering is not selected. An array of about {match_kw} kW would match annual use, "
                         f"or enable net metering to value the surplus.")
    elif results["displacement"] < 50:
        match_kw = int(round(capacity * demand / max(generation, 1) / 10.0)) * 10
        size_note = (f"About {match_kw} kW would match annual use" if match_kw <= 500
                     else "Matching annual use would need more than the 500 kW modeled range")
        notes.append(f"Solar meets {results['displacement']:.1f}% of annual use. {size_note}, subject to roof or ground area "
                     f"and interconnection limits.")

    # Battery value
    demand_charge = profile.get("demand_charge") or 0.0
    if not battery and demand_charge > 0:
        notes.append(f"This facility's tariff ({profile['tariff']}) has a demand charge of ${demand_charge:.2f}/kW-month. "
                     f"Peak shaving and NYISO demand response require battery storage and are not included in these results.")
    if battery:
        no_battery = run_techno_economic_modeling(sun_hours, capacity, facility, False, duration, net_meter,
                                                  False, False, False)
        added_capex = results["capex"] - no_battery["capex"]
        added_value = results["savings"] - no_battery["savings"]
        if no_battery["payback"] is not None:
            notes.append(f"Without the battery, net CapEx would be {fmt_money(no_battery['capex'])} and simple payback "
                         f"{no_battery['payback']} years. The battery adds {fmt_money(added_capex)} of net CapEx and "
                         f"{fmt_money(added_value)} per year in modeled value.")
        if demand_charge == 0:
            notes.append("This facility's tariff has no demand charge, so the battery's value here is backup power only.")
        if dr and dr_dispatch_factor == 0:
            notes.append("NYISO demand response was selected, but this facility type keeps its battery in reserve for backup "
                         "power during grid emergencies, so no capacity is enrolled.")
        elif dr and duration == 2 and results["dr_load_reduction"] < profile["base_kw"]:
            notes.append("NYISO counts only the power a battery can sustain for 4 hours. A 4-hour battery would roughly "
                         "double the enrolled capacity, up to the facility peak.")

    if island and not battery:
        notes.append("Islanding was selected without battery storage, so backup duration is not modeled.")

    if facility in ("Smart Street Lighting System",):
        notes.append("Street lighting operates at night. Savings assume solar output is credited against the lighting "
                     "account over the year, which depends on a remote crediting arrangement with the utility.")

    notes.append(ITC_TIMING_NOTE)  # [FIX ITC] shown on every run
    quality = profile.get("data_quality", "benchmark")
    if quality != "benchmark":
        notes.append(f"The facility load is a {('low quality' if quality == 'low' else 'provisional')} benchmark. "
                     f"Confirm annual use and peak demand with 12 months of utility bills before design.")
    else:
        notes.append("The facility load is a national benchmark for this building type. Confirm annual use and peak "
                     "demand with 12 months of utility bills before design.")
    return notes


def generate_comprehensive_pdf(zipcode, city, sun_hours, capacity, facility, battery, duration, net_meter, shaving, dr,
                               island, results, dr_dispatch_factor=0.0, dr_capacity_rate=20.00):
    profile = FACILITY_PROFILES[facility]
    rate = profile["rate"]
    tariff = profile["tariff"]
    demand_charge = profile.get("demand_charge") or 0.0
    report_date = datetime.date.today().strftime("%B %d, %Y")
    backup_modeled = island and battery and results.get("autonomy", 0) > 0
    widths2 = [80, 100]

    pdf = BrandedExecutivePDF()
    pdf.set_title(f"TE3 Pre-Feasibility Screening Report - {facility} - {zipcode}")  # [FIX P42]
    pdf.set_author("TE3 Engine")
    pdf.set_auto_page_break(auto=True, margin=18)

    # ---------------- PAGE 1: title, key results, summary, screening notes ----------------
    pdf.add_page()
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*REPORT_NAVY)
    pdf.cell(0, 10, "Solar and Storage Pre-Feasibility Screening Report", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.set_draw_color(*REPORT_AMBER)
    pdf.set_line_width(0.8)
    pdf.line(15, pdf.get_y() + 1, 195, pdf.get_y() + 1)
    pdf.set_draw_color(*REPORT_BORDER)  # [FIX P36] reset so tables get thin neutral borders
    pdf.set_line_width(0.2)
    pdf.ln(4)
    _paragraph(pdf, f"{facility}  |  {city} (ZIP {zipcode})  |  {report_date}  |  Version {TE3_VERSION}",
               size=9, color=REPORT_MUTED)
    pdf.ln(2)

    # Key results box [FIX P1]
    tiles = [("Annual savings", f"{fmt_money(results['savings'])} / year"),
             ("Net capital cost (after 30% ITC*)", fmt_money(results["capex"])),
             ("Simple payback", f"{results['payback']} years" if results["payback"] is not None else "N/A (no savings)"),
             ("Annual solar generation", f"{results['generation']:,.0f} kWh"),
             ("Share of annual use met by solar", f"{results['displacement']}%"),
             ("Backup duration (screening estimate)", f"{results['autonomy']} hours" if backup_modeled else "Not modeled")]
    box_w, box_h = 60, 17
    y_start = pdf.get_y()
    for i, (label, value) in enumerate(tiles):
        x = 15 + (i % 3) * box_w
        y = y_start + (i // 3) * box_h
        pdf.set_fill_color(240, 244, 248)
        pdf.rect(x, y, box_w - 2, box_h - 2, "F")
        pdf.set_xy(x + 2, y + 2)
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(*REPORT_MUTED)
        pdf.cell(box_w - 6, 4, label)
        pdf.set_xy(x + 2, y + 7)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*REPORT_NAVY)
        pdf.cell(box_w - 6, 6, value)
    pdf.set_xy(15, y_start + 2 * box_h + 1)

    _section_title(pdf, "Summary")
    sources = ["solar energy used on site"]
    if net_meter and results.get("nem_revenue", 0) > 0:
        sources.append("export credits")
    if shaving and results.get("shaving_savings", 0) > 0:
        sources.append("lower demand charges")
    if dr and results.get("dr_revenue", 0) > 0:
        sources.append("NYISO demand response payments")
    savings_sources = sources[0] if len(sources) == 1 else ", ".join(sources[:-1]) + " and " + sources[-1]
    resilience = ("With battery storage and islanding, the system can also supply part of the facility's load during a grid "
                  "outage; the backup duration above is a screening estimate. "
                  if backup_modeled else "")
    summary = (
        "Municipalities face rising energy costs and greater exposure to grid disruptions. Solar photovoltaic (PV) systems, "
        "with optional battery energy storage (BESS), can lower electricity costs and, where storage is included, support "
        "critical services during outages.\n\n"
        f"This report screens a {capacity} kW solar array"
        f"{f' with a {duration}-hour battery' if battery else ''} at a {facility.lower()} in {city} (ZIP {zipcode}). "
        f"Savings come from {savings_sources}. "
        f"{resilience}"
        "Results use national building benchmarks, typical-year solar data and current New York utility rates. They are "
        "screening estimates intended to decide whether a detailed study is warranted, not a design or an investment-grade "
        "analysis. Confirm facility use with 12 months of utility bills before design."  # [FIX P2, P15, P18]
    )
    _paragraph(pdf, summary)

    _section_title(pdf, "Screening Notes")
    notes = build_screening_notes(sun_hours, capacity, facility, battery, duration, net_meter, shaving, dr, island,
                                  results, dr_dispatch_factor)
    for note in notes:
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(*REPORT_TEXT)
        pdf.multi_cell(0, 4.8, f"-  {note}", align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(1)

    # ---------------- PAGE 2: configuration and results ----------------
    pdf.add_page()
    _section_title(pdf, "1. Project Configuration")
    if dr and dr_dispatch_factor == 0:
        dr_text = "Not eligible (battery reserved for backup)"  # [FIX P12]
    elif dr:
        dr_text = f"Included: ${dr_capacity_rate:,.2f}/kW-year; {int(dr_dispatch_factor * 100)}% of battery power offered"
    else:
        dr_text = "Not included"
    if island and not battery:
        island_text = "Selected; not modeled (requires battery storage)"
    elif island:
        island_text = "Modeled (see backup duration)"
    else:
        island_text = "Not included"
    config_rows = [
        ["Location", f"{city} (ZIP {zipcode})"],
        ["Facility type", facility],
        ["Solar resource", f"{round(sun_hours / 365, 2) if sun_hours else 0} peak sun hours per day (NSRDB via PVWatts)"],
        ["Utility tariff (National Grid)", f"{tariff}; average commercial rate ${rate:.4f}/kWh"],
        ["Demand charge", f"${demand_charge:.2f}/kW-month" if demand_charge else "None (lighting tariff)"],
        ["Solar capacity", f"{capacity} kW DC"],
        ["Battery storage", f"{capacity} kW, {duration} hours ({capacity * duration} kWh)" if battery else "Not included"],
        ["Net energy metering", "Included (exports credited at the average commercial rate)" if net_meter
                                 else "Not included (exports not credited)"],
        ["Peak shaving", f"Included ({tariff} demand charge)" if shaving else "Not included"],
        ["NYISO demand response (SCR)", dr_text],
        ["Microgrid islanding", island_text],
    ]
    _table_header(pdf, widths2, ["Setting", "Value"])
    _table_rows(pdf, widths2, config_rows)

    _section_title(pdf, "2. Results")
    result_rows = [
        ["Facility annual electricity use (benchmark)", f"{profile['demand']:,} kWh / year (data quality: {profile.get('data_quality', 'benchmark')})"],
        ["Facility peak demand (estimated)", f"{profile['base_kw']} kW" if profile["base_kw"] else "None billed (lighting tariff)"],
        ["Annual solar generation", f"{results['generation']:,.1f} kWh / year"],
        ["Share of annual use met by solar", f"{results['displacement']}%"],
        ["Energy cost savings (on-site use)", f"{fmt_money(results['base_savings'])} / year"],
        ["Peak shaving savings", f"{fmt_money(results['shaving_savings'])} / year" if shaving
                                 else ("Not available (no demand charge)" if demand_charge == 0 else "Not included")],
    ]
    if net_meter:
        result_rows += [["Net metering export credit", f"{fmt_money(results['nem_revenue'])} / year"],
                        ["Solar exported to the grid", f"{results['excess']:,.0f} kWh / year"]]
    if dr and dr_dispatch_factor == 0:
        result_rows.append(["NYISO demand response revenue", "Not eligible (battery reserved for backup)"])
    elif dr:
        result_rows.append(["NYISO demand response revenue",
                            f"{fmt_money(results['dr_revenue'])} / year ({results['dr_load_reduction']:,.1f} kW enrolled)"])
    result_rows += [
        ["Gross capital cost", fmt_money(results["gross_capex"])],  # [FIX P5]
        ["Federal ITC (30%)*", f"- {fmt_money(results['ira_credit'])}"],
    ]
    emphasis_start = len(result_rows)
    result_rows += [
        ["Total annual savings", f"{fmt_money(results['savings'])} / year"],
        ["Net capital cost", fmt_money(results["capex"])],
        ["Simple payback", f"{results['payback']} years" if results["payback"] is not None else "N/A (no annual savings)"],
    ]
    if backup_modeled:
        result_rows.append(["Backup duration (screening estimate)", f"{results['autonomy']} hours"])
    _table_header(pdf, widths2, ["Metric", "Value"])
    _table_rows(pdf, widths2, result_rows, emphasis_from=emphasis_start)

    pdf.ln(1.5)
    footnotes = ["* Assumes eligibility for the 30% federal Investment Tax Credit (elective pay for public entities). "
                 "Under the 2025 federal tax law (OBBBA), solar projects must begin construction by July 4, 2026 or be "
                 "placed in service by December 31, 2027."]
    if island and not battery:
        footnotes.append("Islanding was selected without battery storage: backup duration and the islanding cost premium "
                         "are not included.")  # [FIX P13]
    for fn in footnotes:
        _paragraph(pdf, fn, size=7.5, style="I", color=REPORT_MUTED, line_h=4)

    # Options not selected that would apply to this facility [FIX P14]
    options = []
    if not net_meter:
        options.append("Net energy metering: credits solar output above the facility's use.")
    battery_uses = []
    if demand_charge > 0:
        battery_uses.append("peak shaving")
    if DR_DISPATCH_FACTORS.get(facility, 0) > 0:
        battery_uses.append("demand response")
    if profile["base_kw"] > 0:
        battery_uses.append("backup modeling")
    if not battery and battery_uses:
        uses = battery_uses[0] if len(battery_uses) == 1 else ", ".join(battery_uses[:-1]) + " and " + battery_uses[-1]
        options.append(f"Battery storage: enables {uses} for this facility type.")
    if battery and not shaving and demand_charge > 0:
        options.append("Peak shaving: lowers the monthly demand charge.")
    if battery and not dr and DR_DISPATCH_FACTORS.get(facility, 0) > 0:
        options.append("NYISO demand response: capacity payments for enrolled battery power.")
    if not island and profile["base_kw"] > 0:
        options.append("Microgrid islanding: models backup duration (requires battery storage; adds 15% to capital cost).")
    if options:
        pdf.ln(2)
        _paragraph(pdf, "Options not included in this configuration (each may change savings, cost or resilience):",
                   size=8.5, style="B", color=REPORT_NAVY, line_h=4.5)
        for opt in options:
            _paragraph(pdf, f"-  {opt}", size=8.5, line_h=4.5)

    # ---------------- PAGE 3: glossary and assumptions ----------------
    pdf.add_page()
    _section_title(pdf, "3. Glossary and Assumptions")
    glossary = [
        ("Total annual savings", "Sum of energy cost savings, net metering credit, peak shaving savings and demand response "
                                 "revenue for the configuration selected."),
        ("Energy cost savings", f"Solar energy used on site, up to the facility's annual use, valued at ${rate:.4f}/kWh: "
                                "National Grid (Niagara Mohawk) average commercial price, U.S. EIA Form EIA-861, 2024. "
                                "This average includes demand charges, so for demand-metered accounts (SC-2 Demand, SC-3) "
                                "the per-kWh value of solar may be lower."),
        ("Peak shaving", "Battery discharge during the facility's highest-demand periods to lower the monthly demand charge "
                         "(SC-2 Demand $18.93/kW-month; SC-3 Secondary $15.62/kW-month above the first 40 kW). The model "
                         "shaves up to 40% of battery power, capped at the facility peak, for all 12 months. Monthly peaks "
                         "outside summer are lower, so this is an upper estimate. Not available on lighting tariffs."),
        ("Net energy metering", "Credits solar output above the facility's annual use at the average commercial rate. Under "
                                "New York VDER rules, many non-residential projects are compensated through the Value Stack, "
                                "which values exports by time and location and may be lower."),
        ("NYISO demand response", f"Battery capacity enrolled in the NYISO Special Case Resources (SCR) program, valued at "
                                  f"${dr_capacity_rate:,.2f}/kW-year. This is the low end of recent NYCA capacity prices "
                                  "after the 74.17% SCR capacity accreditation factor (NYISO, 2026-27, Rest of State)."),
        ("Demand response dispatch factor", "Share of battery power offered to the SCR program after reserving backup "
                                            "capacity: 100% for offices, libraries, community centers and public works; 50% "
                                            "for schools and water and wastewater plants; 0% for police, fire, EOC, street "
                                            "lighting and traffic signals. Enrolled kW is also limited to what the battery "
                                            "can sustain for the 4-hour SCR obligation and to the facility peak."),
        ("Backup duration", "Screening estimate: battery energy divided by the facility's estimated peak demand, plus half "
                            "of one average day's solar output divided by the same peak. Using the peak as a continuous "
                            "load is conservative; the solar term assumes typical sun during the outage. A critical-load "
                            "method is planned for Version 1.1."),  # [FIX H3 wording]
        ("System losses", "Solar output is reduced by 14%, the PVWatts default system losses (soiling, wiring, mismatch, "
                          "availability). Module temperature and inverter efficiency effects are not yet applied; this "
                          "is planned for Version 1.1."),
        ("Federal ITC", "30% Investment Tax Credit applied to the full capital cost, assuming eligibility. Public entities "
                        "may claim it through elective pay. Confirm eligibility and the OBBBA deadlines with a tax advisor."),
        ("Model assumptions", "Battery power (kW) equals solar capacity; battery energy is power times the selected hours. "
                              "The same battery is credited for peak shaving and demand response. Capital costs are "
                              "planning assumptions ($2,500/kW solar; $600/kW for a 2-hour and $950/kW for a 4-hour "
                              "battery; 15% islanding premium) pending sourced benchmarks in Version 1.1. Battery "
                              "degradation, replacement, operations and maintenance, financing and rate escalation are not "
                              "modeled."),  # [FIX M3, P10, P11, P28]
        ("Accuracy", "Facility loads are national benchmarks (CBECS 2018) with an expected range of about plus or minus 30 "
                     "to 40% for an individual building. Results are suitable for screening, not for design or procurement."),
    ]
    for term, definition in glossary:
        if pdf.get_y() > 255:
            pdf.add_page()
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(*REPORT_NAVY)
        pdf.cell(0, 5, term, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        _paragraph(pdf, definition, size=8.5, line_h=4.3)
        pdf.ln(1.5)

    # ---------------- PAGE 4: methods and sources ----------------
    pdf.add_page()
    _section_title(pdf, "4. Methods and Data Sources")
    _paragraph(pdf, "Formulas as computed by TE3 Engine Version 1. Symbols are defined in the table that follows.",
               size=9, color=REPORT_MUTED)
    pdf.ln(1)
    formulas = [
        ("Solar generation", "E_annual = P_dc x H_sun x 0.86"),
        ("Share of use met", "D_offset = Min(E_annual / L_facility, 1) x 100%"),
        ("Energy cost savings", "S_energy = Min(E_annual, L_facility) x R_tariff"),
        ("Net metering credit", "S_nem = Max(E_annual - L_facility, 0) x R_tariff"),
        ("Peak shaving", "S_shave = Min(P_bess x 0.40, L_peak) x R_demand x 12  (a)"),
        ("DR enrolled capacity", "K_dr = Min(P_bess x F_dispatch x Min(D_bess / 4, 1), L_peak)"),
        ("DR revenue", "S_dr = K_dr x R_dr"),
        ("Gross capital cost", "C_gross = (P_dc x 2,500 + P_bess x c_bess) x 1.15  (b)"),
        ("Net capital cost", "C_net = C_gross x (1 - 0.30)"),
        ("Simple payback", "P_years = C_net / (S_energy + S_nem + S_shave + S_dr)"),
        ("Backup duration", "T_backup = C_bess / L_peak + (P_dc x H_day x 0.5) / L_peak"),
    ]
    for label, formula in formulas:
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_text_color(*REPORT_NAVY)
        pdf.cell(36, 6.2, label)
        pdf.set_font("Courier", "B", 8)
        pdf.set_text_color(15, 23, 42)
        pdf.set_fill_color(248, 250, 252)
        pdf.cell(144, 6.2, f" {formula}", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)
        pdf.ln(0.8)
    _paragraph(pdf, "(a) For SC-3, only kW above the first 40 kW is valued.  (b) The 1.15 islanding premium applies only "
                    "when islanding is modeled with a battery; P_bess and c_bess are zero without a battery.",
               size=7.5, style="I", color=REPORT_MUTED, line_h=4)
    pdf.ln(2)

    col_widths = [20, 16, 86, 58]
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_fill_color(*REPORT_NAVY)
    pdf.set_text_color(255, 255, 255)
    for i, header in enumerate(["Symbol", "Unit", "Description", "Source"]):
        last = i == 3
        pdf.cell(col_widths[i], 6.5, f" {header}", border=1, fill=True,
                 new_x=XPos.LMARGIN if last else XPos.RIGHT, new_y=YPos.NEXT if last else YPos.TOP)

    audit_records = [
        ("E_annual", "kWh/yr", "Annual solar generation", "PVWatts v8 (NLR)", "https://developer.nlr.gov/docs/solar/pvwatts/v8/"),
        ("P_dc", "kW", "Solar array rating (DC)", "User input", ""),
        ("H_sun", "h/yr", "Annual peak sun hours at the location (H_day per day)", "NLR NSRDB", "https://nsrdb.nlr.gov/"),
        ("L_facility", "kWh/yr", "Facility annual use (benchmark)", "TE3 TRM; CBECS 2018", "https://www.eia.gov/consumption/commercial/data/2018/"),
        ("L_peak", "kW", "Facility peak demand (annual use / (8,760 x load factor))", "TE3 TRM; UFC 3-501-03N", ""),
        ("R_tariff", "$/kWh", "Average commercial rate", "EIA-861 2024, Table 7", "https://www.eia.gov/electricity/sales_revenue_price/pdf/table_7.pdf"),
        ("R_demand", "$/kW-mo", "Tariff demand charge", "National Grid Service Rates", "https://www.nationalgridus.com/Upstate-NY-Business/Rates/Service-Rates"),
        ("P_bess", "kW", "Battery power (equal to P_dc)", "Model assumption", ""),
        ("D_bess", "h", "Battery duration (2 or 4)", "User input", ""),
        ("C_bess", "kWh", "Battery energy (P_bess x D_bess)", "Calculated", ""),
        ("c_bess", "$/kW", "Battery cost ($600 for 2 h; $950 for 4 h)", "Model assumption", ""),
        ("F_dispatch", "share", "DR dispatch factor by facility type", "NYISO DR Resources", "https://www.nyiso.com/documents/20142/3037451/9-Demand-Response.pdf/3d224420-5b44-a282-5cc9-c082f497d112"),
        ("K_dr", "kW", "DR enrolled capacity", "NYISO SCR rules", "https://www.nyiso.com/documents/20142/30712914/Demand-Response-Special-Case-Resources.pdf"),
        ("R_dr", "$/kW-yr", "DR capacity value", "NYISO 2026-27 CAF", "https://www.nyiso.com/documents/20142/41593818/Final-Capacity-Accreditation-Factors-for-the-2026-2027-capability-year.pdf/83685470-882d-66d2-e6d8-68ed4d449e44"),
        ("C_gross", "$", "Capital cost before the ITC", "Model assumption", ""),
        ("C_net", "$", "Capital cost after the 30% ITC", "IRS section 48E", "https://www.irs.gov/credits-deductions/clean-electricity-investment-credit"),
        ("T_backup", "h", "Backup duration (screening estimate)", "Calculated", ""),
    ]
    pdf.set_text_color(*REPORT_TEXT)
    for idx, (term, unit, desc, source_text, url) in enumerate(audit_records):
        pdf.set_fill_color(*((248, 250, 252) if idx % 2 else (255, 255, 255)))
        pdf.set_font("Helvetica", "", 7.8)
        n_lines = len(pdf.multi_cell(col_widths[2], 3.6, f" {desc}", align="L", dry_run=True, output="LINES"))
        row_h = max(6.0, n_lines * 3.6 + 1.6)
        if pdf.get_y() + row_h > pdf.page_break_trigger:
            pdf.add_page()
        x0, y0 = pdf.get_x(), pdf.get_y()
        pdf.cell(col_widths[0], row_h, f" {term}", border=1, fill=True)
        pdf.cell(col_widths[1], row_h, f" {unit}", border=1, fill=True)
        pdf.cell(col_widths[2], row_h, "", border=1, fill=True)
        pdf.set_xy(x0 + col_widths[0] + col_widths[1], y0 + 0.8)
        pdf.multi_cell(col_widths[2], 3.6, f" {desc}", align="L")
        pdf.set_xy(x0 + col_widths[0] + col_widths[1] + col_widths[2], y0)
        if url:
            pdf.set_text_color(31, 100, 180)
            pdf.set_font("Helvetica", "U", 7.8)
            pdf.cell(col_widths[3], row_h, f" {source_text}", border=1, fill=True, link=url,
                     new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            pdf.set_text_color(*REPORT_TEXT)
        else:
            pdf.cell(col_widths[3], row_h, f" {source_text}", border=1, fill=True, new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.ln(3)
    _paragraph(pdf, "Data vintages: CBECS 2018 (facility benchmarks); EIA-861 2024 (energy rate); National Grid PSC No. 220 "
                    "service rates and 2026 class load shapes; NYISO 2026-27 capacity accreditation; PVWatts v8 with NSRDB "
                    "typical-year data. Full source register: TE3 Technical Reference Manual.",  # [FIX P3]
               size=7.5, style="I", color=REPORT_MUTED, line_h=4)

    return pdf.output()

# =====================================================================
# 6. CACHED API CALLS
# =====================================================================
class SolarDataError(Exception):
    """[FIX H1] Raised instead of returning None, so failures are not cached and the API key is never displayed."""


@st.cache_data(ttl=3600, show_spinner="Retrieving solar resource data...")
def fetch_solar_resource_data(lat, lon, api_key):
    params = {"api_key": api_key, "lat": lat, "lon": lon, "system_capacity": 4, "azimuth": 180,
              "tilt": 20, "array_type": 1, "module_type": 0, "losses": 14}
    try:
        res = requests.get("https://developer.nlr.gov/api/pvwatts/v8.json", params=params, timeout=12)
    except requests.RequestException as e:
        raise SolarDataError(f"the service could not be reached ({type(e).__name__})") from None
    if res.status_code != 200:
        raise SolarDataError(f"the service returned HTTP {res.status_code}")
    value = (res.json().get("outputs") or {}).get("solrad_annual")
    if value is None:
        raise SolarDataError("the response contained no solar resource value")
    return value


# =====================================================================
# 7. EXECUTION PIPELINE
# =====================================================================
if st.session_state.simulation_active and is_valid_zip:
    geo_error = None
    with st.spinner("🌍 Locating ZIP code..."):
        try:
            geo_results = get_coordinates_from_zip(clean_zip)
        except GeocodeError as e:  # [FIX M1]
            geo_results = None
            geo_error = str(e)
        
    if geo_results:
        lat, lon, city_label = geo_results["lat"], geo_results["lon"], geo_results["display_name"]

        # [FIX B1] Current release supports New York State only (National Grid, NYISO and NY net metering assumptions)
        if not (geo_results.get("state_code") == "US-NY" or geo_results.get("state") == "New York"):
            st.warning(f"ZIP code {clean_zip} is outside New York State. This version of TE3 supports New York State ZIP codes only. National coverage is planned for a future release.")
            st.stop()
        
        st.markdown(f"""
            <div class="location-badge">
                📍 <b>Target Location:</b> {html.escape(city_label)} (ZIP Code: {clean_zip})
            </div>
        """, unsafe_allow_html=True)

        # 1. Pull data utilizing the optimized, cached network function hook pointed to nlr.gov
        solar_error = ""
        try:
            daily_solrad_value = fetch_solar_resource_data(lat, lon, NREL_API_KEY)
        except SolarDataError as e:  # [FIX H1]
            daily_solrad_value = None
            solar_error = str(e)

        # 2. Convert daily solar resource to annual peak sun hours
        annual_sun_hours = None

        if daily_solrad_value is not None:
            # Calibrate daily radiation metrics into annual metric baselines
            annual_sun_hours = daily_solrad_value * 365

        else:
            # Graceful interface alert if developer.nlr.gov experiences latency
            st.error(f"❌ Solar resource data unavailable: {solar_error}. Please try again in a few minutes.")
        
        # 3. Solar capacity from the sidebar slider [FIX L2]
        final_capacity = system_capacity_kw

        # 4. MODEL & LAYOUT RENDER BLOCK ---
        if annual_sun_hours is not None:
            metrics = run_techno_economic_modeling(
                annual_sun_hours, final_capacity, facility_selection, 
                enable_battery, bess_duration, enable_net_metering,
                enable_peak_shaving, enable_demand_response, enable_islanding
            )
            
            # Displaying outputs on the user dashboard
            # KPI DASHBOARD REGION
            st.markdown("### 📊 Energy Outcomes")

            # [FIX B2] Payback wording when the configuration produces no savings
            payback_phrase = (
                f"a calculated simple payback period of <b>{metrics['payback']} years</b>"
                if metrics['payback'] is not None
                else "<b>no simple payback</b>, because this configuration produces no annual savings"
            )

            st.markdown(f"""
                <div style="
                    background-color: #f0f4ff; 
                    border: 1px solid #bfdbfe;
                    padding: 0.85rem 1.25rem;
                    border-radius: 8px;
                    margin-bottom: 1.25rem;
                    font-size: 1.05rem;
                    color: #1e40af;
                    font-weight: 500;
                ">
                    💡 <b>Executive Insight:</b> This simulated energy infrastructure configuration is projected to displace approximately
                    <b>{metrics['displacement']}%</b> of the facility's annual electricity demand with {payback_phrase}.
                </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="Projected Annual Generation", 
                    value=f"{metrics['generation']:,} kWh/yr",
                    help="### Projected Annual Generation\n\nThe total estimated electricity production from the proposed solar array over a 12-month period.\n\nCalculated from the NLR NSRDB solar resource (via PVWatts), accounting for localized peak sun hours and applying the PVWatts default system losses of 14%. Module temperature and inverter efficiency effects are planned for Version 1.1.\n\n*Applied Formula: Annual Generation = System Capacity (kW) * Average Peak Sun Hours * 0.86 (Efficiency Coefficient) * 365 Days.*"
                )
            with col2:
                st.metric(
                    label="Grid Energy Demand Offset", 
                    value=f"{metrics['displacement']}%",
                    help="### Grid Energy Demand Offset(%)\n\nThe percentage of the asset's total annual electricity consumption directly offset by on-site solar generation.\n\nA higher displacement rate indicates reduced long-term exposure to utility delivery surcharges and commodity market rate volatility."
                )
                
            with col3:
                st.metric(
                    label="Simple Payback Period", 
                    value=f"{metrics['payback']} Years" if metrics['payback'] is not None else "N/A",
                    help="### Simple Payback Period\n\nThe estimated number of years required for cumulative energy cost savings to fully recover the net capital investment in the solar array.\n\nFormula: Net System Cost (post 30% IRA Tax Credit) / Projected Annual Utility Savings, expressed in nominal dollars at current rate assumptions.\n\nAssumes eligibility for the 30% federal Investment Tax Credit. Under the 2025 federal tax law (OBBBA), solar projects must begin construction by July 4, 2026 or be placed in service by December 31, 2027."
                )

            st.info(f"⚖️ **Tax credit timing:** {ITC_TIMING_NOTE}")  # [FIX ITC]

            st.markdown("<br>", unsafe_allow_html=True)
            
            col_fin1, col_fin2 = st.columns([3, 2])
            with col_fin1:
                st.markdown("### 💵 Financial Outcomes")
                
                st.metric(
                    label="Estimated Annual Savings", 
                    value=f"${metrics['savings']:,.2f} / yr",
                    help="### ESTIMATED ANNUAL SAVINGS\n\nThe projected total reduction in annual utility expenditure resulting from on-site solar generation, battery peak shaving, and applicable grid incentive programs.\n\nExpressed in nominal dollars at current utility rate assumptions.\n\nSavings are calculated on an annual net basis and assume solar generation is consumed on site. Systems that export significant midday generation will realize lower savings unless net metering is enabled."
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    st.metric(
                        label="Battery Peak Shaving", 
                        value=f"${metrics['shaving_savings']:,.2f}/yr",
                        delta="▲ Demand Charge Avoided",
                        delta_color="normal", 
                        help="### BATTERY PEAK SHAVING\n\nThe financial value captured by deploying the Battery Energy Storage System (BESS) to suppress peak electricity demand (kW) during high-load periods.\n\nThis directly reduces the monthly delivery demand charge assessed by National Grid: $18.93 per kW under SC-2 Demand and $15.62 per kW (above the first 40 kW) under SC-3 Secondary (National Grid Upstate NY Service Rates, PSC No. 220). Street lighting and traffic signals are billed under PSC No. 214, which has no demand charge, so peak shaving does not apply."
                    )
                    
                with sub_col2:
                    current_asset_rate = FACILITY_PROFILES[facility_selection]['rate']
                    st.metric(
                        label="Average Commercial Rate", 
                        value=f"${current_asset_rate:.4f}/kWh",
                        delta="▲ Retail Avoidance",
                        delta_color="normal",
                        help="### AVERAGE COMMERCIAL RATE\n\nThe average commercial electricity rate applied to this simulation.\n\nNational Grid (Niagara Mohawk) average commercial price of 10.43 cents/kWh, calculated as total commercial revenue divided by total commercial sales (U.S. EIA, Form EIA-861, 2024, Table 7). It includes supply, delivery and demand charges, and is applied to every facility type.\n\nLimitation: demand-metered accounts (SC-2 Demand, SC-3) pay delivery through per-kW demand charges, so the per-kWh value of solar for those accounts may be lower than this average. Battery peak shaving is valued separately at the tariff demand charge.\n\nRate source used in this run: " + str(FACILITY_PROFILES[facility_selection].get("rate_source", "EIA-861 2024"))  # [FIX L6]
                    )

                # Introduce a NEM DisplaY Card if button is enabled
                if enable_net_metering:
                    if metrics['nem_revenue'] > 0:
                        nem_col1, nem_col2 = st.columns(2)
                        with nem_col1:
                            st.metric(
                                label="NEM Export Revenue", 
                                value=f"${metrics['nem_revenue']:,.2f}/yr",
                                delta="▲ Grid Export Credit",
                                delta_color="normal",
                                help="### NET ENERGY METERING (NEM) REVENUE CREDIT\n\nThe estimated annual financial credit generated by exporting excess solar generation back to the grid.\n\nUnder New York's net metering policy, electricity exported to the grid is credited at the average commercial rate ($/kWh), directly offsetting future utility bills.\n\nCalculated as: Excess Generation (kWh) × Average Commercial Rate ($/kWh).\n\nNote: This model applies traditional retail-rate NEM compensation. Larger systems or community solar projects may qualify for New York's Value of Distributed Energy Resources (VDER) tariff, which assigns location and time-based value to exported energy."
                            )
                        with nem_col2:
                            st.metric(
                                label="Excess Generation Exported",
                                value=f"{metrics['excess']:,.0f} kWh/yr",
                                delta="▲ Grid Surplus",
                                delta_color="normal",
                                help="### EXCESS GENERATION EXPORTED\n\nThe total amount of solar energy generated on-site that exceeds the facility's annual electricity consumption, resulting in net exports to the grid.\n\nThis surplus generation is eligible for net metering credits, providing additional financial value beyond on-site consumption savings."
                           
                            )


                # NYISO DR Display Card to be rendered when feature is enabled
                if enable_demand_response:
                    dr_col1, dr_col2 = st.columns(2)
                    with dr_col1:
                        st.metric(
                            label="NYISO DR Market Revenue", 
                            value=f"${metrics.get('dr_revenue', 0):,.2f}/yr",
                            delta="▲ DR Program Income",
                            delta_color="normal",
                            help="### NYISO DEMAND RESPONSE (DR) MARKET REVENUE\n\nEstimated annual revenue from enrolling battery storage in NYISO's Special Case Resources (SCR) program.\n\nThis model enrolls battery power using a facility-specific dispatch factor (the share of battery power not reserved for backup), limited to what the battery can sustain for NYISO's 4-hour SCR performance obligation and to the facility's peak demand. Enrolled capacity is valued at a conservative upstate New York SCR rate of $20/kW/year, at the low end of the range implied by recent NYCA capacity prices ($2 to $6.74/kW-month) after the 74% SCR capacity accreditation factor.\n\nActual revenue varies by NYISO load zone, seasonal auction clearing prices, and facility performance during dispatch events.\n\nNote: Street lighting, traffic signals, and emergency operations centers are excluded from DR participation due to operational constraints. Police and fire stations are also excluded, because their batteries are reserved for backup power during the grid emergencies when SCR events are called. Single facilities below NYISO's 100 kW minimum enroll through an aggregator (Responsible Interface Party).\n\nReferences: NYISO, Demand Response: Special Case Resources (program rules); NYCA capacity prices, Modo Energy (November 2025) and Rise Energy (May 2026), with the NYISO 2026-27 SCR capacity accreditation factor (rate)."
                        )
                    with dr_col2:
                        st.metric(
                            label="Estimated DR Load Reduction", 
                            value=f"{metrics.get('dr_load_reduction', 0):,.1f} kW",
                            delta="▲ Grid Relief",
                            delta_color="normal",
                            help="### ESTIMATED DR LOAD REDUCTION\n\nThe projected amount of load reduction (in kW) that the facility can achieve during demand response events through battery discharge. It is limited to the battery power the facility offers to the program, the power the battery can sustain for the 4-hour SCR obligation, and the facility's peak demand.\n\nThis reduction contributes to grid stability during peak demand periods and is a key factor in calculating potential DR market revenue."
                        )
                

                st.markdown("---")
                
                st.markdown(f"""
                    <div style="
                        background-color: #f8fafc; 
                        border: 1px solid #cbd5e1; 
                        border-left: 4px solid #1f3a56; 
                        padding: 1rem; 
                        border-radius: 6px;
                        margin-top: 10px;
                    ">
                        <span style="font-weight: 700; color: #0f172a; font-size: 1rem;">
                            🏢 Facility Type: {facility_selection}
                        </span>
                        <p style="margin: 0.5rem 0 0 0; color: #334155; font-size: 0.95rem; line-height: 1.5;">
                            {FACILITY_PROFILES[facility_selection]['desc_simple']}
                        </p>
                    </div>
                """, unsafe_allow_html=True)

                with st.expander("🔍 View Technical Profile"):
                    st.markdown(f"""
                        <div style="background-color: #f8fafc; border: 1px solid #cbd5e1; padding: 1rem; border-radius: 6px; margin-top: 10px;">
                            <span style="font-weight: 700; color: #0f172a; font-size: 1rem;">
                                📋 Facility Technical Profile
                            </span>
                            <p style="margin: 0.5rem 0 0 0; color: #334155; font-size: 0.95rem; line-height: 1.5;">
                                {FACILITY_PROFILES[facility_selection]['desc_technical']}
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

                if enable_islanding and not enable_battery:  # [FIX A3]
                    st.warning("🛡️ **Backup Power Duration:** Microgrid islanding requires battery storage. Enable BESS to model backup power duration.")  # [FIX UI3]
                elif enable_islanding:
                    st.markdown(f"""
                        <div class="resilience-badge">
                            🛡️ <b>Backup Power Duration:</b> Microgrid islanding is active.  
                            The system can sustain critical operations for up to <b>{metrics['autonomy']} hours</b> 
                            during a prolonged grid outage, based on modeled emergency load-shedding and battery discharge assumptions. 
                        </div>
                    """, unsafe_allow_html=True)
                    
            with col_fin2:
                st.markdown("### 📜 Generate Report")
                st.write("View a detailed report to enhance your energy investment decision-making:")
                
            with st.spinner("Generating PDF report..."):
                pdf_data = generate_comprehensive_pdf(
                    zipcode=clean_zip, 
                    city=city_label, 
                    sun_hours=annual_sun_hours, 
                    capacity=final_capacity, 
                    facility=facility_selection, 
                    battery=enable_battery, 
                    duration=bess_duration, 
                    net_meter=enable_net_metering, 
                    shaving=enable_peak_shaving,
                    dr=enable_demand_response, 
                    island=enable_islanding, 
                    results=metrics,
                    dr_dispatch_factor=DR_DISPATCH_FACTORS.get(facility_selection, 0.0),
                    dr_capacity_rate=DR_CAPACITY_RATE
                )
                
                st.download_button(
                    label="Download PDF",
                    data=bytes(pdf_data),
                    file_name=f"TE3_PreFeasibility_Report_{clean_zip}.pdf",
                    mime="application/pdf"
                )

    else:
        if geo_error:
            st.error(f"❌ Location lookup failed: {geo_error}. Please try again in a few minutes.")
        else:
            st.error(f"❌ ZIP code `{clean_zip}` was not found. Check the ZIP code and try again.")

elif submit_button and not is_valid_zip:
    st.sidebar.error("⚠️ Invalid ZIP Code: Please enter a valid 5-digit US ZIP code to proceed with the evaluation.")


else:
    # Optimized container that pops elegantly against a white background
    st.markdown(
        """
        <div style="
            background-color: #fdfbf7; 
            padding: 30px 35px; 
            border-left: 6px solid #f0ad4e; 
            border-right: 1px solid #e9e3d5;
            border-top: 1px solid #e9e3d5;
            border-bottom: 1px solid #e9e3d5;
            border-radius: 8px;
            margin: 20px 0px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.04);
        ">
            <span style="
                font-size: 26px; 
                font-weight: 500; 
                color: #7d6333; 
                line-height: 1.6; 
                display: block;
            ">
                👋 Welcome to the TE3 Engine! Please configure a valid 5-digit US ZIP code in the configuration module to begin your evaluation.
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )