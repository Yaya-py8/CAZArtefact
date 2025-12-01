import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Causal Impact", layout="wide")

@st.cache_data
def load_time_series():
    df = pd.read_csv("master_combined.csv", parse_dates=["date"])
    df.st_index('datetime', inplace=True)
    # Resamples the data to daily frequency
    df_daily = df.resample('D').mean()
    return df_daily

st.title("Causal Impact Analysis")

# Part 1 - Interactive Data Exploration
st.header("1. Explore the Raw Data" )
st.markdown("Before running the model, we must verify that our control cities track Bristol's trends.")

try:
    df = load_time_series()

    # Interactivity: Select cities to compare
    st.subheader("Compare Pollution Trends")
    options = ['TW_NO2', "SP_NO2", "Cardiff_NO2", "Liv_NO2", "Leeds_NO2"]
    default_select = ['TW_NO2', "Cardiff_NO2"]

    selected_cols = st.multiselect("Select Monitoring Sites:", options, default=default_select)

    # Create an interactive Plotly chart
    if selected_cols:
        fig = px.line(df, y=selected_cols, title="Daily Average NO2 Trends (2019-2025)")
        # Add a vertical line for the intervention date
        fig.add_vline(x="2022-11-28", line_width=2, line_dash="dash", line_color="red",
                        annotation_text="CAZ launch")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please select at least one city.")
except Exception as e:
    st.error(f"Could not load raw data: {e}")

st.divider()

# Part 2 - The Model Results (static but explained)
st.header('2. Causal Model Results')
st.markdown("""
            The interactive chart above shows the raw trends. The CausalImpact model (below) quantifies the **difference** between Bristol and the control citites after the red line.
            """)
# Uses the tabs for the images
tab1, tab2 = st.tabs(["Daily Model", "Hourly Model"])

with tab1:
    st.image("causal_impact_results_DAILY_R.png", caption="Figure 4.2: Final Model Results")
    st.info('Notice how the confidence interval (blue area) is tight, but still crosses zero.")')

with tab2:
    st.image('causal_impact_results_R.png', caption='Figure 4.1: Initial Model Results')
    