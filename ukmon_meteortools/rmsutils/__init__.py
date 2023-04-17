# Copyright (C) 2018-2023 Mark McIntyre
# flake8: noqa

try: 
    from .multiDayRadiant import multiDayRadiant
    from .analyseUFOwithRMS import analyseUFOwithRMS
    from .multiTrackStack import multiTrackStack
except:
    print('Unable to locate RMS: you must be in the RMS folder when importing these utilities')
try:
    from .multiEventGroundMap import multiEventGroundMap
    from .plotCAMSOrbits import plotCAMSOrbits
    from .plotRMSOrbits import plotRMSOrbits
except:
    print('unable to locate WMPL: ground maps and orbit plots will be unavailable')

