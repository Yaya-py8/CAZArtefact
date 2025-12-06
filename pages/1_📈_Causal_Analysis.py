import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Causal Impact Analysis", layout="wide")

# --- 1. ROBUST DATA LOADING FUNCTION ---
@st.cache_data
def load_time_series():
    try:
        # 1. Load CSV
        df = pd.read_csv("master_combined.csv")
        df.columns = df.columns.str.strip()

        # 2. Handle Date
        if 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
            df.set_index('datetime', inplace=True)
        else:
            return pd.DataFrame()

        # 3. Filter for specific columns
        target_cols = ['TW_NO2', 'SP_NO2', 'Cardiff_NO2', 'Liv_NO2', 'Leeds_NO2']
        existing_cols = [c for c in target_cols if c in df.columns]
        df = df[existing_cols]

        # 4. Force Numeric
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # 5. Resample to Daily
        df_daily = df.resample('D').mean()

        # --- FIX: RENAME COLUMNS FOR BETTER DISPLAY ---
        # Map the code names to nice, readable names
        rename_map = {
            'TW_NO2': 'Temple Way (Bristol)',
            'SP_NO2': 'St Pauls (Bristol)',
            'Cardiff_NO2': 'Cardiff',
            'Liv_NO2': 'Liverpool',
            'Leeds_NO2': 'Leeds'
        }
        df_daily = df_daily.rename(columns=rename_map)
        
        return df_daily

    except Exception as e:
        st.error(f"Error processing data: {e}")
        return pd.DataFrame()

# ... (Title and Markdown remain the same) ...

# --- PART 1: INTERACTIVE DATA EXPLORER ---
st.divider()
st.header("1. Explore the Trends (Raw Data)")
st.markdown("Use this chart to verify that the control cities track Bristol's trends *before* the intervention.")

df = load_time_series()

if not df.empty:
    # Dropdown to select cities (Now using the nice names!)
    all_cols = df.columns.tolist()
    
    # Update default selection to use the new names
    default_cols = ['Temple Way (Bristol)', 'Cardiff']
    # Safety check to make sure defaults exist in the file
    default_cols = [c for c in default_cols if c in all_cols]
    
    selected_cols = st.multiselect(
        "Select Monitoring Sites to Compare:", 
        options=all_cols, 
        default=default_cols
    )

    if selected_cols:
        # Create Plotly Chart
        fig = px.line(df, y=selected_cols, title="Daily Average NO2 Trends (2019-2025)")
        
        # --- FIX: Use add_shape instead of add_vline to avoid the crash ---
        # 1. Add the vertical line manually
        fig.add_shape(
            type="line",
            x0="2022-11-28", y0=0, 
            x1="2022-11-28", y1=1,
            xref="x", yref="paper",
            line=dict(color="red", width=2, dash="dash")
        )
        
        # 2. Add the text label manually
        fig.add_annotation(
            x="2022-11-28", y=1.05,
            xref="x", yref="paper",
            text="CAZ Launch",
            showarrow=False,
            font=dict(color="red")
        )
        
        fig.update_layout(xaxis_title="Date", yaxis_title="NO2 Concentration (µg/m³)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Please select at least one city to view the chart.")
else:
    st.warning("Could not load data for the interactive chart. Please check 'master_combined.csv'.")


# --- PART 2: CAUSAL IMPACT RESULTS ---
st.divider()
st.header("2. Causal Model Results (The 'What')")
st.markdown("""
To isolate the policy's effect from weather and national trends, a **Bayesian Structural Time-Series (BSTS)** model was used.
""")

# Create Tabs for the narrative
tab1, tab2 = st.tabs(["🏆 Final Model (Daily)", "🧪 Initial Model (Hourly)"])

with tab1:
    st.subheader("Refined Analysis: Daily Aggregated Data")
    st.markdown("Aggregating to daily averages smoothed out high-frequency noise, resulting in a stable counterfactual prediction.")
    
    # 1. Display the Plot
    try:
        # Ensure this filename matches your saved R plot
        st.image("causal_impact_results_DAILY_R.png", caption="Figure 4.2: Final CausalImpact Analysis", use_container_width=True)
    except:
        st.error("Image 'causal_impact_results_DAILY_R.png' not found. Please add it to the project folder.")

    # 2. Display Key Stats
    st.info("### Statistical Verdict: No Significant Effect")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Estimated Reduction", "-5.21 µg/m³", delta="-9.5%", delta_color="normal")
    col2.metric("P-Value", "0.231", help="A p-value > 0.05 indicates the result could be due to random chance.")
    col3.metric("95% Confidence Interval", "[-20.4, 9.3]", help="The interval crosses zero, indicating no significant effect.")

    st.markdown("""
    **Interpretation:** The model estimates a reduction, but the 95% confidence interval crosses zero and the p-value (0.231) is well above the threshold for significance. 
    We conclude that the CAZ had **no statistically significant causal effect** at these two central monitoring sites.
    """)

with tab2:
    st.subheader("Initial Analysis: Hourly Data")
    st.markdown("The initial model run on raw hourly data demonstrated why data aggregation was necessary.")
    
    try:
        # You can use your 'Test3' plot or the original hourly one here
        # Ensure this filename exists in your folder
        st.image("causal_impact_results_R.png", caption="Figure 4.1: Initial Hourly Model (High Volatility)", use_container_width=True)
    except:
        st.warning("Image 'causal_impact_results_R.png' not found.")
        
    st.markdown("""
    **Observation:** The prediction interval (blue shaded area) is extremely wide, indicating the model could not distinguish the policy signal from hourly traffic/weather noise. This justified the move to the Daily Model.
    """)