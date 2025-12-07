import pandas as pd 
import os

data_folder = r'.'
file_to_save = 'master_combined.csv'

FILES_TO_PROCESS = {
    'Temple_Way_COMBINED_CLEAN.csv': 'TW',
    'St_Pauls_COMBINED_CLEAN.csv': 'SP',
    'Cardiff_COMBINED_CLEAN.csv': 'Cardiff',
    'Liverpool_COMBINED_CLEAN.csv': 'Liv',
    'Leeds_COMBINED_CLEAN.csv': 'Leeds'
}

print(f"--- Starting: Combining specified CSVs into {file_to_save} ---")

all_dfs = []
for file, prefix in FILES_TO_PROCESS.items():
    file_path = os.path.join(data_folder, file)
    if not os.path.exists(file_path):
        print(f"WARNING: File {file_path} does not exist. Skipping.")
        continue

    print(f"Processing {file_path}...")
    df = pd.read_csv(file_path)

    # Convert 'datetime' column to datetime objects
    df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
    df = df.set_index('datetime')
    
    # Rename columns with the prefix (e.g., 'NO2' -> 'TW_NO2')
    df = df.rename(columns={col: f"{prefix}_{col}" for col in df.columns})
    all_dfs.append(df)

# --- 3. Join all DataFrames together on their shared datetime index ---
if not all_dfs:
    print("ERROR: No files were processed. Exiting.")
else:
    print("Joining all dataframes...")
    # This joins them side-by-side, aligning them by the 'datetime' index
    master_df = pd.concat(all_dfs, axis=1)
    
    # Optional: If you only want to keep NO2 and one set of weather data
    # You can be more specific, but for now, let's keep all.
    
    print(f"Master DataFrame created. Shape: {master_df.shape}")
    
    # --- 4. Save the new master file ---
    master_df.to_csv(file_to_save)
    print(f"\nSuccess! Master file saved as '{file_to_save}'")
    print(master_df.info())
