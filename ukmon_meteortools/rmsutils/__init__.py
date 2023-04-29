# Copyright (C) 2018-2023 Mark McIntyre
# flake8: noqa

try: 
    from .multiDayRadiant import multiDayRadiant
except Exception:
    print('MultiDayRadiant can only be run from the RMS source folder')

try: 
    from .multiTrackStack import multiTrackStack
except Exception:
    print('multiTrackStack can only be run from an RMS environment')
try: 
    from .analyseUFOwithRMS import analyseUFOwithRMS
except Exception:
    print('analyseUFOwithRMS can only be run from an RMS environment')

try:
    from .multiEventGroundMap import multiEventGroundMap
except Exception:
    print('unable to locate WMPL: ground maps and orbit plots will be unavailable')
try:
    from .plotCAMSOrbits import plotCAMSOrbits
    from .plotRMSOrbits import plotRMSOrbits
except Exception:
    print('unable to locate WMPL: ground maps and orbit plots will be unavailable')

