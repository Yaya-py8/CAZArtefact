import pandas as pd
import glob
import os

# --- 1. Settings: All your changes go in this section ---

# 1. Point this to your new Cardiff data folder
DATA_FOLDER = r'/Users/yahye/Downloads/Liverpool Speke'

# 2. Change the name of the final combined file
OUTPUT_FILE = "Liverpool_COMBINED_CLEAN.csv"

# 3. This variable tells the script which row to use as the header
HEADER_ROW_NUMBER = 10 # 11th row is index 10

# 4. Set the *exact* column names from your Cardiff CSV
DATE_COLUMN_NAME = 'Date'
TIME_COLUMN_NAME = 'Time'

# 5. Set the time format.
TIME_FORMAT = '%H:%M:%S' # For '01:00:00'

# 6. Create a "rename map" to match the Cardiff names to your standard names
COLUMN_RENAME_MAP = {
    'Nitrogen dioxide': 'NO2',
    'PM10 particulate matter (Hourly measured)': 'PM10',
    'PM2.5 particulate matter (Hourly measured)': 'PM25', # Standardize to PM25
    'Modelled Wind Direction': 'M_DIR',
    'Modelled Wind Speed': 'M_SPED',
    'Modelled Temperature': 'M_T'
}

# 7. This list of columns to KEEP is now based on your *standard* names
COLUMNS_TO_KEEP = [
    'datetime',  # This script creates this column
    'NO2',
    'PM10',
    'PM25',
    'M_T',
    'M_SPED',
    'M_DIR'
]
# --- End of Setup ---


print(f"--- Starting: Combining all CSVs in folder: {DATA_FOLDER} ---")

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
        # Use the HEADER_ROW_NUMBER variable
        df = pd.read_csv(file, header=HEADER_ROW_NUMBER, low_memory=False) 

        # Rename columns based on your map
        df = df.rename(columns=COLUMN_RENAME_MAP)
        
        # Check for the new column names
        if DATE_COLUMN_NAME not in df.columns or TIME_COLUMN_NAME not in df.columns:
            print(f"  ERROR: File '{file}' is missing '{DATE_COLUMN_NAME}' or '{TIME_COLUMN_NAME}' columns.")
            print(f"  This file might have a different structure. Skipping this file.")
            print(f"  (Its columns are: {df.columns.to_list()})")
            continue 
            
        # Standardize PM2.5 (in case the rename map missed one)
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
    
    # This line assumes your new data *also* uses '24:00:00'
    combined_df[TIME_COLUMN_NAME] = combined_df[TIME_COLUMN_NAME].replace('24:00:00', '00:00:00')

    print("  Combining and converting to datetime...")
    try:
        # 1. Combine the 'Date' and 'Time' columns
        datetime_str = combined_df[DATE_COLUMN_NAME] + ' ' + combined_df[TIME_COLUMN_NAME]

        # --- !! THIS IS THE FIX !! ---
        # 2. Convert to datetime objects using the 'YYYY-MM-DD' format
        combined_df['datetime'] = pd.to_datetime(
            datetime_str, 
            format=f'%Y-%m-%d {TIME_FORMAT}', # Changed from 'dd/mm/YYYY'
            errors='coerce' 
        )
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: Could not combine Date and Time. Error: {e}")
        # Stop the script
        exit()
    
    # 3. Handle the '24:00:00' (now '00:00:00') by adding one day
    mask_24h = (combined_df[TIME_COLUMN_NAME] == '00:00:00') & (combined_df['datetime'].notna())
    combined_df.loc[mask_24h, 'datetime'] += pd.Timedelta(days=1)

    # Set the new datetime column as the index (best practice for time series)
    combined_df = combined_df.set_index('datetime').sort_index()

    # Select only the columns we need.
    final_df = pd.DataFrame(index=combined_df.index)

    print("  Selecting and converting final columns...")
    for col in COLUMNS_TO_KEEP:
        if col in combined_df.columns:
            # Convert data to numbers
            final_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
        elif col != 'datetime':
            print(f"  Warning: Standardized column '{col}' not found. Skipping.")

    # Drop any rows where all key data is missing
    final_df = final_df.dropna(how='all', subset=[col for col in COLUMNS_TO_KEEP if col != 'datetime'])

    # --- 4. Save the Final, Clean File ---
    final_df.to_csv(OUTPUT_FILE)

    print(f"\nSuccess! Clean, combined file saved as '{OUTPUT_FILE}'")
    print("\n--- Final Data Info ---")
    final_df.info()
    print("\n--- Final Data Head ---")
    print(final_df.head())