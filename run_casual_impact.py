import pandas as pd
from casualimpact import CausalImpact

df = pd.read_csv('master_combined.csv',
                 index_col='datetime',
                 parse_dates=True)
print('Data loaded, interpolating missing values')
df_interpolated = df.interpolate(method='linear', limit_direction='both')

print('NaNs remaining after interpolation:', df_interpolated.isna().sum().sum())