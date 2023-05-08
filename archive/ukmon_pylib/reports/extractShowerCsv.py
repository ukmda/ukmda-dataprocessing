# Copyright (C) 2018-2023 Mark McIntyre
#
# wrapper around extractors.createSplitMatchFile
# to allow it to be called from bash scripts easily

import sys
from reports.extractors import createSplitMatchFile, createUFOSingleMonthlyExtract, createRMSSingleMonthlyExtract


if __name__ =='__main__':
    if sys.argv[3] =='M':
        createSplitMatchFile(sys.argv[1], shwr=sys.argv[2])
    if sys.argv[3] =='R':
        createRMSSingleMonthlyExtract(sys.argv[1], shwr=sys.argv[2])
    if sys.argv[3] =='U':
        createUFOSingleMonthlyExtract(sys.argv[1], shwr=sys.argv[2])
