import pandas as pd

# --- Configuration ---
INPUT_FILE = 'bristol_diffusion_tubes_WITH_HEADERS.csv'
OUTPUT_FILE = 'bristol_spatial_data.csv'

print(f"Reading raw data from {INPUT_FILE}...")
df = pd.read_csv(INPUT_FILE)

# --- 1. Clean the Data ---
# The '2024' column has some text (like '-') which makes it an 'object'. 
# We force it to numbers, turning '-' into NaN (blank).
df['2024'] = pd.to_numeric(df['2024'], errors='coerce')

print(f"Total sites before filtering: {len(df)}")

# --- 2. Filter by Data Capture (Methodology: >= 75%) ---
# We ensure the monitor was working for at least 75% of the year 
# in both the 'Before' (2022/23) and 'After' (2024) periods.
df_clean = df[
    (df['Valid Data Capture for Monitoring Period (%)'] >= 75) &
    (df['Valid Data Capture 2024 (%)'] >= 75)
].copy()

# --- 3. Filter Missing Data ---
# We need a 'Before' value (2022) and at least one 'After' value (2023 or 2024)
df_clean = df_clean.dropna(subset=['2022'])
df_clean = df_clean.dropna(subset=['2023', '2024'], how='all')

print(f"Total sites after quality filtering: {len(df_clean)}")

# --- 4. Calculate Variables ---
# Define 'Before' as 2022
df_clean['NO2_Before'] = df_clean['2022']

# Define 'After' as the average of 2023 and 2024
df_clean['NO2_After'] = df_clean[['2023', '2024']].mean(axis=1)

# Calculate the key metric: Percentage Change
df_clean['Percentage Change (%)'] = ((df_clean['NO2_After'] - df_clean['NO2_Before']) / df_clean['NO2_Before']) * 100

# --- 5. Save Final File ---
# We keep only the columns we need for the map and dashboard
cols_to_keep = [
    'Diffusion Tube ID', 
    'X OS Grid Ref (Easting)', 
    'Y OS Grid Ref (Northing)', 
    'Site Type', 
    'NO2_Before', 
    'NO2_After', 
    'Percentage Change (%)'
]

final_df = df_clean[cols_to_keep]
final_df.to_csv(OUTPUT_FILE, index=False)

print(f"Success! Processed data saved to '{OUTPUT_FILE}'")
print(final_df.head())