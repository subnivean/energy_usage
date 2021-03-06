import pandas as pd
import sqlite3

# Steps to create `all.txt` (all `.csv` files combined)
#    $ cd Tesla_Data_From_App
#    $ echo "DateTime,Home_kW,Solar_kW,Powerwall_kW,Grid_kW" >|all_csvs.txt
#    $ grep -h "^20[12][019]-" *.csv |sort |uniq >>all_csvs.txt

# Parse app data
dfapp = pd.read_csv('Tesla_Data_From_App/all_csvs.txt', skipinitialspace=True)
dfapp['DateTime'] = pd.to_datetime(dfapp['DateTime'], utc=True)
dfapp = dfapp.set_index(['DateTime'])
dfapp.index = dfapp.index.tz_convert('US/Eastern')

# Parse data missing from API (due to gateway or program being down)
# This has been hand-modified to include battery level and grid status.
dfmissing = pd.read_csv('Tesla_Data_From_App/missing_from_api.txt', skipinitialspace=True)
dfmissing['DateTime'] = pd.to_datetime(dfmissing['DateTime'], utc=True)
dfmissing = dfmissing.set_index(['DateTime'])
dfmissing.index = dfmissing.index.tz_convert('US/Eastern')

# Parse API data
dfapi = pd.read_csv("Tesla_Data_From_API/tesla_gateway_meter_data_mod.csv", skipinitialspace=True)
dfapi['DateTime'] = pd.to_datetime(dfapi['DateTime'], utc=True)
dfapi = dfapi.set_index(['DateTime'])
dfapi.index = dfapi.index.tz_convert('US/Eastern')
# Make API values compatible with app format (Watts to kilowatts)
dfapi[['Grid_kW', 'Home_kW', 'Solar_kW', 'Powerwall_kW']] /= 1000

# Add most recent API data (after last date
# in `tesla_gateway_meter_data_mod.csv` above).
# Be sure to run ``
dfnew = pd.read_csv("Tesla_Data_From_API/tesla_gateway_meter_data.csv", skipinitialspace=True, skiprows=33413,
                     names=['DateTime'] + list(dfapi.columns))
dfnew['DateTime'] = pd.to_datetime(dfnew['DateTime'], utc=True)
dfnew = dfnew.set_index(['DateTime'])
dfnew.index = dfnew.index.tz_convert('US/Eastern')
# Make API values compatible with app format (Watts to kilowatts)
dfnew[['Grid_kW', 'Home_kW', 'Solar_kW', 'Powerwall_kW']] /= 1000

# Combine all dataframes and sort by index
dfall = pd.concat([dfapp, dfmissing, dfapi, dfnew], sort=False)
dfall = dfall.sort_index()

# Create new columns for summing kWh
dfall['delta_hours'] = dfall.index.to_series(keep_tz=True).diff().astype('timedelta64[s]') / 3600
dfall['Home_kWh'] = dfall['Home_kW'] * dfall['delta_hours']
dfall['Solar_kWh'] = dfall['Solar_kW'] * dfall['delta_hours']
dfall['Powerwall_kWh'] = dfall['Powerwall_kW'] * dfall['delta_hours']
dfall['Grid_kWh'] = dfall['Grid_kW'] * dfall['delta_hours']

# Store it to a sqlite3 database
#con = sqlite3.connect("energy.sqlite")
#dfall.to_sql('energy_data', con, if_exists='append')