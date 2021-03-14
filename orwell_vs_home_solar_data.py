import os
import sys
import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
# Really excellent fix for:
# `Execution failed on sql 'SELECT * FROM energy_data':
#  invalid literal for int() with base 10: b'00-04'`,
# found at https://stackoverflow.com/questions/48614488
import django.db.backends.sqlite3.base

# Run this from the command line first:
# rsync pi@rpi-3241:Tesla/energy.sqlite ~/energy_usage/energy.sqlite
os.system("rsync pi@rpi-3241:Tesla/energy.sqlite ~/energy_usage/energy.sqlite")

DATE = sys.argv[1]
B2ORATIO = 5.3 / 3.7  # Ratio of peak outputs

# Create your connection.
conn = sqlite3.connect('energy.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
df = pd.read_sql_query("SELECT * FROM energy_data", conn, index_col='DateTime')

# This allows you to do things like `df.loc["2021-02-08"]`
# without getting a `KeyError`.
df.index = df.index.astype('datetime64[ns]') \
                   .tz_localize('utc').tz_convert('US/Eastern')

hskw = df.loc[DATE]['Solar_kWh'].sum()
oskw = df.loc[DATE]['Orwell_kWh'].sum()
aoskw = oskw * B2ORATIO  # Relative max outputs
haorat = aoskw / hskw
print(f"{hskw=:6.2f}   {oskw=:6.2f}   {aoskw=:6.2f}   {haorat=:6.2f}   total={hskw + oskw:6.2f}")

df.loc[DATE]['Solar_kW'].rolling(5).mean().plot()
(df.loc[DATE]['Orwell_kW'] * B2ORATIO).plot()

plt.show()