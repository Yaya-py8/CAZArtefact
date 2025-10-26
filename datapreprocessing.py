import pandas as pd
import glob
import os

# --- 1. Setup: SET THIS TO YOUR CSV FOLDER ---
DATA_FOLDER = r'/Users/yahye/Downloads/St Pauls'

# This is the name of the clean file it will save
OUTPUT_FILE = "St_Pauls_COMBINED_CLEAN.csv"

# These are the columns you care about for your analysis
COLUMNS_TO_KEEP = [
    'datetime',  # This script creates this column
    'NO2',
    'PM10',
    'PM25',
    'M_T',      # Temperature
    'M_SPED',   # Wind Speed
    'M_DIR'     # Wind Direction
]
# --- End of Setup ---


print(f"--- Starting: Combining all CSVs in folder: {DATA_FOLDER} ---")

# Use glob to find all .csv files in that folder
csv_files = glob.glob(os.path.join(DATA_FOLDER, "*.csv"))

if not csv_files:
    print(f"ERROR: No .csv files found in '{DATA_FOLDER}'.")
    print("Please check the path in the DATA_FOLDER variable.")
else:
    print(f"Found {len(csv_files)} files to combine...")

# --- 2. Read and Combine Files ---
df_list = []
for file in csv_files:
    print(f"Processing {file}...")
    try:
        # --- !! THE FIX IS HERE !! ---
        # Changed header=4 to header=5 to correctly read Row 6
        df = pd.read_csv(file, header=3, low_memory=False) 

        # --- !! NEW ERROR CHECKING !! ---
        # Check if the essential columns exist before proceeding
        if 'End Date' not in df.columns or 'End Time' not in df.columns:
            print(f"  ERROR: File '{file}' is missing 'End Date' or 'End Time' columns.")
            print(f"  This file might have a different structure. Skipping this file.")
            print(f"  (Its columns are: {df.columns.to_list()})")
            continue # Skips to the next file in the loop
            
        # Standardize PM2.5 column (some files might be 'PM2.5', others 'PM25')
        if 'PM2.5' in df.columns:
            df = df.rename(columns={'PM2.5': 'PM25'})
            
        df_list.append(df)
    except Exception as e:
        print(f"  Could not read {file}. Error: {e}")

if not df_list:
    print("\nERROR: No files were successfully read and processed.")
    print("Please check the error messages above to fix your CSV files.")
else:
    # Combine all the individual dataframes that passed the check
    combined_df = pd.concat(df_list, ignore_index=True)

    print("\nAll valid files combined. Now cleaning data...")

    # --- 3. Clean the Combined Data ---

    # Create a single datetime column
    # 'End Time' has '24:00:00' which pandas can't handle. We replace it with '00:00:00'
    combined_df['End Time'] = combined_df['End Time'].replace('24:00:00', '00:00:00')

    # Combine date and time, then convert to datetime objects
    combined_df['datetime'] = pd.to_datetime(
        combined_df['End Date'] + ' ' + combined_df['End Time'], 
        format='%d/%m/%Y %H:%M:%S',
        errors='coerce' # If any dates are bad, mark them as 'NaT'
    )
    
    # Handle the '24:00:00' (now '00:00:00') by adding one day
    mask_24h = (combined_df['End Time'] == '00:00:00') & (combined_df['datetime'].notna())
    combined_df.loc[mask_24h, 'datetime'] += pd.Timedelta(days=1)

    # Set the new datetime column as the index (best practice for time series)
    combined_df = combined_df.set_index('datetime').sort_index()

    # Select only the columns we need.
    final_df = pd.DataFrame(index=combined_df.index)

    for col in COLUMNS_TO_KEEP:
        if col in combined_df.columns:
            # Convert data to numbers, errors='coerce' turns bad data (e.g., "N/A") into NaN
            final_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
        elif col != 'datetime':
            print(f"  Warning: Column '{col}' not found in the combined data. Skipping.")

    # Drop any rows where all key data is missing
    final_df = final_df.dropna(how='all', subset=[col for col in COLUMNS_TO_KEEP if col != 'datetime'])

    # --- 4. Save the Final, Clean File ---
    # This saves the file in your CURRENT working directory (where you run the script from)
    final_df.to_csv(OUTPUT_FILE)

    print(f"\nSuccess! Clean, combined file saved as '{OUTPUT_FILE}'")
    print("\n--- Final Data Info ---")
    final_df.info()
    print("\n--- Final Data Head ---")
    print(final_df.head())