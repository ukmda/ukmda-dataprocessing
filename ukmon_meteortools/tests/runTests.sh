#!/bin/bash

PYTHONPATH=$WMPL_LOC:$RMS_LOC:.:..
export PYTHONPATH

pytest -v ./tests --cov=. 
