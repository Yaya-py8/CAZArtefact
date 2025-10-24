import pandas as pd

# --- SETTINGS: YOU MUST EDIT THESE ---

# 1. The name of your large, unfilterd CSV file
FILE_TO_LOAD = '/Users/yahye/Downloads/ContinuousAirQuality.csv'

# 2. The name of the file you want to save
FILE_TO_SAVE = 'air_quality_filtered_2019-2023.csv'

# 3. The exact name of the column in your CSV that contains the date and time
#    Common names are 'date', 'Date', 'datetime', 'date_time', 'Timestamp'
DATE_COLUMN_NAME = 'date_time' 

# 4. The exact names of the monitoring stations you want to keep.
#    You MUST find these names in your CSV file.
#    These are just examples!
STATIONS_TO_KEEP = [
    # Bristol "Treatment" Stations
    'Bristol St Pauls', 
    'Bristol Temple Way',
    'Bristol Old Market',
    
    # Example "Control" Stations
    'Cardiff Centre',
    'Sheffield Devonshire Green'
    # Add all your other control stations here
]

# 5. The exact names of the columns you want to keep.
#    You need the date, the station name, and your pollutants.
COLUMNS_TO_KEEP = [
    DATE_COLUMN_NAME,
    'station_name',  # This is also a guess, find the real column name!
    'NO2',
    'PM2.5'
    # Add 'PM10' or any other pollutants you need
]

# 6. The date range you want to keep
START_YEAR = 2019
END_YEAR = 2023

# --- END OF SETTINGS ---


def filter_data(file_path, save_path):
    """
    Loads the large dataset, filters it by date, stations, and columns,
    and saves the result to a new, smaller CSV.
    """
    print(f"Loading data from {file_path}...")
    
    # Load the entire dataset into memory. 120MB is fine for pandas.
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"ERROR: File not found at {file_path}")
        print("Please check the FILE_TO_LOAD setting in this script.")
        return
    except Exception as e:
        print(f"An error occurred loading the file: {e}")
        return
        
    print(f"Original dataset shape: {df.shape[0]} rows, {df.shape[1]} columns")

    # --- 1. Filter by Date ---
    print(f"Filtering data between {START_YEAR} and {END_YEAR}...")
    
    # This is the most critical step. We convert the date column to a 
    # proper datetime object, which allows us to filter by year.
    # If this step fails, your DATE_COLUMN_NAME is wrong or the
    # date format is unusual.
    try:
        # 'errors="coerce"' will turn any unparseable dates into 'NaT' (Not a Time)
        df[DATE_COLUMN_NAME] = pd.to_datetime(df[DATE_COLUMN_NAME], errors='coerce')
    except KeyError:
        print(f"ERROR: The column '{DATE_COLUMN_NAME}' was not found.")
        print("Please correct the DATE_COLUMN_NAME setting.")
        return
    
    # Drop any rows where the date couldn't be understood
    df = df.dropna(subset=[DATE_COLUMN_NAME])

    # Perform the date filtering
    df_filtered = df[
        (df[DATE_COLUMN_NAME].dt.year >= START_YEAR) & 
        (df[DATE_COLUMN_NAME].dt.year <= END_YEAR)
    ]
    
    print(f"Shape after date filter: {df_filtered.shape[0]} rows")

    # --- 2. Filter by Stations ---
    print(f"Filtering for specific stations...")
    
    # This assumes your station name column is called 'station_name'
    # Change this if your column has a different name (e.g., 'Site', 'Location')
    station_col = 'station_name' # <--- EDIT THIS if your station column is different
    
    try:
        df_filtered = df_filtered[df_filtered[station_col].isin(STATIONS_TO_KEEP)]
    except KeyError:
        print(f"ERROR: The column '{station_col}' was not found.")
        print("Please find the station name column in your CSV and update the 'station_col' variable in this script.")
        return
        
    print(f"Shape after station filter: {df_filtered.shape[0]} rows")
    
    if df_filtered.empty:
        print("WARNING: The dataset is empty after filtering by stations.")
        print("This means the names in your STATIONS_TO_KEEP list don't match the names in the CSV.")
        print("Check your CSV for the exact station names.")
        return

    # --- 3. Filter by Columns ---
    print(f"Selecting final columns...")
    
    # This will keep only the columns you listed in COLUMNS_TO_KEEP
    try:
        df_final = df_filtered[COLUMNS_TO_KEEP]
    except KeyError as e:
        print(f"ERROR: One of the columns in COLUMNS_TO_KEEP was not found: {e}")
        print("Please check your COLUMNS_TO_KEEP list.")
        return

    # --- 4. Save the Result ---
    print(f"Saving filtered data to {save_path}...")
    df_final.to_csv(save_path, index=False)
    
    print("\n--- Success! ---")
    print(f"Filtered data saved to: {save_path}")
    print(f"Final shape: {df_final.shape[0]} rows, {df_final.shape[1]} columns")
    print("\nYou can now use this smaller file for your analysis.")


if __name__ == "__main__":
    # This makes the script run when you execute it from the command line
    filter_data(FILE_TO_LOAD, FILE_TO_SAVE)
