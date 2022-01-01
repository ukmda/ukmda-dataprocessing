"""
Curation of a folder or set of folders containing UFO data
usage: python CurateUFO.py configfile.ini

An example config file is shown below
"""
#
# disable some linter warnings
# flake8: noqa: F401

import sys
import os
import six
from ufoutils import curateFolder
from ufoutils import curateCamera

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('')
        print('usage 1: python curateUFO.py inifile optonal_date')
        print('eg python curateUFO.py tackley_tc.ini 20200712')
        print('read the ini file and process the given date ')
        print('')
        print('usage 2: python curateUFO.py inifile path')
        print('eg python curateUFO.py tackley_tc.ini c:/temp')
        print('read the ini file, but override the file location and recursively process it')
        print('Useful for processing large historic datasets')
        print('')
        print('usage 3: python curateUFO.py path')
        print('eg python curateUFO.py c:/temp')
        print('Look for an ini file called testing.ini at the given file location')
        print('Useful for processing single folders of data')
    else:
        if len(sys.argv) == 3:
            print('got two args')
            # if the second argument is a folder, treat it as a path to recurse into
            if os.path.isdir(sys.argv[2]):
                badfolder=os.path.join(sys.argv[2], 'bad')
                for root, subdirs, files in os.walk(sys.argv[2]):
                    for subdir in subdirs:
                        if subdir[:2] == '20': 
                            fn = os.path.join(root, subdir)
                            curateFolder.main(sys.argv[1], fn, badfolder)
            elif os.path.isfile(sys.argv[1]):
                curateCamera.main(sys.argv[1], sys.argv[2])
            else:
                print('invalid arguments')
        else:
            # if the argument is a file, so treat it as an ini file
            # if its a path, treat it as a path to recurse into
            if os.path.isfile(sys.argv[1]):
                curateFolder.main(sys.argv[1])
            else:
                print('invalid arguments')                


    

"""
Example config file
"""
