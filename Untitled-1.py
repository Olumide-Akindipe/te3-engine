# =====================================================================
# 2. USER INTERFACE LAYER (SIDEBAR CONTROLS)
# =====================================================================
st.sidebar.header("⚙️ System Configuration")
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

