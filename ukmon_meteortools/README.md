# ukmon_pytools
## Version 2023.04.15

Python tools and utilities to work with meteor data from the UK Meteor Network

Available submodules shown below. To get more information about each module or function 
use Python's built-in help capability

``` python
from ukmon_meteortools import utils
help(utils)
help(utils.sendAnEmail)
```

Example usage 
```python
>>>from ukmon_meteortools.utils import Math
>>> Math.date2JD(2023,4,11,12,45,9)
2460046.0313541666

>>> Math.jd2LST(2460046.0313541666, lon=-1.31*3.1415/180)
(30.741775497696892, 30.76463863658577)