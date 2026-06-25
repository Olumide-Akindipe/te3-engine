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
        f"Municipalities in the United States are facing infrastructure challenges due to rising energy costs and increased vulnerability to grid disruptions. In order to protect critical infrastructure and ensure continuity of public services, local governments are exploring the integration of distributed energy resources (DERs) such as solar photovoltaic (PV) systems and battery energy storage systems (BESS). These technologies provide a pathway to reduce electricity costs but also enhance resilience against power outages and grid instability.\n\n"
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
    pdf.cell(95, 6, f" Blended Utility Rate: ${current_asset_rate:.2f} / kWh Baseline", border=1, ln=True)

    pdf.cell(85, 6, "  Proposed HW Generation Capacity", border=1)
    pdf.cell(95, 6, f"  {capacity} kW Photovoltaic (PV) Array", border=1, ln=True)

    pdf.cell(85, 6, "Net Energy Metering (NEM) Interconnection", border=1)
    pdf.cell(95, 6, f"{'ACTIVE / RETAIL RATE NEM CREDITED' if net_meter else 'INACTIVE / VOLUMETRIC METERS ONLY'}", border=1, ln=True)

    pdf.cell(85, 6, "  Energy Storage Hardware (BESS)", border=1)
    pdf.cell(95, 6, f"  {f'Active {duration}-Hour Setup' if battery else 'Not Deployed'} ", border=1, ln=True)

    pdf.cell(85, 6, " Peak Demand Shaving Dispatch", border=1)
    pdf.cell(95, 6, f" {'ENABLED (SC-3 Tariff Management Mode)' if shaving else 'DISABLED'}", border=1, ln=True)

    pdf.cell(85, 6, " NYISO DR Market Participation / VPP", border=1)
    pdf.cell(95, 6, f" {'ENROLLED - $' + str(dr_capacity_rate) + '/kW/yr SCR Rate | ' + str(int(dr_dispatch_factor * 100)) + '% Dispatch Factor' if dr else 'EXCLUDED / RETAIL ONLY'} ", border=1, ln=True)

# Restored: 2x Microgrid Multiplier Rule & Load Isolation Justification
    pdf.cell(85, 6, " Microgrid Islanding Automation Switch", border=1)
    # Dynamically evaluates and displays the microgrid capabilities based on sidebar state
    if island:
        # Simple capacity multiplier rule based on battery configuration
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


    # 1. Net Energy Metering (NEM) Dynamic Flow
    if net_meter:
        nem_val = results.get('nem_revenue', 0)
        pdf.cell(85, 6, "  Net Energy Metering (NEM) Revenue Credit", border=1)
        pdf.cell(95, 6, f" ${nem_val:,.2f} / Year Credited Stacks", border=1, ln=True)

    #2. Excess Generation Revenue (if applicable)
    if net_meter:
        pdf.cell(85, 6, "  Excess SolarGeneration Exported to Grid", border=1)
        pdf.cell(95, 6, f"  {results['excess']:,.0f} kWh / Year Net Export Volume", border=1, ln=True)

    # 3. NYISO Demand Response (DR) Virtual Power Plant (VPP) Dynamic Flow
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
    # 0.184 is the blended utility rate
    current_asset_rate = current_asset_rate if 'current_asset_rate' in locals() else 0.184
    facility = facility if 'facility' in locals() else "Municipal Office Building"
    
    # Text Definitions Block
    glossary_data = [
        ("Total Annual Energy Cost Savings", "Also known as Total Combined Value Offset (Value Stacking). The total annual financial benefit generated by the solar system. This includes electricity cost savings, demand charge reductions, and any applicable energy export credits combined into a single estimate."),
        ("Grid Energy Offset (Retail Rate Assumption)", f"The specific per-kWh variable cost bypassed by generating electricity on-site. This is based on an estimated blended utility rate (${current_asset_rate:.2f}/kWh for the chosen {facility}) and utility structures."),
        ("Battery Peak Shaving (Demand Charge Reduction)", "The use of Battery Energy Storage Systems (BESS) reduces electricity costs by supplying power during peak demand periods, lowerings the facility's highest measured power usage and associated demand charges."),
        ("Net Energy Metering (NEM) Framework","A policy that allows excess solar energy generated on-site to be sent back to the grid in exchange for credits. In New York, this follows the Value of Distributed Energy Resources (VDER) system, which assigns financial value to exported electricity."),
        ("NYISO Demand Response (DR) Market - Special Case Resources (SCR) Program", "Enrolling in NYISO's Special Case Resources (SCR) program allows facilities with battery storage to receive capacity payments for committing to reduce load during grid stress events. This model applies a facility-specific dispatchable capacity factor and a conservative upstate New York SCR rate of $20/kW/year, consistent with 2026 NYISO capacity auction clearing prices for upstate zones A through E. Actual revenue varies by load zone, seasonal auction results, and facility performance. Street lighting, traffic signal networks, and emergency operations centers are excluded from DR participation due to operational constraints."),
        ("DR Dispatchable Capacity Factor", "The fraction of the solar system capacity (kW) assumed available for dispatch into the NYISO demand response market during grid stress events. This factor varies by facility type, reflecting real-world operational constraints on load curtailment. Office buildings and schools are assigned 25%, multi-family housing 15%, and water and wastewater facilities 10%, reflecting their higher critical load fractions. Mission-critical facilities including traffic signal networks, street lighting systems, and emergency operations centers are assigned 0% and excluded from DR participation entirely."),
        ("NYISO Capacity Accreditation Factor (CAF)", "A discount factor applied by NYISO to battery storage resources that reduces the credited capacity value based on system duration and peak-hour availability. A 2-hour battery system receives a lower CAF than a 4-hour system, meaning actual DR capacity payments are materially lower than the headline clearing price. This model applies a conservative flat rate of $20/kW/year for upstate zones to account for CAF discounting without requiring zone-specific or duration-specific modeling. Reference: NYISO 2025-2029 Demand Curve Reset; Modo Energy NYISO April 2026 benchmark data."),
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
        ("R_tariff", "$/kWh", "Blended Utility Rate: Estimated regional utility power pricing applied to asset.", "U.S. EIA Form 861 Surveys"),
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