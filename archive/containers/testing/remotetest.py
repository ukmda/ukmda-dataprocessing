#
# copyright mark mcintyre 2023-
#

import pandas as pd
import numpy as np
from RMS.Math import angularSeparation
from wmpl.Utils.Physics import calcRadiatedEnergy
from meteortools.utils import date2JD

print('this is a test script for RMS and WMPL')

df = pd.DataFrame([[1,2],[3,4]])
print(df)
angsep = angularSeparation(0, 0, 3.1415/4, 3.1415/8)
print(f'angsep {angsep}')
tarr = np.array([0,1,2])
marr = np.array([-1,-2,-1])
re = calcRadiatedEnergy(tarr, marr)
print(f'rad energy {re}')


print(f'2023-11-12T6:12:11 is {date2JD(2023,11,12,6,12,11)}')
