import pandas as pd

# 1. Defines the column headers in order
col_names = [
    'Diffusion Tube ID', 
    'X OS Grid Ref (Easting)', 
    'Y OS Grid Ref (Northing)', 
    'Site Type', 
    'Valid Data Capture for Monitoring Period (%)', 
    'Valid Data Capture 2024 (%)', 
    '2020', 
    '2021', 
    '2022', 
    '2023', 
    '2024'
]

# The input file has no headers whilst the output file has headers
input_file = '/Users/yahye/Downloads/tabula-Bristol City Council_ASR_2025.csv'
output_file = 'bristol_diffusion_tubes_WITH_HEADERS.csv'

# 2. Read the CSV, telling pandas it has no header and to use the column names
df = pd.read_csv(input_file, header=None, names=col_names)

# 3. Outputs file with column headers.
df.to_csv(output_file, index=False)

print(f"Success! New file saved as: {output_file}")
print(df.head())
