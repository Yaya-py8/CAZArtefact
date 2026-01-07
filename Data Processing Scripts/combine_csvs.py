import pandas as pd 
import os

# Define file paths and output configuration
data_folder = r'.'
file_to_save = 'master_combined.csv'

# Dictionary mapping raw data files to short prefixes.
# This distinguishes the Treatment sites (TW, SP) from the Control sites (Cardiff, Liv, Leeds).
FILES_TO_PROCESS = {
    'Temple_Way_COMBINED_CLEAN.csv': 'TW',
    'St_Pauls_COMBINED_CLEAN.csv': 'SP',
    'Cardiff_COMBINED_CLEAN.csv': 'Cardiff',
    'Liverpool_COMBINED_CLEAN.csv': 'Liv',
    'Leeds_COMBINED_CLEAN.csv': 'Leeds'
}

print(f"--- Starting: Combining specified CSVs into {file_to_save} ---")

all_dfs = []
# Iterate through the dictionary to process each site individually
for file, prefix in FILES_TO_PROCESS.items():
    file_path = os.path.join(data_folder, file)
    
    # Error handling: ensure the file exists before attempting read
    if not os.path.exists(file_path):
        print(f"WARNING: File {file_path} does not exist. Skipping.")
        continue

    print(f"Processing {file_path}...")
    df = pd.read_csv(file_path)

    # Convert 'datetime' column to datetime objects
    # This ensures that pandas interprets the column as time, not just a string
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    
    # Sets the datetime column as the index
    # This is required for the subsequent join since it aligns by time rather than row number
    df = df.set_index('datetime')
    
    # Renames columns with the unique prefix (e.g., changes 'NO2' to 'TW_NO2')
    # This prevents column collision when merging multiple cities into one dataframe
    df = df.rename(columns={col: f"{prefix}_{col}" for col in df.columns})
    all_dfs.append(df)

# --- 3. Join all DataFrames together on their shared datetime index ---
if not all_dfs:
    print("ERROR: No files were processed. Exiting.")
else:
    print("Joining all dataframes...")
    # Concatenate along axis 1 (columns) using the datetime index
    # This creates a single wide-format dataset containing all treatment and control data aligned by hour
    master_df = pd.concat(all_dfs, axis=1)
    
    # Optional: If you only want to keep NO2 and one set of weather data
    # You can be more specific, but for now, let's keep all.
    
    print(f"Master DataFrame created. Shape: {master_df.shape}")
    
    # --- 4. Save the new master file ---
    # Export the aligned dataset for use in the CausalImpact model
    master_df.to_csv(file_to_save)
    print(f"\nSuccess! Master file saved as '{file_to_save}'")
    print(master_df.info())
