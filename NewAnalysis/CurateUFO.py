"""
Curation of a folder or set of folders containing UFO data
usage: python CurateUFO.py configfile.ini

An example config file is shown below
"""
#
# disable some linter warnings
# flake8: noqa: F401

import sys
import six
from CameraCurator import curateFolder
from CameraCurator import curateCamera

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('\nusage: python curateUFO.py inifile optonal_date')
        print('eg python curateUFO.py tackley_tc.ini 20200712')
        print('Reads config from an inifile -read example inifile for more info\n')
    else:
        if len(sys.argv) == 3:
            curateCamera.main(sys.argv[1], sys.argv[2])
        else:
            curateFolder.main(sys.argv[1])

    

"""
Example config file
"""
