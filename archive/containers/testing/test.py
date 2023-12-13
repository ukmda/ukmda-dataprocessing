import pandas as pd
import numpy as np
from RMS.Math import angularSeparation
from wmpl.Utils.Physics import calcRadiatedEnergy

print('hello world')
df = pd.DataFrame([[1,2],[3,4]])
print(df)
angsep = angularSeparation(0, 0, 3.1415/4, 3.1415/8)
print(f'angsep {angsep}')
tarr = np.array([0,1,2])
marr = np.array([-1,-2,-1])
re = calcRadiatedEnergy(tarr, marr)
print(f'rad energy {re}')
