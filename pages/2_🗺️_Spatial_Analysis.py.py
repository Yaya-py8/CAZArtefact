import streamlit as st
import pandas as pd
import pyproj
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="Spatial Analysis", layout="wide")

# --- Helper Function to Convert Coordinates ---
# QGIS gave you British National Grid (EPSG:27700). 
# Streamlit needs GPS coordinates (Latitude/Longitude).
def convert_coords(df):
    if 'X OS Grid Ref (Easting)' in df.columns:
        bng = pyproj.Proj(init='epsg:27700')
        wgs84 = pyproj.Proj(init='epsg:4326')
        lons, lats = pyproj.transform(bng, wgs84, df['X OS Grid Ref (Easting)'].values, df['Y OS Grid Ref (Northing)'].values)
        df['lat'] = lats
        df['lon'] = lons
    return df

@st.cache_data
def load_spatial_data():
    # Make sure this matches your actual filename
    df = pd.read_csv('bristol_spatial_data.csv')
    # Clean up column names for easier coding
    df.columns = df.columns.str.strip() 
    return convert_coords(df)

st.title("🗺️ Spatial Analysis: Interactive Exploration")

# Load Data
try:
    df = load_spatial_data()
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.stop()

# --- PART 1: Interactive Spatial Map (The "Distinction" Version) ---
st.header("1. Interactive Spatial Map")
st.markdown("""
This map allows for granular investigation of the pollution changes.
* **Red Markers:** Sites where pollution **increased** (Potential Displacement).
* **Blue Markers:** Sites where pollution **decreased**.
* **Click any marker** to see the Site ID, Location, and exact % change.
""")

if 'lat' in df.columns and 'lon' in df.columns and 'Percentage Change (%)' in df.columns:
    
    # 1. Create Base Map centered on Bristol (Zoomed in for detail)
    m = folium.Map(location=[51.4545, -2.5879], zoom_start=13, tiles="CartoDB positron")

    # 2. Add Precision Markers
    for index, row in df.iterrows():
        # Determine color: Red for Increase (Bad), Blue for Decrease (Good)
        # You can also add Orange/Yellow for small changes if you want
        if row['Percentage Change (%)'] > 0:
            color = '#FF4B4B' # Red
            fill_color = '#FF4B4B'
            radius = 8  # Make bad spots slightly bigger
        else:
            color = '#1C83E1' # Blue
            fill_color = '#1C83E1' 
            radius = 6

        # Create the Popup text (HTML formatted for professionalism)
        # This is what appears when you click the dot
        popup_html = f"""
        <div style="font-family: sans-serif; font-size: 12px;">
            <b>Site ID:</b> {row['Diffusion Tube ID']}<br>
            <b>Location:</b> {row.get('Location', 'N/A')}<br>
            <hr style="margin: 3px 0;">
            <b>Change:</b> <span style="color: {'red' if row['Percentage Change (%)'] > 0 else 'blue'}; font-weight: bold;">{row['Percentage Change (%)']:.1f}%</span><br>
            <span style="color: gray;">(2022: {row['NO2_Before']:.1f} → After: {row['NO2_After']:.1f})</span>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['lat'], row['lon']],
            radius=radius,
            color=color,
            weight=1,
            fill=True,
            fill_color=fill_color,
            fill_opacity=0.8,
            popup=folium.Popup(popup_html, max_width=250),
            tooltip=f"{row.get('Location', 'Site')} ({row['Percentage Change (%)']:.1f}%)" # Hover text
        ).add_to(m)

    # Render Map
    st_folium(m, width=None, height=600)

    st.divider()

    # --- PART 2: The Styled Data Table ---
    st.subheader("2. Explore the Underlying Data")
    st.markdown("Full dataset with color-coded pollution changes.")

    # Select columns to display
    display_cols = ['Diffusion Tube ID', 'Location', 'NO2_Before', 'NO2_After', 'Percentage Change (%)']
    # Filter only columns that actually exist
    display_cols = [c for c in display_cols if c in df.columns]

    # Create a styler object for the distinction-level visual
    styler = df[display_cols].style.background_gradient(
        subset=['Percentage Change (%)'],
        cmap='RdBu_r',  # Red-Blue reversed (Red = High/Bad, Blue = Low/Good)
        vmin=-50, vmax=50 # Center the colors like your map
    ).format(
        {'Percentage Change (%)': '{:.1f}%',
         'NO2_Before': '{:.1f}',
         'NO2_After': '{:.1f}'}
    )

    st.dataframe(styler, use_container_width=True, height=400)

else:
    st.error("Coordinate conversion failed or column 'Percentage Change (%)' not found. Cannot display interactive map.")