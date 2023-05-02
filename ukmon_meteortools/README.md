# ukmon_meteortools

Python tools and utilities to work with meteor data from the UK Meteor Network

To get more information about the submodules and functions use Python's built-in help capability

``` python
from ukmon_meteortools import utils
help(utils)
help(utils.sendAnEmail)
```

Example usage 
```python
>>>from ukmon_meteortools.utils import date2JD, jd2LST
>>> date2JD(2023,4,11,12,45,9)
2460046.0313541666
>>>import numpy as np
>>> jd2LST(2460046.0313541666, lon=np.radians(-1.31))
(30.741774823384617, 30.76463863658577)
>>> import datetime
>>> getActiveShowers(datetime.datetime.now())
LYR
ETA
>>> from ukmon_meteortools.utils import getShowerDets
>>> getShowerDets('LYR')
(6, 'April Lyrids', 32.0, '04-22')
>>>
```