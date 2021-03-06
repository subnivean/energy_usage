import matplotlib.pyplot as plt
import sqlite3
import pandas as pd
# Really excellent fix for:
# `Execution failed on sql 'SELECT * FROM energy_data':
#  invalid literal for int() with base 10: b'00-04'`,
# found at https://stackoverflow.com/questions/48614488
import django.db.backends.sqlite3.base


# Create your connection.
conn = sqlite3.connect('energy.sqlite', detect_types=sqlite3.PARSE_DECLTYPES)
df = pd.read_sql_query("SELECT * FROM energy_data", conn, index_col='DateTime')

# This allows you to do things like `df.loc["2021-02-08"]`
# without getting a `KeyError`.
df.index = df.index.astype('datetime64[ns]') \
                   .tz_localize('utc').tz_convert('US/Eastern')


df2019 = (df.groupby(by=df.index.floor('d')).sum()['Solar_kWh']).loc['2019']
df2020 = (df.groupby(by=df.index.floor('d')).sum()['Solar_kWh']).loc['2020']
df2021 = (df.groupby(by=df.index.floor('d')).sum()['Solar_kWh']).loc['2021']

# Make sure we have `DataFrame`s
# df2019 = pd.DataFrame(df2019)
# df2020 = pd.DataFrame(df2020)
# df2021 = pd.DataFrame(df2021)

# Adjust follow-on years so we can overlay year-over-year
df2020.index -= pd.Timedelta('365D')
df2021.index -= pd.Timedelta('731D')

df2019.plot()
df2020.plot()
df2021.plot()

# ax = df2019.reset_index().plot(x='DateTime', y=1, kind='scatter')
# df2020.reset_index().plot(x='DateTime', y=1, kind='scatter', ax=ax)
# df2021.reset_index().plot(x='DateTime', y=1, kind='scatter', ax=ax)

plt.show()