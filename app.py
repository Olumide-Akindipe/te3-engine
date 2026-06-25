import os
import re
import requests
import streamlit as st
from dotenv import load_dotenv
from fpdf import FPDF

# =====================================================================
# 1. APPLICATION INITIALIZATION & CONFIGURATION
# =====================================================================
load_dotenv()
NREL_API_KEY = os.getenv("NREL_API_KEY")

st.set_page_config(
    page_title="TE3 Engine",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

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

# EXPANDED FACILITY PROFILES WITH DYNAMIC NATIONAL GRID ELECTRIC TARIFF MAPPING (Verified 2026 Reference)
FACILITY_PROFILES = {
    "Municipal Office Building": {
        "demand": 75000, "base_kw": 25, "rate": 0.19,   #✅ Standard SC-2 Demand Tier
        "desc_simple": "Office buildings use most of their electricity during the day, making them strong candidates for solar systems that can directly reduce annual electricity costs.",
        "desc_technical": "Daytime-operated municipal facility with predictable load patterns. The primary opportunity lies in reducing annual electricity costs through solar generation, with limited exposure to peak demand charges due to relatively stable load profiles."
    },
    "Commercial Office Building": {
        "demand": 240000, "base_kw": 75, "rate": 0.18,
        "desc_simple": "Commercial office buildings have significant energy demands during business hours, making them ideal candidates for solar installations that can offset electricity costs.",
        "desc_technical": "High-demand commercial facility with predictable daytime load patterns due to higher occupancy and extended operational hours. Strong potential for reducing annual electricity costs through solar generation, with moderate exposure to peak demand charges."
    },
    "Public School Facility": {
        "demand": 380000, "base_kw": 120, "rate": 0.13,  ## ✅ Correct SC-3 Large General Service Step-down
        "desc_simple": "Schools have high energy use during the day and seasonal swings, creating strong opportunities to reduce both electricity bills and peak demand costs using solar and battery systems.",
        "desc_technical": "Schools are associated with high daytime and seasonal load variability driven by student and staff occupancy schedules. Significant opportunity for both volumetric energy cost reduction and demand charge mitigation through integrated solar generation and battery-enabled peak shaving."
    },
    "Multi-Family Housing": {
        "demand": 450000, "base_kw": 65, "rate": 0.11, 
        "desc_simple": "Residential buildings use electricity throughout the day, with peaks in the morning and evening. Solar systems can reduce overall costs, while storage can help shift energy to when it's most needed.",
        "desc_technical": "Continuous 24-hour residential load profile with pronounced morning and evening peaks. Strong candidate for solar-based cost offset, with moderate opportunity for load shifting and distributed energy optimization through storage integration."
    },
    "Wastewater Treatment Plant": {
        "demand": 1500000, "base_kw": 250, "rate": 0.11, 
        "desc_simple": "Wastewater plants run 24/7 and consume large amounts of energy. The main benefit of this system is improving reliability and protecting operations during power outages while stabilizing long-term energy costs.",
        "desc_technical": "Energy-intensive critical infrastructure operating continuously under high mechanical load conditions. Primary value lies in resilience enhancement and long-term energy cost stabilization, given constant demand and operational risk exposure during grid disruptions."
    },
    "Water Treatment & Pumping Station": {
        "demand": 1150000, "base_kw": 220, "rate": 0.12, 
        "desc_simple": "Water systems require constant energy with occasional spikes from pumping. Solar and storage can help reduce peak costs and improve system reliability.",
        "desc_technical": "Essential public utility asset with continuous baseline demand and periodic high-load pumping cycles. Offers strong potential for demand charge mitigation and resilience enhancement through coordinated solar generation and battery dispatch strategies.",
    },
    "Smart Street Lighting System": {
        "demand": 110000, "base_kw": 0, "rate": 0.14,   # ✅ Corrected: Unmetered accounts have 0 kW active demand
        "desc_simple": "Street lighting uses energy mostly at night, making it ideal for systems that store solar energy during the day and use it after dark to reduce costs.",
        "desc_technical": "Nighttime-dominant municipal load with predictable usage patterns. Highly compatible with solar-plus-storage systems that enable daytime energy capture and nighttime discharge, maximizing energy arbitrage and cost efficiency."
    },
    "Traffic Signal Network": {
        "demand": 35000, "base_kw": 4, "rate": 0.19, 
        "desc_simple": "Traffic signals use relatively little energy but must stay operational at all times. The main value of this system is ensuring reliability and safety during outages.",
        "desc_technical": "Low-load but mission-critical infrastructure requiring continuous uptime. Primary value of DER integration lies in resilience, enabling localized backup power and microgrid isolation capabilities to ensure uninterrupted operation."    
    },
    "Emergency Operations Center (EOC)": {
        "demand": 500000, "base_kw": 110, "rate": 0.13, 
        "desc_simple": "Emergency centers must stay operational at all times. Solar and battery systems help reduce costs while ensuring backup power during grid outages.",
        "desc_technical": "Mission-critical municipal facility requiring 100% operational continuity. It requires highest priority for resilience planning, with DER systems providing both cost mitigation and essential backup power through microgrid islanding capabilities."
    }
}

# Reference Standards
# Engineering Reference Checklist For Code Documentation
# 1. U.S. Energy Information Administration (EIA), "Commercial Buildings Energy Consumption Survey (CBECS): Energy Characteristics & Consumption Baselines for the Northeast Census Region," 2022-2026 Data Tables. Available: https://www.eia.gov/consumption/commercial/
# [2] U.S. Environmental Protection Agency (EPA), "ENERGY STAR Portfolio Manager Technical Reference: Building Energy Performance Metrics and National Median Benchmarks," Climate Region 1 Reference Sheets. Available: https://www.energystar.gov/buildings/benchmark
# [3] Niagara Mohawk Power Corp d/b/a National Grid, "Schedule for Electric Service, P.S.C. No. 220 Electricity: Non-Residential Service Classifications SC-2 (Demand) and SC-3 (Large General Service Primary & Secondary)," Upstate New York Tariff Statements. Available: https://www.nationalgridus.com/Upstate-NY-Business/Rates/Tariff-Provisions

# B. Commercial & Institutional Baseline Metrics
# [4] EIA CBECS (Commercial Buildings Energy Consumption Survey): This provides the core regional electricity use footprints across the Northeast United States. You can review building specific consumption datasets through the EIA CBECS Survey Overview Data Portal and explore deeper building profile classifications directly at the EIA Commercial Energy Consumption Main Reports Hub.
# [5] EPA ENERGY STAR Portfolio Manager: This is the standard operational matrix for scoring institutional building efficiency and verifying median load profiles. You can analyze regional medians for assets like K-12 schools and multi-family infrastructure via the EPA ENERGY STAR Portfolio Manager Data Explorer Tool. To benchmark initial software assumptions against strict federal standards, review the foundational data input logic via the ENERGY STAR Portfolio Manager Technical Reference Guide.

# C. New York State Electricity Tariffs & Municipal Baselines
# To track the dynamic shift between the SC-2 Small General Service and SC-3 Large General Service blended volumetric and demand structures, use the active New York State regulatory filings:
# [6] National Grid NY Electric Tariffs (PSC No. 220): You can look up active service classifications, delivery constraints, and fixed customer charges directly through the National Grid Upstate NY Tariff Provisions Portal. To track historical supply commodity variance or evaluate active 2026 fuel cost balancing modifications, access the direct monthly pricing statement schedules via the National Grid PSC 220 Electricity Commodity Billing Sheet (PDF).
# [7] NYSERDA Benchmarking Frameworks: To cross-reference how New York municipal bodies catalog public asset consumption limits, study the active operational tools deployed in the NYSERDA Clean Energy Communities Benchmarking Toolkit.



# DR MARKET CONFIGURATION — NYISO SCR UPSTATE NY REFERENCE RATES
DR_CAPACITY_RATE = 20.00  # $/kW-year for capacity enrolled in NYISO DR programs (subject to market fluctuations and program eligibility) — upstate NY SCR conservative estimate
                           # Based on NYISO upstate zones A-E 2026 clearing prices
                           # Source: Modo Energy NYISO April 2026 benchmark report

DR_DISPATCH_FACTORS = {
    "Municipal Office Building": 0.25,      ## Baseline municipal administrative load
    "Commercial Office Building": 0.30,     ## Added: High flexibility via HVAC setbacks/lighting dims
    "Public School Facility": 0.25,         ## High summer alignment, daytime loads
    "Multi-Family Housing": 0.15,           ## Low flexibility due to continuous residential load
    "Wastewater Treatment Plant": 0.10,     ## Process-heavy critical infrastructure
    "Water Treatment & Pumping Station": 0.10,  ## High critical load requirements, limited flexibility
    "Smart Street Lighting System": 0.0,    ## Excluded from traditional SCR
    "Traffic Signal Network": 0.0,          ## Zero curtailment permitted for public safety
    "Emergency Operations Center (EOC)": 0.0,       ## Mission-critical baseline
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

enable_net_metering = st.sidebar.checkbox("Enable Net Energy Metering (NEM)", value=False)
enable_peak_shaving = st.sidebar.checkbox("Enable Battery Peak Shaving", value=False)
enable_demand_response = st.sidebar.checkbox("Enable NYISO DR Market VPP", value=False)
enable_islanding = st.sidebar.checkbox("Enable Microgrid Islanding (Backup for Grid Outages) ", value=False)

# Section 4: Submit Button
st.sidebar.markdown("---")
submit_button = st.sidebar.button(
    label="🚀 Run Techno-Economic Evaluation",
    use_container_width=True
)

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
@st.cache_data(ttl=3600)
def get_coordinates_from_zip(zipcode):
    geo_url = f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&country=United States&format=json&addressdetails=1"
    headers = {"User-Agent": "TE3_Energy_Evaluation_App_v1.0"}
    try:
        geo_response = requests.get(geo_url, headers=headers, timeout=10)
        if geo_response.status_code == 200 and geo_response.json():
            location_data = geo_response.json()[0]
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
                "display_name": display_name
            }
    except Exception as e:
        st.sidebar.error(f"Geocoding Engine Latency: {str(e)}")
    return None

# =====================================================================
# 4. TECHNO-ECONOMIC MATH MATRIX (OPTION B ACTIVE)
# =====================================================================
def run_techno_economic_modeling(sun_hours, system_kw, facility_type, battery_active, duration, net_metering_active, shaving_active, dr_active, islanding_active):
    # 🟢 sun_hours extracted from the integrated API dataset is already an annualized resource vector.
    # Solar Generation and Load Matching Calculation (with 14% system losses factored in)
    annual_generation_kwh = system_kw * sun_hours * 0.86 

    # Calculates how much of the facility's annual electricity usage is covered by the new solar array capped at 100%. 
    annual_demand_kwh = FACILITY_PROFILES[facility_type]["demand"]
    grid_displacement_percentage = min((annual_generation_kwh / annual_demand_kwh) * 100, 100.0)
    
    # OPTION B: EXTRACT THE ASSET-SPECIFIC NATIONAL GRID RATE BASELINE WITH RESPECT TO THE FACILITY PROFILE
    active_rate = FACILITY_PROFILES[facility_type]["rate"]
    
    base_savings = min(annual_generation_kwh, annual_demand_kwh) * active_rate
    excess_generation = max(0.0, annual_generation_kwh - annual_demand_kwh)
    net_metering_revenue = (excess_generation * active_rate) if net_metering_active else 0.0
    
    shaving_savings = 0.0
    if battery_active and shaving_active:
        shaving_savings = (system_kw * 0.40) * 12.00 * 12 
        
    dr_revenue = 0.0
    dr_load_reduction_kw = 0.0
    if battery_active and dr_active:
        dr_load_reduction_kw = system_kw * DR_DISPATCH_FACTORS.get(facility_type, 0.0)
        dr_revenue = dr_load_reduction_kw * DR_CAPACITY_RATE

    optimized_annual_savings = base_savings + net_metering_revenue + shaving_savings + dr_revenue
    
    #Capital Expenditures (CapEx) and Incentives
    base_capex = system_kw * 2500
    if battery_active:
        base_capex += (system_kw * (600 if duration == 2 else 950))
    if islanding_active:
        base_capex *= 1.15 
        
    net_capex = base_capex * 0.70 
    payback_years = net_capex / optimized_annual_savings if optimized_annual_savings > 0 else 0
    
    autonomy_hours = 0.0
    if islanding_active:
        battery_capacity_kwh = system_kw * duration if battery_active else 0.0
        avg_hourly_demand = FACILITY_PROFILES[facility_type]["base_kw"]
        daily_sun_hours = sun_hours / 365
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
        "payback": round(payback_years, 1),
        "excess": round(excess_generation, 1),
        "gross_capex": round(base_capex, 2),
        "ira_credit": round(base_capex * 0.30, 2),
        "autonomy": round(autonomy_hours, 1)
    }

# =====================================================================
# 5. ENTERPRISE PDF COMPILER (WITH TECHNICAL REFERENCE GLOSSARY)
# =====================================================================
class BrandedExecutivePDF(FPDF):
    def header(self):
        # Generates a visual 8mm solid navy blue decorative accent stripe down the left margin boundary
        self.set_fill_color(31, 58, 86) 
        self.rect(0, 0, 8, 297, "F")
        self.set_left_margin(15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "TE3 Infrastructure Portfolio Matrix | Comprehensive Capital Evaluation", ln=True, align="R")
        self.set_text_color(0, 0, 0) 
        
    def footer(self):
        # Repositions cursor 15mm up from bottom edge
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | Vetted via Federal Climate Architecture Baselines (NREL NSRDB)", align="C")

def generate_comprehensive_pdf(zipcode, city, sun_hours, capacity, facility, battery, duration, net_meter, shaving, dr, island, results, dr_dispatch_factor=0.0, dr_capacity_rate=20.00):
    pdf = BrandedExecutivePDF()
    current_asset_rate = FACILITY_PROFILES[facility]["rate"]
    
    # --- PAGE 1: EXECUTIVE DASHBOARD SUMMARY & CONTEXT BRIEF ---
    pdf.add_page()
    pdf.set_left_margin(15)
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(31, 58, 86) 
    pdf.cell(0, 12, "TECHNO-ECONOMIC INVESTMENT REPORT", ln=True)
    pdf.ln(1)
    pdf.set_draw_color(230, 150, 30) # Branded Orange Accent Divider Line
    pdf.set_line_width(0.8)
    pdf.line(15, pdf.get_y(), 195, pdf.get_y())
    pdf.ln(6)
    
    # EXECUTIVE NARRATIVE SUMMARY (THE USE CASE STORY)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(31, 58, 86)
    pdf.cell(0, 6, "Executive Summary", ln=True)
    pdf.ln(1)
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(50, 50, 50)
    preamble_story = (
        f"Municipalities in the United States are facing infrastructure challenges due to rising energy costs and increased vulnerability to grid disruptions. In order to protect critical infrastructure and ensure continuity of public services, local governments are exploring the integration of distributed energy resources (DERs) such as solar photovoltaic (PV) systems and battery energy storage systems (BESS). These technologies provide a pathway to reduce electricity costs but also enhance resilience against power outages and grid instability.\n\n"
        f"This model evaluates the potential benefits of deploying a solar PV system, with optional battery storage, at a municipal facility in {city} (ZIP: {zipcode})."
        f"By integrating solar generation and distributed energy systems into the municipal portfolio, the system addresses both economic and resilience challenges."
        f"First, it reduces electricity expenses by generating on-site power and strategically managing energy use during peak demand periods."
        f"Second, it enhances resilience by providing backup power capabilities during grid outages, ensuring that critical municipal functions can continue uninterrupted.\n\n"
        f"This analysis translates complex energy modeling outputs into financial and operational insights for municipal decision-makers, quantifying projected cost savings, grid independence, and return on investment timelines. "
        f"By leveraging solar resource data and current utility rate structures, this report provides a comprehensive assessment of the financial and operational impacts of the proposed energy system,"
        f"empowering informed infrastructure investment decisions and long-term cost savings that align with sustainability goals and community resilience objectives."
    )
    pdf.multi_cell(0, 5, preamble_story)


    # =====================================================================
    # --- PAGE 2: INFRASTRUCTURE CONTEXT & PORTFOLIO BASELINE MATRIX ---
    # =====================================================================
    pdf.add_page() 
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(31, 58, 86)
    pdf.cell(0, 6, "1. Project context & Geographic Infrastructure Baseline", ln=True)
    pdf.ln(2)

    # -- TABLE 1: RESTRUCTURED INFRASTRUCTURE CORE MATRIX --
    pdf.set_fill_color(240, 244, 248)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(85, 6, "Configuration Parameter", border=1, fill=True)
    pdf.cell(95, 6, "Model Baseline State (Vetted Portfolio Constraints)", border=1, fill=True, ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(85, 6, "  Target Geography Profile", border=1)
    pdf.cell(95, 6, f"  {city} ({zipcode})", border=1, ln=True)

    pdf.cell(85, 6, "  Solar Resource Irradiance", border=1)
    pdf.cell(95, 6, f"  {round(sun_hours / 365, 2) if sun_hours else 0} Peak Sun Hours / Day Average (NREL NSRDB)", border=1, ln=True)

    pdf.cell(85, 6, "  Selected Asset Classification", border=1)
    pdf.cell(95, 6, f"  {facility}", border=1, ln=True)

    pdf.cell(85, 6, "  Asset Structural Parameters", border=1)
    asset_notes = FACILITY_PROFILES[facility]['desc_technical']
    clean_notes = asset_notes if len(asset_notes) < 55 else asset_notes[:52] + "..."
    pdf.cell(95, 6, f"  {clean_notes}", border=1, ln=True)

    pdf.cell(85, 6, "  National Grid Electric Tariff Class", border=1)
    pdf.cell(95, 6, f"  Blended Utility Rate: ${current_asset_rate:.2f} / kWh Baseline", border=1, ln=True)

    pdf.cell(85, 6, "  Proposed HW Generation Capacity", border=1)
    pdf.cell(95, 6, f"  {capacity} kW Photovoltaic (PV) Array", border=1, ln=True)

    pdf.cell(85, 6, "  Net Energy Metering (NEM) Interconnection", border=1)
    pdf.cell(95, 6, f"  {'ACTIVE / RETAIL RATE NEM CREDITED' if net_meter else 'INACTIVE / VOLUMETRIC METERS ONLY'}", border=1, ln=True)

    pdf.cell(85, 6, "  Energy Storage Hardware (BESS)", border=1)
    pdf.cell(95, 6, f"  {f'Active {duration}-Hour Setup' if battery else 'Not Deployed'} ", border=1, ln=True)

    pdf.cell(85, 6, "  Peak Demand Shaving Dispatch", border=1)
    pdf.cell(95, 6, f"  {'ENABLED (SC-3 Tariff Management Mode)' if shaving else 'DISABLED'}", border=1, ln=True)

    pdf.cell(85, 6, "  NYISO DR Market Participation / VPP", border=1)
    pdf.cell(95, 6, f"  {'ENROLLED - $' + str(dr_capacity_rate) + '/kW/yr SCR Rate | ' + str(int(dr_dispatch_factor * 100)) + '% Dispatch Factor' if dr else 'EXCLUDED / RETAIL ONLY'} ", border=1, ln=True)

    pdf.cell(85, 6, "  Microgrid Islanding Automation Switch", border=1)
    if island:
        autonomy_hours = results.get('autonomy', duration * 2 if battery else 0)
        islanding_status = f"OPERATIONAL | {autonomy_hours} hrs backup | 50% Critical Load Isolation Mode)"
    else:
        islanding_status = "NON-OPERATIONAL"
    pdf.cell(95, 6, f"  {islanding_status}", border=1, ln=True)
    
    # =====================================================================
    # --- PAGE 3: TECHNO-ECONOMIC SAVINGS & FINANCIAL INVESTMENT OUTCOMES ---
    # =====================================================================
    pdf.add_page()
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(31, 58, 86)
    pdf.cell(0, 6, "2. Techno-Economic Energy Outcomes", ln=True)
    pdf.ln(2)
    
    # -- TABLE 2: PROJECTED FINANCIAL VECTORS --
    pdf.set_fill_color(240, 244, 248)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(85, 6, "  Performance Metric Indicators", border=1, fill=True)
    pdf.cell(95, 6, "  Projected Financial Value", border=1, fill=True, ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(85, 6, "  Projected Annual Generation", border=1)
    pdf.cell(95, 6, f"  {results['generation']:,} kWh / Year", border=1, ln=True)

    pdf.cell(85, 6, "  Grid Energy Demand Offset", border=1)
    pdf.cell(95, 6, f"  {results['displacement']}% Grid Avoidance", border=1, ln=True)

    pdf.cell(85, 6, "  Direct Volumetric Solar Co-Generation Avoidance Savings", border=1)
    pdf.cell(95, 6, f"  ${results['base_savings']:,} / Year Nominal Base Load", border=1, ln=True)

    pdf.cell(85, 6, "  Peak Demand BESS Shaving Adjustments", border=1)
    pdf.cell(95, 6, f"  ${results['shaving_savings']:,.2f} / Year Utility Avoidance", border=1, ln=True)

    if net_meter:
        nem_val = results.get('nem_revenue', 0)
        pdf.cell(85, 6, "  Net Energy Metering (NEM) Revenue Credit", border=1)
        pdf.cell(95, 6, f"  ${nem_val:,.2f} / Year Credited Stacks", border=1, ln=True)

        pdf.cell(85, 6, "  Excess Solar Generation Exported to Grid", border=1)
        pdf.cell(95, 6, f"  {results['excess']:,.0f} kWh / Year Net Export Volume", border=1, ln=True)

    if dr:
        dr_val = results.get('dr_revenue', 0)
        dr_load = results.get('dr_load_reduction', 0)
        pdf.cell(85, 6, "  NYISO DR Market VPP Revenue", border=1)
        pdf.cell(95, 6, f"  ${dr_val:,} / Year | {dr_load} kW Dispatched", border=1, ln=True)
    
    # Strategic Capital Highlight Sub-Table
    pdf.set_fill_color(254, 247, 234) 
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(180, 90, 0)

    pdf.cell(85, 7, "  TOTAL ANNUAL ENERGY COST SAVINGS", border=1, fill=True)
    pdf.cell(95, 7, f"  ${results['savings']:,} / Year Post-Optimization", border=1, fill=True, ln=True)

    pdf.cell(85, 7, "  ESTIMATED NET INITIAL SETUP INVESTMENT (CapEx)", border=1, fill=True)
    pdf.cell(95, 7, f"  ${results.get('capex', 0):,} (Post-IRA 30% Investment Tax Credit)", border=1, fill=True, ln=True)

    pdf.cell(85, 7, "  SIMPLE PAYBACK PERIOD", border=1, fill=True)
    pdf.cell(95, 7, f"  {results['payback']} Nominal Calendar Years", border=1, fill=True, ln=True)
    
    if island and results.get('autonomy', 0) > 0:
        pdf.cell(85, 7, "  BACKUP POWER DURATION (Grid Outage Runtime)", border=1, fill=True)
        pdf.cell(95, 7, f"  {results['autonomy']} Hours Sustained Autonomous Runtime", border=1, fill=True, ln=True)

    pdf.set_text_color(0, 0, 0)

    # Fallback content block when optional modules are inactive
    inactive_modules = []
    if not net_meter:
        inactive_modules.append("Net Energy Metering (NEM) - enables retaiil-rate export credits for excess solar generation")
    if not dr:
        inactive_modules.append("NYISO Demand Response (DR) - enables participation in NYISO's demand response via the Special Case Resources (SCR) program")
    if not island:
        inactive_modules.append("Microgrid Islanding - enables backup power capabilities during grid outages through automated transfer switch configurations")
    if not battery:
        inactive_modules.append("Battery Energy Storage System (BESS) - enables energy storage for peak shaving and demand response participation")

    if inactive_modules:
        pdf.ln(6)
        pdf.set_fill_color(245, 245, 250)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(31, 58, 86)
        pdf.multi_cell(0, 4.5, f"Note: The following optional modules were not activated in this configuration, which may impact the total projected savings and operational capabilities: {', '.join(inactive_modules)}. For a more comprehensive analysis, consider enabling these features to capture their full financial and resilience benefits.")
        pdf.set_font("Helvetica", "", 8.5)
        pdf.set_text_color(60, 60, 60)
        pdf.ln(2)
        for module in inactive_modules:
            pdf.cell(5, 4.5, "- ", border=0)
            pdf.cell(0, 5, f" - {module}", ln=True)
        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(120, 120, 120)
        pdf.multi_cell(0, 4.5,
            "To activate these modules, return to the TE3 sidebar and enable the corresponding "
            "interconnection features. Each module adds incremental financial value to the total "
            "annual savings projection and expands the scope of this investment analysis. This report is based on modeled projections using current utility rates and solar resource data. Actual performance and savings may vary based on real-world conditions, system performance, and market dynamics."
        )

    # --- PAGE 4: APPLIED REGULATORY, GLOSSARY AND METHODOLOGY FRAMEWORK ---
    pdf.add_page()
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(31, 58, 86)
    pdf.cell(0, 8, "3. Technical Glossary & Regulatory Framework Definitions", ln=True)
    pdf.ln(2)

    current_asset_rate = current_asset_rate if 'current_asset_rate' in locals() else 0.184
    facility = facility if 'facility' in locals() else "Municipal Office Building"
    
    glossary_data = [
        ("Total Annual Energy Cost Savings", "Total combined value offset (Value Stacking). The complete financial benefit generated by solar on-site generation, demand management, and grid export incentives."),
        ("Grid Energy Offset (Retail Rate)", f"The specific variable cost bypassed by on-site generation. Factored at a blended delivery/supply rate of ${current_asset_rate:.2f}/kWh for the evaluated {facility} asset template."),
        ("Battery Peak Shaving", "Using BESS hardware capacity to dispatch during critical coincidental peak utility windows to artificially trim seasonal demand surcharges under commercial delivery classes."),
        ("Net Energy Metering (NEM)", "Interconnection rules allowing multi-asset generation exports. Under New York VDER rules, exports are calculated based on hourly unbundled value stack variables."),
        ("NYISO Demand Response Market", "Enrolling storage capacity in the Special Case Resources (SCR) program for capacity reservations. Modeled at a conservative upstate NY base clearing price of $20.00/kW/year. Excludes lighting/signals."),
        ("DR Dispatchable Capacity Factor", "The assumed portion of system capacity available for grid curtailment. Office and schools hold 25%; water/wastewater assets hold 10% due to processing baselines. Signals and lights hold 0%."),
        ("NYISO Capacity Accreditation (CAF)", "The performance discount applied by the ISO to storage based on real-world duration. Accommodated directly within the compressed $20.00/kW/year modeling assumption threshold."),
        ("Backup Power Duration (Islanding)", "Emergency load-shedding isolation mode runtime. Assumes smart automated transfer switches slice standard non-critical circuit demands by 50%, doubling standard discharge envelopes."),
        ("NREL NSRDB Infrastructure", "National Renewable Energy Laboratory Solar Resource Database. Feeds high-fidelity historical solar irradiance metrics into the localization mapping engine."),
        ("System Performance Adjustment", "Integrated baseline coefficient computing real-world thermal losses, inverter drop-offs, and wiring friction. Forces a flat 14% performance penalty per IEC 61724-1."),
        ("Battery Lifecycle Assumptions", "Sized around Lithium Iron Phosphate (LFP) chemistries, setting standard operational threshold profiles optimized to maintain active state-of-health curves over time."),
        ("Model Assumptions & Limitations", "Projections represent weather-normalized engineering baselines. Actual field results will fluctuate under variable weather pattern dynamics and real-world grid anomalies.")
    ]
    
    # TWO-COLUMN COMPACT GLOSSARY PATTERN WITH PAGINATION MONITOR
    pdf.set_font("Helvetica", "", 7.5)
    col_w = 88
    space_between_cols = 4
    col_left_x = 15
    col_right_x = col_left_x + col_w + space_between_cols
    
    for idx, (title, definition) in enumerate(glossary_data):
        # MANUAL PAGINATION TRIPWIRE: If cursor hits 250mm, add clean page break
        if pdf.get_y() > 250:
            pdf.add_page()
            pdf.ln(10)
            
        is_even = (idx % 2 == 0)
        curr_x = col_left_x if is_even else col_right_x
        
        pdf.set_x(curr_x)
        
        # Term Header
        pdf.set_font("Helvetica", "B", 8)
        pdf.set_text_color(31, 58, 86)
        pdf.cell(col_w, 4, f">> {title}:", ln=True)
        pdf.set_x(curr_x)
        
        # Definition Body
        pdf.set_font("Helvetica", "", 7.5)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(col_w, 3.5, definition)
        
        if not is_even:
            pdf.ln(2.5)


    # =========================================================================
    # COMPLIANCE & AUDIT METHODOLOGY FOOTPRINT (TECHNICAL APPENDIX GENERATION)
    # =========================================================================
    pdf.add_page()
    pdf.ln(5)
    
    # Section Header
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(31, 58, 86)
    pdf.cell(0, 10, "4. Technical Methodology & Audit Framework Equations", ln=True)
    pdf.ln(2)
    
    pdf.set_font("Helvetica", "", 9.5)
    pdf.set_text_color(80, 80, 80)
    pdf.multi_cell(0, 5, "This section outlines the mathematical core verification formulas and verified federal data benchmarks utilized to compute the performance metrics and financial vectors displayed within this brief.")
    pdf.ln(5)

    def print_audit_formula(title_text, formula_text):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(31, 58, 86)
        pdf.cell(0, 5, title_text, ln=True)
        pdf.ln(1)
        
        pdf.set_fill_color(248, 250, 252) 
        pdf.set_text_color(15, 23, 42)    
        pdf.set_font("Courier", "B", 10)
        pdf.cell(0, 8, f"   {formula_text}", border=1, ln=True, fill=True)
        pdf.ln(2)

    print_audit_formula("1. Solar Photovoltaic Generation Model", "E_annual = P_dc x H_sun x n_system")
    print_audit_formula("2. Grid Energy Demand Offset Model", "D_offset = Min( (E_annual / L_facility) * 100, 100% )")
    print_audit_formula("3. Financial OpEx Mitigation Model", "S_annual = E_annual x R_tariff")
    print_audit_formula("4. Simple Investment Payback Vector", "P_years = C_capital / S_annual")
    print_audit_formula("5. Microgrid Islanding (Backup Power Duration)", "T_backup = (C_bess / (L_critical x 0.50)) x F_solar")
    pdf.ln(2)

    # Render 4-Column Audit Matrix Table with Embedded Standard URLs
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(31, 58, 86)
    pdf.cell(0, 5, "Variable Matrix & Data Source Dictionary:", ln=True)
    pdf.ln(3)

    col_widths = [22, 16, 92, 60] 
    
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(31, 58, 86) 
    
    headers = ["Term", "Unit", "Description (One-Line Audit Definition)", "Source Standard / Authority Link"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 7, header, border=1, ln=(i == len(headers)-1), fill=True)

    audit_records = [
        ("E_annual", "kWh/yr", "Projected Annual Generation: Total calculated electrical output.", "NREL NSRDB Database Portal", "https://nsrdb.nrel.gov/"),
        ("P_dc", "kW", "Proposed Solar Capacity: The physical DC power ceiling layout size.", "User Specified Input", ""),
        ("H_sun", "hrs/yr", "Annual Peak Sun Hours: Localized solar irradiance metric mapped to ZIP.", "NREL Resource Profiles", "https://nsrdb.nrel.gov/"),
        ("n_system", "%", "System Efficiency Factor: Performance coefficient forcing a 14% system loss.", "IEC 61724-1 Standard", ""),
        ("D_offset", "%", "Grid Energy Demand Offset: Total percentage tracking net grid avoidance.", "Calculated Output Metric", ""),
        ("L_facility", "kWh/yr", "Annual Facility Load: Baseline electricity draw hardcoded to asset class.", "EIA CBECS Survey Library", "https://www.eia.gov/consumption/commercial/"),
        ("L_critical", "kW", "Critical Facility Demand: Continuous load capacity needed during isolation.", "EPA Portfolio Manager Explorer", "https://www.energystar.gov/buildings/benchmark"),
        ("S_annual", "$/yr", "Estimated Annual Savings: Gross operational budget baseline utility savings.", "Calculated Energy Output", ""),
        ("R_tariff", "$/kWh", "Blended Utility Rate: Estimated regional utility power pricing applied to asset.", "National Grid Tariff PSC 220", "https://www.nationalgridus.com/Upstate-NY-Business/Rates/Tariff-Provisions"),
        ("P_years", "Years", "Simple Payback Period: Baseline amortization tracking net asset recovery speed.", "Calculated Financial Output", ""),
        ("C_capital", "$", "Net Capital Cost: Total estimated fiscal deployment footprint calculations.", "Calculated CapEx Output", ""),
        ("T_backup", "Hours", "Microgrid Islanding: Total hours the facility remains active during an outage.", "Calculated Resilience Output", ""),
        ("C_bess", "kWh", "Battery Energy Capacity: Total storage volume of hardware setup.", "User Sizing Input Layer", ""),
        ("F_solar", "Coeff.", "Solar Replenishment Factor: Dynamic daytime battery charging coefficient.", "NYSERDA Infrastructure Profiles", "https://www.nyserda.ny.gov/")
    ]

    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(50, 50, 50)
    fill_row = False

    for term, unit, desc, source_text, url in audit_records:
        if fill_row:
            pdf.set_fill_color(248, 250, 252) 
        else:
            pdf.set_fill_color(255, 255, 255) 
            
        row_h = 10.0 if len(desc) > 80 else 6.5
        
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        
        pdf.cell(col_widths[0], row_h, f" {term}", border=1, fill=True)
        pdf.cell(col_widths[1], row_h, f" {unit}", border=1, fill=True)
        
        pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
        pdf.multi_cell(col_widths[2], row_h / 2 if row_h == 10.0 else row_h, f" {desc}", border=1, fill=True)
        
        pdf.set_xy(x_start + col_widths[0] + col_widths[1] + col_widths[2], y_start)
        
        # IF TARGET URL IS DETECTED, APPLY INTERACTIVE LINK STYLING
        if url:
            pdf.set_text_color(31, 100, 180) # Hyperlink Blue
            pdf.set_font("Helvetica", "U", 7.5) # 'U' enables the text underline asset style
            pdf.cell(col_widths[3], row_h, f" {source_text}", border=1, ln=True, fill=True, link=url)
            pdf.set_text_color(50, 50, 50)
            pdf.set_font("Helvetica", "", 7.5)
        else:
            pdf.cell(col_widths[3], row_h, f" {source_text}", border=1, ln=True, fill=True)
            
        fill_row = not fill_row 

    return pdf.output()


# =====================================================================
# 6. CACHED API CONNECTION HOOKS (BYPASSES SIDEBAR LATENCY)
# =====================================================================
@st.cache_data(ttl=3600, show_spinner="Querying federal solar irradiance matrix...")
def fetch_solar_resource_data(lat, lon, api_key):
    # 🟢 FIXED: Corrected domain spelling to developer.nlr.gov
    url = f"https://developer.nlr.gov/api/pvwatts/v8.json?api_key={NREL_API_KEY}&lat={lat}&lon={lon}&system_capacity=4&azimuth=180&tilt=20&array_type=1&module_type=0&losses=14"
    try:
        res = requests.get(url, timeout=12)
        if res.status_code == 200 and "outputs" in res.json():
            # Return the single annualized solar production reference metric 
            return res.json()["outputs"].get("solrad_annual")
    except Exception as e:
        pass
    return None


# =====================================================================
# 7. EXECUTION PIPELINE (PROD-READY & ALIGNMENT BALANCED)
# =====================================================================
if st.session_state.simulation_active and is_valid_zip:
    with st.spinner("🌍 Connecting to geospatial servers..."):
        geo_results = get_coordinates_from_zip(clean_zip)
        
    if geo_results:
        lat, lon, city_label = geo_results["lat"], geo_results["lon"], geo_results["display_name"]
        
        st.markdown(f"""
            <div class="location-badge">
                📍 <b>Target Location:</b> {city_label} (Zip Code: {clean_zip})
            </div>
        """, unsafe_allow_html=True)

        # 1. Pull data utilizing the optimized, cached network function hook pointed to nlr.gov
        daily_solrad_value = fetch_solar_resource_data(lat, lon, NREL_API_KEY)

        # 2. SAFE VARIABLE INITIALIZATION (Completely prevents down-funnel NameErrors)
        annual_sun_hours = None

        if daily_solrad_value is not None:
            # Calibrate daily radiation metrics into annual metric baselines
            annual_sun_hours = daily_solrad_value * 365

        else:
            # Graceful interface alert if developer.nlr.gov experiences latency
            st.error("❌ Data Parsing Error: The proxy service at developer.nlr.gov returned empty solar data attributes.")
        
        # 3. SAFE VARIABLE FALLBACK CHECK (Protects widget configuration name changes)
        # Ensures that whatever your sidebar slider variable is named, it maps cleanly here
        final_capacity = locals().get('system_capacity_kw', locals().get('solar_capacity_kw', 50))

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
                    <b>{metrics['displacement']}%</b> of the facility's annual electricity demand with a calculated simple payback period of <b>{metrics['payback']} years</b>.
                </div>
            """, unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="Projected Annual Generation", 
                    value=f"{metrics['generation']:,} kWh/yr",
                    help="### Projected Annual Generation\n\nThe total estimated electricity production from the proposed solar array over a 12-month period.\n\nCalculated using the NREL NSRDB solar resource model, accounting for localized peak sun hours and programmatically enforcing an IEC 61724-1 system de-rating coefficient of 14% to account for real-world environmental and thermal inefficiencies.\n\n*Applied Formula: Annual Generation = System Capacity (kW) * Average Peak Sun Hours * 0.86 (Efficiency Coefficient) * 365 Days.*"
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
                    value=f"{metrics['payback']} Years",
                    help="### Simple Payback Period\n\nThe estimated number of years required for cumulative energy cost savings to fully recover the net capital investment in the solar array.\n\nFormula: Net System Cost (post 30% IRA Tax Credit) / Projected Annual Utility Savings, expressed in nominal dollars at current rate assumptions."
                )

            st.markdown("<br>", unsafe_allow_html=True)
            
            col_fin1, col_fin2 = st.columns([3, 2])
            with col_fin1:
                st.markdown("### 💵 Financial Outcomes")
                
                st.metric(
                    label="Estimated Annual Savings", 
                    value=f"${metrics['savings']:,} / yr",
                    help="### ESTIMATED ANNUAL SAVINGS\n\nThe projected total reduction in annual utility expenditure resulting from on-site solar generation, battery peak shaving, and applicable grid incentive programs.\n\nExpressed in nominal dollars at current utility rate assumptions."
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                sub_col1, sub_col2 = st.columns(2)
                with sub_col1:
                    st.metric(
                        label="Battery Peak Shaving", 
                        value=f"${metrics['shaving_savings']:,.2f}/yr",
                        delta="▲ Demand Charge Avoided",
                        delta_color="normal", 
                        help="### BATTERY PEAK SHAVING\n\nThe financial value captured by deploying the Battery Energy Storage System (BESS) to suppress peak electricity demand (kW) during high-load periods.\n\nThis directly reduces the monthly demand charge baseline assessed by National Grid under commercial SC-2 and SC-3 tariff classifications."
                    )
                    
                with sub_col2:
                    current_asset_rate = FACILITY_PROFILES[facility_selection]['rate']
                    st.metric(
                        label="Blended Utility Rate", 
                        value=f"${current_asset_rate:.2f}/kWh",
                        delta="▲ Retail Avoidance",
                        delta_color="normal",
                        help="### BLENDED UTILITY RATE\n\nThe dynamic blended electricity tariff applied to this simulation.\n\nAutomatically referenced from National Grid's 2026 Upstate New York pricing structures, accounting for whether the selected asset is billed under a standard volumetric commercial rate (SC-2 Non-Demand) or subject to primary distribution voltage demand charges (SC-3 Primary/Secondary)."
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
                                help="### NET ENERGY METERING (NEM) REVENUE CREDIT\n\nThe estimated annual financial credit generated by exporting excess solar generation back to the grid.\n\nUnder New York's net metering policy, electricity exported to the grid is credited at the facility's applied blended utility rate ($/kWh), directly offsetting future utility bills.\n\nCalculated as: Excess Generation (kWh) × Blended Utility Rate ($/kWh).\n\nNote: This model applies traditional retail-rate NEM compensation. Larger systems or community solar projects may qualify for New York's Value of Distributed Energy Resources (VDER) tariff, which assigns location and time-based value to exported energy."
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
                            help="### NYISO DEMAND RESPONSE (DR) MARKET REVENUE\n\nEstimated annual revenue from enrolling battery storage in NYISO's Special Case Resources (SCR) program.\n\nThis model applies a facility-specific dispatchable capacity factor and a conservative upstate New York SCR rate of $20/kW/year, consistent with 2026 NYISO capacity auction clearing prices for upstate zones (A–E).\n\nActual revenue varies by NYISO load zone, seasonal auction clearing prices, and facility performance during dispatch events.\n\nNote: Street lighting, traffic signals, and emergency operations centers are excluded from DR participation due to operational constraints.\n\nReference: NYISO April 2026 upstate UCAP clearing price — Modo Energy benchmark report."
                        )
                    with dr_col2:
                        st.metric(
                            label="Estimated DR Load Reduction", 
                            value=f"{metrics.get('dr_load_reduction', 0):,} kW",
                            delta="▲ Grid Relief",
                            delta_color="normal",
                            help="### ESTIMATED DR LOAD REDUCTION\n\nThe projected amount of load reduction (in kW) that the facility can achieve during demand response events through a combination of solar generation and battery discharge.\n\nThis reduction contributes to grid stability during peak demand periods and is a key factor in calculating potential DR market revenue."
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

                if enable_islanding:
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
                    label="📥 Export Report (.pdf)",
                    data=bytes(pdf_data),
                    file_name=f"TE3_Feasibility_Report_{clean_zip}.pdf",
                    mime="application/pdf"
                )

    else:
        st.error(f"❌ Geocoding Exception: Could not find geographic coordinates for ZIP code `{clean_zip}`.")

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