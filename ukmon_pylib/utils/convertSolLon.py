#
# my own function to convert Solar Longitude to date, as the RMS/WMPL ones seem unstable
#
import numpy as np
from wmpl.Utils.TrajConversions import date2JD


def sollon2jd(Year, Month, Long):

    Long = np.radians(Long)
    N = Year - 2000
    if abs(N) > 100:
        print("Algorithm is not stable for years below 1900 or above 2100")

    JDM0 = 2451182.24736 + 365.25963575 * N
    ApproxJD = date2JD(Year, Month, 15, 12, 0, 0)
    DiffJD = ApproxJD-2451545

    Dt = 1.94330 * np.sin(Long - 1.798135) + 0.01305272 * np.sin(2*Long + 2.634232) + 78.195268 + 58.13165 * Long - 0.0000089408 * DiffJD

    if abs(ApproxJD - (JDM0 + Dt))>50:
        Dt = Dt + 365.2596

    JD1 = JDM0 + Dt

    return JD1


if __name__ == '__main__':
    print(sollon2jd(2021, 1, 140))
    print(sollon2jd(2021, 8, 140))
    print(sollon2jd(2021, 12, 140))
