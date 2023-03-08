#
# Script provided by Denis Vida to convert WMPL trajectory data from 
# the pre Sept 2021 layout to the new layout
#
# Copyright (C) 2018-2023 Mark McIntyre

import os
import shutil
import sys


def sortToDateDirs(pth):
    for dirname in os.listdir(pth):
        if os.path.isdir(os.path.join(pth, dirname)):
            # Check that it is a trajectory dir
            if len(dirname) > 8:
                if len(dirname.split("_")) > 2:
                    if dirname[:8].isnumeric():
                        print('processing', dirname)
                        year = dirname[:4]
                        month = dirname[:6]
                        date = dirname[:8]

                        # Make a year directory
                        out_dir = os.path.join('.', year)
                        if not os.path.exists(out_dir):
                            os.mkdir(out_dir)

                        # Make a month directory
                        out_dir = os.path.join(out_dir, month)
                        if not os.path.exists(out_dir):
                            os.mkdir(out_dir)

                        # Make a date directory
                        out_dir = os.path.join(out_dir, date)
                        if not os.path.exists(out_dir):
                            os.mkdir(out_dir)


                        # Copy the trajectory to the date directory
                        shutil.move(os.path.join(pth, dirname), os.path.join(out_dir, dirname))


if __name__ == '__main__':
    sortToDateDirs(sys.argv[1])
