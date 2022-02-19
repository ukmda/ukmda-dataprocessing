""" Functions for pickling and unpickling Python objects. """

from __future__ import print_function, absolute_import

import os
import pickle


def savePickle(obj, dir_path, file_name):
    os.makedirs(dir_path, exist_ok=True)
    with open(os.path.join(dir_path, file_name), 'wb') as f:
        pickle.dump(obj, f, protocol=2)


def loadPickle(dir_path, file_name):
    with open(os.path.join(dir_path, file_name), 'rb') as f:
        p = pickle.load(f, encoding='latin1')

        if hasattr(p, "uncertainties"):
            p.uncertanties = p.uncertainties

        if hasattr(p, "uncertanties"):
            p.uncertainties = p.uncertanties

        # Check if the pickle file is a trajectory file
        if hasattr(p, 'orbit') and hasattr(p, 'observations'):
            if p.orbit is not None:
                p.orbit.fixMissingParameters()

        return p
