import streamlit as st

st.set_page_config(
    page_title="Bristol CAZ Evaluation",
    page_icon="🍃",
    layout="wide"
)

# --- HEADER & CONTEXT ---
st.title("🍃 Evaluating the Bristol Clean Air Zone (CAZ)")
st.markdown("### A Dual-Analysis Framework: Causal Inference & Spatial Mapping")

st.info("""
**Research Finding:** This project reveals an **Ecological Fallacy**. The aggregate time-series analysis suggests 'no significant effect', 
but the spatial analysis reveals that this is due to opposing trends: widespread improvements in the centre were cancelled out by pollution displacement on boundary roads.
""")

st.divider()

# --- THE DUAL ANALYSIS (Side-by-Side) ---
col1, col2 = st.columns(2)

# --- LEFT COLUMN: The "What" (Causal Impact) ---
with col1:
    st.header("1. The 'What': Causal Impact")
    st.markdown("#### Did the CAZ work at central monitoring sites?")
    
    # Display the Main CausalImpact Plot (Static Image from R)
    try:
        st.image("causal_impact_results_DAILY_R.png", use_container_width=True,
                 caption="Figure 4.2: Daily CausalImpact Analysis.")
    except:
        st.error("Image 'causal_impact_results_DAILY_R.png' not found.")

    # Key Stat
    st.metric(label="Estimated Causal Effect (NO2)", value="-5.21 µg/m³", delta="Not Significant (p=0.231)", delta_color="off")
    
    with st.expander("🔍 See Statistical Details"):
        st.write("""
        * **P-Value:** 0.231 (Result is likely random chance)
        * **95% CI:** [-20.4, 9.3] (Crosses zero)
        * **Method:** Bayesian Structural Time-Series (BSTS) with synthetic controls.
        """)

    st.markdown("""
    **Observation:** The model shows a slight reduction, but the confidence interval crosses zero. 
    Statistically, the CAZ had **no significant effect** at these central AURN sites.
    """)

# --- RIGHT COLUMN: The "Where" (Spatial Analysis) ---
with col2:
    st.header("2. The 'Where': Spatial Analysis")
    st.markdown("#### Where did the pollution actually go?")
    
    # Display the Spatial Map (Static Image from QGIS)
    try:
        st.image('percentage change v3.png', use_container_width=True,
                 caption="Figure 5.1: Spatial Map of NO2 % Change.")
    except:
        st.error("Image not found.")

    # Key Stat
    st.metric(label="Displacement Hotspot (St Pauls)", value="+15% Increase", delta="Displacement Detected", delta_color="inverse")

    st.markdown("""
    **Observation:** The map explains the 'No Effect' result. We see **Blue Zones** (Success) in the centre 
    cancelling out **Red Zones** (Displacement) on the boundaries.
    """)

st.divider()

# --- CONCLUSION SECTION ---
st.header("📝 Synthesis & Conclusion")
st.success("""
**The CAZ works, but it moves the problem.** By combining these two analyses, we prove that the aggregate "No Effect" result was misleading. 
The policy successfully cleaned the commercial core but created unintended **pollution displacement** onto residential boundary roads.
""")

st.markdown("---")
st.caption("👈 Use the sidebar to explore the Interactive Data and Validation Tests.")