"""
copyright Mark McIntyre, 2026-

A script to create the various charts from a trajectory pickle

"""
import sys
import os
import glob
import argparse
from wmpl.Utils.Pickling import loadPickle

def makePlots(trajfldr):
    print(f'checking {trajfldr} and subfolders')
    for pth, dirs, files in os.walk(trajfldr):
        for fil in files:
            if '.pickle' in fil:
                trajname = os.path.join(pth, fil)
                print(f'processing {fil}')
                traj = loadPickle(trajfldr, trajname)
                traj.save_results = True
                traj.savePlots(trajfldr, trajname[:15], show_plots=False)
    print('done')


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser(description='create plots from a set of trajectory pickles')
    arg_parser.add_argument('dir_path', metavar='DIR_PATH', type=str, 
        help='Path to folder containing trajectory pickles to analyse')
    cml_args = arg_parser.parse_args()

    makePlots(cml_args.dir_path)