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

if __name__ == '__main__':
    curateFolder.main(sys.argv[1])

"""
Example config file
"""
