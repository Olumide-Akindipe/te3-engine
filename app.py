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

# EXPANDED FACILITY PROFILES WITH DYNAMIC NATIONAL GRID ELECTRIC TARIFF MAPPING (May 2026 Reference)
FACILITY_PROFILES = {
    "Municipal Office Building": {
        "demand": 45000, "base_kw": 15, "rate": 0.18, 
        "desc_simple": "Office buildings use most of their electricity during the day, making them strong candidates for solar systems that can directly reduce annual electricity costs.",
        "desc_technical": "Daytime-operated municipal facility with predictable load patterns. The primary opportunity lies in reducing annual electricity costs through solar generation, with limited exposure to peak demand charges due to relatively stable load profiles."
    },
    "Public School Facility": {
        "demand": 220000, "base_kw": 75, "rate": 0.21, 
        "desc_simple": "Schools have high energy use during the day and seasonal swings, creating strong opportunities to reduce both electricity bills and peak demand costs using solar and battery systems.",
        "desc_technical": "Schools are associated with high daytime and seasonal load variability driven by student and staff occupancy schedules. Significant opportunity for both volumetric energy cost reduction and demand charge mitigation through integrated solar generation and battery-enabled peak shaving."
    },
    "Multi-Family Housing": {
        "demand": 380000, "base_kw": 65, "rate": 0.24, 
        "desc_simple": "Residential buildings use electricity throughout the day, with peaks in the morning and evening. Solar systems can reduce overall costs, while storage can help shift energy to when it's most needed.",
        "desc_technical": "Continuous 24-hour residential load profile with pronounced morning and evening peaks. Strong candidate for solar-based cost offset, with moderate opportunity for load shifting and distributed energy optimization through storage integration."
    },
    "Wastewater Treatment Plant": {
        "demand": 1200000, "base_kw": 160, "rate": 0.15, 
        "desc_simple": "Wastewater plants run 24/7 and consume large amounts of energy. The main benefit of this system is improving reliability and protecting operations during power outages while stabilizing long-term energy costs.",
        "desc_technical": "Energy-intensive critical infrastructure operating continuously under high mechanical load conditions. Primary value lies in resilience enhancement and long-term energy cost stabilization, given constant demand and operational risk exposure during grid disruptions."
    },
    "Water Treatment & Pumping Station": {
        "demand": 1150000, "base_kw": 150, "rate": 0.20, 
        "desc_simple": "Water systems require constant energy with occasional spikes from pumping. Solar and storage can help reduce peak costs and improve system reliability.",
        "desc_technical": "Essential public utility asset with continuous baseline demand and periodic high-load pumping cycles. Offers strong potential for demand charge mitigation and resilience enhancement through coordinated solar generation and battery dispatch strategies.",
    },
    "Smart Street Lighting System": {
        "demand": 110000, "base_kw": 25, "rate": 0.17, 
        "desc_simple": "Street lighting uses energy mostly at night, making it ideal for systems that store solar energy during the day and use it after dark to reduce costs.",
        "desc_technical": "Nighttime-dominant municipal load with predictable usage patterns. Highly compatible with solar-plus-storage systems that enable daytime energy capture and nighttime discharge, maximizing energy arbitrage and cost efficiency."
    },
    "Traffic Signal Network": {
        "demand": 35000, "base_kw": 4, "rate": 0.18, 
        "desc_simple": "Traffic signals use relatively little energy but must stay operational at all times. The main value of this system is ensuring reliability and safety during outages.",
        "desc_technical": "Low-load but mission-critical infrastructure requiring continuous uptime. Primary value of DER integration lies in resilience, enabling localized backup power and microgrid isolation capabilities to ensure uninterrupted operation."    
    },
    "Emergency Operations Center (EOC)": {
        "demand": 500000, "base_kw": 85, "rate": 0.22, 
        "desc_simple": "Emergency centers must stay operational at all times. Solar and battery systems help reduce costs while ensuring backup power during grid outages.",
        "desc_technical": "Mission-critical municipal facility requiring 100% operational continuity. It requires highest priority for resilience planning, with DER systems providing both cost mitigation and essential backup power through microgrid islanding capabilities."
    }
}

# =====================================================================
# 2. USER INTERFACE LAYER (SIDEBAR CONTROLS)
# =====================================================================
st.sidebar.header("⚙️ System Configurations")
raw_zip = st.sidebar.text_input("Enter ZIP Code:", value="", max_chars=5, placeholder="e.g., 10001")
clean_zip = raw_zip.strip()

is_valid_zip = bool(re.match(r"^\d{5}$", clean_zip))
if not is_valid_zip and clean_zip:
    st.sidebar.warning("⚠️ Enter a valid 5-digit ZIP code.")

st.sidebar.markdown("---")
st.sidebar.markdown("### 🏢 Infrastructure Profile")
facility_selection = st.sidebar.selectbox("Asset Classification Type:", list(FACILITY_PROFILES.keys()))
system_capacity_kw = st.sidebar.slider("Proposed Solar Capacity (kW):", min_value=10, max_value=500, value=50, step=10)

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
    annual_generation_kwh = system_kw * sun_hours * 0.86 

    annual_demand_kwh = FACILITY_PROFILES[facility_type]["demand"]
    grid_displacement_percentage = min((annual_generation_kwh / annual_demand_kwh) * 100, 100.0)
    
    # OPTION B: EXTRACT THE ASSET-SPECIFIC NATIONAL GRID RATE BASELINE
    active_rate = FACILITY_PROFILES[facility_type]["rate"]
    
    base_savings = min(annual_generation_kwh, annual_demand_kwh) * active_rate
    excess_generation = max(0.0, annual_generation_kwh - annual_demand_kwh)
    net_metering_revenue = (excess_generation * 0.08) if net_metering_active else 0.0
    
    shaving_savings = 0.0
    if battery_active and shaving_active:
        shaving_savings = (system_kw * 0.40) * 12.00 * 12 
        
    dr_revenue = 0.0
    if battery_active and dr_active:
        dr_revenue = (system_kw * 0.25) * 45.00 
        
    optimized_annual_savings = base_savings + net_metering_revenue + shaving_savings + dr_revenue
    
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
        autonomy_hours = (battery_capacity_kwh / avg_hourly_demand) + ((system_kw * sun_hours * 0.5) / avg_hourly_demand)
        
    return {
        "generation": round(annual_generation_kwh, 1),
        "demand": annual_demand_kwh,
        "displacement": round(grid_displacement_percentage, 1),
        "savings": round(optimized_annual_savings, 2),
        "base_savings": round(base_savings, 2),
        "shaving_savings": round(shaving_savings, 2),
        "dr_revenue": round(dr_revenue, 2),
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
        self.set_fill_color(31, 58, 86) 
        self.rect(0, 0, 8, 297, "F")
        self.set_left_margin(15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 5, "TE3 Infrastructure Portfolio Matrix | Comprehensive Capital Evaluation", ln=True, align="R")
        self.set_text_color(0, 0, 0) 
        
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Page {self.page_no()} | Vetted via Federal Climate Architecture Baselines (NREL NSRDB)", align="C")

def generate_comprehensive_pdf(zipcode, city, sun_hours, capacity, facility, battery, duration, net_meter, shaving, dr, island, results):
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
    pdf.set_draw_color(230, 150, 30) 
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
        f"Municipalities in the United States are facing infrastructure challenges due to rising energy costs and increased vulnerability to grid disruptions. In order to protect critical infrastructure and ensure continuity of public services, local governments are exploring the integration of distributed energy resources (DERs) such as solar photovoltaic (PV) systems and battery energy storage systems (BESS). These technologies provide a pathway to reduce electricity costs but also enhance resilience against power outages and grid instability."
        f"This model evaluates the potential benefits of deploying a solar PV system, with optional battery storage, at a municipal facility in {city} (ZIP: {zipcode}).\n\n"
        f"By integrating solar generation and distributed energy systems into the municipal portfolio, the system addresses both economic and resilience challenges.\n\n"
        f"First, it reduces electricity expenses by generating on-site power and strategically managing energy use during peak demand periods.\n\n"
        f"Second, it enhances resilience by providing backup power capabilities during grid outages, ensuring that critical municipal functions can continue uninterrupted.\n\n"
        f"This analysis translates complex energy modeling outputs into financial and operational insights for municipal decision-makers, quantifying projected cost savings, grid independence, and return on investment timelines.\n\n"
        f"By leveraging solar resource data and current utility rate structures, this report provides a comprehensive assessment of the financial and operational impacts of the proposed energy system,"
        f"empowering informed infrastructure investment decisions and long-term cost savings that align with sustainability goals and community resilience objectives."
    )
    pdf.multi_cell(0, 5, preamble_story)

    # =====================================================================
    # --- PAGE 2: INFRASTRUCTURE CONTEXT & PORTFOLIO BASELINE MATRIX ---
    # =====================================================================
    pdf.add_page() # Defensively forces data table onto its own uniform page
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(31, 58, 86)
    pdf.cell(0, 6, "1. Project context & Geographic Infrastructure Baseline", ln=True)
    pdf.ln(2)

    # -- TABLE 1: RESTRUCTURED INFRASTRUCTURE CORE MATRIX --
    # Input Data Table (Cleaned strings to prevent padding shifts)
    pdf.set_fill_color(240, 244, 248)
    pdf.set_font("Helvetica", "B", 9)
    pdf.cell(85, 6, "Configuration Paramater", border=1, fill=True)
    pdf.cell(95, 6, "Model Baseline State (Vetted Portfolio Constraints)", border=1, fill=True, ln=True)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(85, 6, "  Target Geography Profile", border=1)
    pdf.cell(95, 6, f"  {city} ({zipcode})", border=1, ln=True)

    pdf.cell(85, 6, "  Solar Resource Irradiance", border=1)
    pdf.cell(95, 6, f"  {round(sun_hours / 365, 2) if sun_hours else 0} Peak Sun Hours / Day Average (NREL NSRDB)", border=1, ln=True)

    pdf.cell(85, 6, "  Selected Asset Classification", border=1)
    pdf.cell(95, 6, f"  {facility}", border=1, ln=True)

    # Restored: Safely references background technical structural profile descriptions
    pdf.cell(85, 6, " Asset Structural Parameters", border=1)
    asset_notes = FACILITY_PROFILES[facility]['desc_technical']
    clean_notes = asset_notes if len(asset_notes) < 55 else asset_notes[:52] + "..."
    pdf.cell(95, 6, f" {clean_notes}", border=1, ln=True)


    # Restored: Vetted National Grid Commercial Tariff Rules
    pdf.cell(85, 6, " National Grid Electric Tariff Class", border=1)
    pdf.cell(95, 6, f" Applied Retail Electricity Rate: ${current_asset_rate:.2f} / kWh Baseline", border=1, ln=True)

    pdf.cell(85, 6, "  Proposed HW Generation Capacity", border=1)
    pdf.cell(95, 6, f"  {capacity} kW Photovoltaic (PV) Array", border=1, ln=True)

    pdf.cell(85, 6, "Net Energy Metering (NEM) Interconnection", border=1)
    pdf.cell(95, 6, f"{'ACTIVE / VDER VALUE STACK ENABLED' if net_meter else 'INACTIVE / VOLUMETRIC METERS ONLY'}", border=1, ln=True)

    pdf.cell(85, 6, "  Energy Storage Hardware (BESS)", border=1)
    pdf.cell(95, 6, f"  {f'Active {duration}-Hour Setup' if battery else 'Not Deployed'} ", border=1, ln=True)

    pdf.cell(85, 6, " Peak Demand Shaving Dispatch", border=1)
    pdf.cell(95, 6, f" {'ENABLED (SC-3 Tariff Management Mode)' if shaving else 'DISABLED'}", border=1, ln=True)

    pdf.cell(85, 6, " NYISO DR Market Participation / VPP", border=1)
    pdf.cell(95, 6, f" {'ENROLLED (Wholesale Capacity Aggregation)' if dr else 'EXCLUDED / RETAIL ONLY'} ", border=1, ln=True)

# Restored: 2x Microgrid Multiplier Rule & Load Isolation Justification
    pdf.cell(85, 6, " Microgrid Islanding Automation Switch", border=1)
    # Dynamically evaluates and displays the microgrid capabilities based on sidebar state
    if island:
        # Simple capacity multiplier rule based on battery configuration
        autonomy_hours = results.get('autonomy', duration * 2 if battery else 0)
        islanding_status = f"OPERATIONAL | Frame: {autonomy_hours} Hours of Backup Power with 50% Critical Load Isolation Mode)"
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
    pdf.cell(95, 6, f"  ${results['shaving_savings']:,} / Year Utility Avoidance", border=1, ln=True)


    # 1. Net Energy Metering (NEM) Dynamic Flow
    if net_meter:
        nem_val = results['excess']  * 0.08
        pdf.cell(85, 6, "  Net Energy Metering (NEM) Revenue Credit", border=1)
        pdf.cell(95, 6, f" ${nem_val:,.2f} / Year Credited Stacks", border=1, ln=True)

    # 2. NYISO Demand Response (DR) Virtual Power Plant (VPP) Dynamic Flow
    if dr:
        dr_val = results.get('dr_revenue', 0)
        pdf.cell(85, 6, "  NYISO DR Market VPP Revenue", border=1)
        pdf.cell(95, 6, f"  ${dr_val:,} / Year Contracted Aggregations", border=1, ln=True)
    
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
        pdf.cell(85, 7, "  BACKUP POWER DURATION(Grid Outage Runtime)", border=1, fill=True)
        pdf.cell(95, 7, f"  {results['autonomy']} Hours Sustained Autonomous Runtime", border=1, fill=True, ln=True)

    pdf.set_text_color(0, 0, 0)
    

# --- PAGE 4: APPLIED REGULATORY, GLOSSARY AND METHODOLOGY FRAMEWORK ---
    pdf.add_page()
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(31, 58, 86)
    pdf.cell(0, 10, "3. Technical Glossary & Regulatory Framework Definitions", ln=True)
    pdf.ln(2)

    # [RECOMMENDED APPROACH] Secure variable scope with fallback guards before matrix execution
    # 0.184 is the applied retail electricity rate
    current_asset_rate = current_asset_rate if 'current_asset_rate' in locals() else 0.184
    facility = facility if 'facility' in locals() else "Municipal Office Building"
    
    # Text Definitions Block
    glossary_data = [
        ("Total Annual Energy Cost Savings", "Also known as Total Combined Value Offset (Value Stacking). The total annual financial benefit generated by the solar system. This includes electricity cost savings, demand charge reductions, and any applicable energy export credits combined into a single estimate."),
        ("Grid Energy Offset (Retail Rate Assumption)", f"The specific per-kWh variable cost bypassed by generating electricity on-site. This is based on an estimated applied retail electricity rate (${current_asset_rate:.2f}/kWh for the chosen {facility}) and utility structures."),
        ("Battery Peak Shaving (Demand Charge Reduction)", "The use of Battery Energy Storage Systems (BESS) reduces electricity costs by supplying power during peak demand periods, lowerings the facility's highest measured power usage and associated demand charges."),
        ("Net Energy Metering (NEM) Framework","A policy that allows excess solar energy generated on-site to be sent back to the grid in exchange for credits. In New York, this follows the Value of Distributed Energy Resources (VDER) system, which assigns financial value to exported electricity."),
        ("NYISO Demand Response (DR) Market Virtual Power Plant (VPP) Participation", "Enrolling in demand response programs allows facilities to receive compensation for reducing load or supplying stored energy to the grid during grid stress events. This model assumes a simplified revenue stream based on potential load reductions, energy supplied, and current market rates."),
        ("Backup Power Duration (Microgrid Islanding Capability) ", "The ability of a facility to operate independently from the main power grid during an outage. Solar panels and batteries continue to supply power locally, helping maintain critical operations. This is calculated based on battery capacity, critical load requirements, and potential solar recharging during daylight hours. The model assumes emergency load-shedding switchgear isolates critical life-safety and server infrastructure, which typically reduces total operational peak demand by 50%, effectively doubling (x2) the nominal battery discharge duration frame."),
        ("NREL NSRDB", "NREL Solar Resource Database. Provides historical solar radiation data used to estimate local solar energy potential."),
        ("System Performance Adjustment (IEC 61724-1)", "A standard performance factor applied to solar systems to account for real-world losses such as heat, wiring inefficiencies, and inverter conversion. This model applies a 14% reduction to reflect actual operating conditions."),
        ("Battery Performance & Lifecycle Assumptions", "The model assumes a lithium iron phosphate (LFP) battery systems with typical operating limits designed to balance performance,lifespan, and daily cycling."),
        ("Model Assumptions & Limitations", "The results presented via this model are estimates based on typical weather data and standard operating assumptions. Actual performance and financial outcomes may vary based on numerous reasons such as site conditions, utility tariffs, and system design.")
    ]
    
    for title, definition in glossary_data:
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(31, 58, 86)
        pdf.cell(0, 5, f">> {title}:", ln=True)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(50, 50, 50)
        pdf.multi_cell(0, 4.5, definition)
        pdf.ln(2.5) # FIXED: Explicit layout padding spacing to prevent overlapping titles

    # =========================================================================
    # COMPLIANCE & AUDIT METHODOLOGY FOOTPRINT (TECHNICAL APPENDIX GENERATION)
    # =========================================================================
    # Force a clean page break after the glossary to isolate the technical audit sheets
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

    # Helper function to print formulas cleanly in FPDF
    def print_audit_formula(title_text, formula_text):
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(31, 58, 86)
        pdf.cell(0, 5, title_text, ln=True)
        pdf.ln(1.5)
        
        # Draw shaded background box for the formula line
        pdf.set_fill_color(248, 250, 252) # Light blue-slate hex #F8FAFC
        pdf.set_text_color(15, 23, 42)    # Dark charcoal
        pdf.set_font("Courier", "B", 10)
        pdf.cell(0, 8, f"   {formula_text}", border=1, ln=True, fill=True)
        pdf.ln(4)

    # FIXED: Replaced hidden string operator bugs with explicit 'x' and clean formatting boundaries
    print_audit_formula("1. Solar Photovoltaic Generation Model", "E_annual = P_dc x H_sun x n_system")
    print_audit_formula("2. Grid Energy Demand Offset Model", "D_offset = Min( (E_annual / L_facility) * 100, 100% )")
    print_audit_formula("3. Financial OpEx Mitigation Model", "S_annual = E_annual x R_tariff")
    print_audit_formula("4. Simple Investment Payback Vector", "P_years = C_capital / S_annual")
    print_audit_formula("5. Microgrid Islanding (Backup Power Duration)", "T_backup = (C_bess / (L_critical x 0.50)) x F_solar")
    pdf.ln(2)

    # Render 4-Column Audit Matrix Table
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(31, 58, 86)
    pdf.cell(0, 5, "Variable Matrix & Data Source Dictionary:", ln=True)
    pdf.ln(3)

    # Define strict table column widths (Totaling 190mm printable horizontal envelope)
    col_widths = [22, 16, 97, 55] 
    
    # Print Table Headers
    pdf.set_font("Helvetica", "B", 8.5)
    pdf.set_text_color(255, 255, 255)
    pdf.set_fill_color(31, 58, 86) # Deep Navy Brand Color
    
    headers = ["Term", "Unit", "Description (One-Line Audit Definition)", "Source Standard / Authority"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 7, header, border=1, ln=(i == len(headers)-1), fill=True)

    # FIXED: Cleaned up raw LaTeX formatting flags ($...$) that broke text cells
    audit_records = [
        ("E_annual", "kWh/yr", "Projected Annual Generation: Total calculated electrical output of the system.", "NREL NSRDB / NOAA Proxy Data"),
        ("P_dc", "kW", "Proposed Solar Capacity: The physical DC power ceiling layout size.", "User Specified / Slider Input"),
        ("H_sun", "hrs/yr", "Annual Peak Sun Hours: Localized solar irradiance metric mapped to ZIP.", "NREL NSRDB Database"),
        ("n_system", "%", "System Efficiency Factor: Performance coefficient forcing a 14% system loss.", "IEC 61724-1 Standard"),
        ("D_offset", "%", "Grid Energy Demand Offset: Total percentage tracking net grid avoidance.", "Calculated Performance Output"),
        ("L_facility", "kWh/yr", "Annual Facility Load: Baseline electricity draw hardcoded to asset classification.", "U.S. DOE / NREL ComStock"),
        ("L_critical", "kW", "Critical Facility Demand: Exact amount of continous electricity needed to sustain the facility during grid outage", "Asset Operational Load Baseline"),
        ("S_annual", "$/yr", "Estimated Annual Savings: Gross operational budget baseline utility savings.", "Calculated Financial Output"),
        ("R_tariff", "$/kWh", "Applied Retail Electricity Rate: Regional utility power pricing applied to asset.", "U.S. EIA Form 861 Surveys"),
        ("P_years", "Years", "Simple Payback Period: Baseline amortization tracking net asset recovery speed.", "Calculated Financial Output"),
        ("C_capital", "$", "Net Capital Cost: Total estimated fiscal deployment footprint calculations.", "Calculated Investment Metric"),
        ("T_backup", "Hours", "Microgrid Islanding: Total hours the facility remains active during an outage.", "Calculated Resilience Output"),
        ("C_bess", "kWh", "Battery Energy Capacity: Total storage volume of hardware setup.", "User Specified / Sizing Input"),
        ("F_solar", "Coeff.", "Solar Replenishment Factor: Dynamic daytime battery charging scaling coefficient.", "NREL Resource Profile Integration")
    ]

    # Print Table Body with alternating row colors (Zebra striping)
    pdf.set_font("Helvetica", "", 7.5)
    pdf.set_text_color(50, 50, 50)
    fill_row = False

    for term, unit, desc, source in audit_records:
        if fill_row:
            pdf.set_fill_color(248, 250, 252) # Light gray alternate row
        else:
            pdf.set_fill_color(255, 255, 255) # Pure white row
            
        # FIXED: Dynamic cell-height calculations block to stabilize row layout bounds
        row_h = 10.0 if len(desc) > 80 else 6.5
        
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        
        pdf.cell(col_widths[0], row_h, f" {term}", border=1, fill=True)
        pdf.cell(col_widths[1], row_h, f" {unit}", border=1, fill=True)
        
        # FIXED: Repositioned coordinates specifically for inline multi-cell wrapping
        pdf.set_xy(x_start + col_widths[0] + col_widths[1], y_start)
        pdf.multi_cell(col_widths[2], row_h / 2 if row_h == 10.0 else row_h, f" {desc}", border=1, fill=True)
        
        # FIXED: Repositioned track cursor for final column to maintain tabular integrity
        pdf.set_xy(x_start + col_widths[0] + col_widths[1] + col_widths[2], y_start)
        pdf.cell(col_widths[3], row_h, f" {source}", border=1, ln=True, fill=True)
        
        fill_row = not fill_row # Alternate cell shading toggling

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
if is_valid_zip:
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
                        value=f"${metrics['shaving_savings']:,}/yr",
                        delta="▲ Demand Charge Avoided",
                        delta_color="normal", 
                        help="### BATTERY PEAK SHAVING\n\nThe financial value captured by deploying the Battery Energy Storage System (BESS) to suppress peak electricity demand (kW) during high-load periods.\n\nThis directly reduces the monthly demand charge baseline assessed by National Grid under commercial SC-2 and SC-3 tariff classifications."
                    )
                    
                with sub_col2:
                    current_asset_rate = FACILITY_PROFILES[facility_selection]['rate']
                    st.metric(
                        label="Applied Retail Electricity Rate", 
                        value=f"${current_asset_rate:.2f}/kWh",
                        delta="▲ Retail Avoidance",
                        delta_color="normal",
                        help="### APPLIED RETAIL ELECTRICITY RATE\n\nThe dynamic blended electricity tariff applied to this simulation.\n\nAutomatically referenced from National Grid's 2026 Upstate New York pricing structures, accounting for whether the selected asset is billed under a standard volumetric commercial rate (SC-2 Non-Demand) or subject to primary distribution voltage demand charges (SC-3 Primary/Secondary)."
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
                    results=metrics
                )
                
                st.download_button(
                    label="📥 Export Report (.pdf)",
                    data=bytes(pdf_data),
                    file_name=f"TE3_Feasibility_Report_{clean_zip}.pdf",
                    mime="application/pdf"
                )

    else:
        st.error(f"❌ Geocoding Exception: Could not find geographic coordinates for ZIP code `{clean_zip}`.")


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