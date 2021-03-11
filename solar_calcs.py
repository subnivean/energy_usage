from collections import namedtuple
import datetime

import numpy as np
import pandas as pd
import pysolar
import pysolar.solar as solar

Solarrec = namedtuple('Solarrec', 'fdate azi alt dotp roofazi roofalt')
columns ='fdate azi alt dotp roofazi roofalt'.split()

pysolar.use_numpy()

starttime = datetime.datetime.fromisoformat('2021-03-07T00:00:00+00:00')

ROOFALT = 90 - 16.7
# ROOFALT = 90 - 17.7
# ROOFAZI = 126
# ROOFAZI = 131
ROOFAZI = 145
# ROOFAZI = 150
LATLON = [43.752047, -73.275785]

def get_vector(alt, azi):
    """Calculate unit vector (from [0, 0, 1])
    for a given altitude and azimuth
    """
    alt, azi = np.radians([alt, azi])
    Xr = np.array([0, -np.cos(alt), np.sin(alt)])
    azisin = np.sin(azi)
    azicos = np.cos(azi)
    Zr = np.array(
       [[ azicos, azisin, 0],
        [-azisin, azicos, 0],
        [   0,      0,    1]])
    return Zr.dot(Xr)

roofvec = get_vector(ROOFALT, ROOFAZI)

srs = []
for minutes in range(60 * 24 * 3):
    rec = dict()
    if minutes % (60 * 24) == 0:
        print(f"Day {int(minutes / (60 * 24)) + 1}")
    dmins = datetime.timedelta(minutes=minutes)
    fdate = starttime + dmins
    azi, alt = solar.get_position(*LATLON, fdate)

    dotp = roofvec.dot(get_vector(alt, azi))
    sr = Solarrec(fdate, azi, alt, dotp, ROOFAZI, ROOFALT)
    srs.append(sr)
    # print(f"{fdate.hour - 5:02d}:{fdate.minute:02d}, {alt=:7.4f}, {azi=:7.4f}, {dotp=:8.5f}")

sdf = pd.DataFrame.from_records(srs, columns=Solarrec._fields, index='fdate')

pass
# Some things to try:
# sdf[(sdf['dotp'] > 0) & (sdf['alt'] > 0)].loc['2021-08', 'dotp'].mean()