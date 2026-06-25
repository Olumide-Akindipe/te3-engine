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
        pdf.ln(1.5)
        
        pdf.set_fill_color(248, 250, 252) 
        pdf.set_text_color(15, 23, 42)    
        pdf.set_font("Courier", "B", 10)
        pdf.cell(0, 8, f"   {formula_text}", border=1, ln=True, fill=True)
        pdf.ln(4)

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