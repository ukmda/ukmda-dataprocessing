# Copyright (C) 2018-2023 Mark McIntyre
#
# Python module to create the archive website summary table for the front page
#
import os
import pandas as pd
import datetime


def createSummaryTable(curryr=None, datadir=None):
    """Creates a summary of all data for the website front page. The table has four columns,
    the year, number of detections, number of matches and number of fireballs. 

    Args:
        curryr (str): current year

    """
    if curryr is None:
        curryr = str(datetime.datetime.now().year)
    if datadir is None:
        datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    fname = os.path.join(datadir, 'summarytable.js')
    with open(fname, 'w') as f:
        f.write('$(function() {\n')
        f.write('var table = document.createElement("table");\n')
        f.write('table.className = "table table-striped table-bordered table-hover table-condensed";\n')
        f.write('var header = table.createTHead();\n')
        f.write('header.className = "h4";\n')

        for yr in range(int(curryr), 2012, -1):

            if yr > 2020:
                srchfile = os.path.join(datadir, 'single', 'singles-{}.parquet.snap'.format(yr))
                if os.path.isfile(srchfile):
                    sngl = pd.read_parquet(srchfile, columns=['Y'])
                    detections = len(sngl[sngl.Y==yr])
                else:
                    detections = 0

                srchfile = os.path.join(datadir, 'matched', 'matches-full-{}.parquet.snap'.format(yr))
                if os.path.isfile(srchfile):
                    mtch = pd.read_parquet(srchfile, columns=['_Y_ut'])
                    matches = len(mtch[mtch._Y_ut==yr])
                else:
                    matches = 0

                srchfile = os.path.join(datadir, 'reports', '{}'.format(yr), 'fireballs','fblist.txt')
                if os.path.isfile(srchfile):
                    fireballs = sum(1 for line in open(srchfile))
                else:
                    fireballs = 0
            else:
                srchfile = os.path.join(datadir, 'single', 'ALL{}.log'.format(yr))
                if os.path.isfile(srchfile):
                    with open(srchfile) as inf:
                        lis = inf.readlines()
                    matches = lis[0].split(' ')[3].strip()
                    detections = lis[1].split(' ')[3].strip()
                    fireballs = lis[2].split(' ')[3].strip()

            f.write('var row = table.insertRow(-1);\n')
            f.write('var cell = row.insertCell(0);\n')
            f.write('cell.innerHTML = "<a href=/reports/{}/ALL/index.html>{}</a>";\n'.format(yr, yr))
            f.write('var cell = row.insertCell(1);\n')
            f.write('cell.innerHTML = "{}";\n'.format(detections))
            f.write('var cell = row.insertCell(2);\n')
            f.write('cell.innerHTML = "<a href=/reports/{}/orbits/index.html>{}</a>";\n'.format(yr, matches))
            f.write('var cell = row.insertCell(3);\n')
            f.write('cell.innerHTML = "<a href=/reports/{}/fireballs/index.html>{}</a>";\n'.format(yr,fireballs))

        f.write('var row = header.insertRow(0);\n')
        f.write('var cell = row.insertCell(0);\n')
        f.write('cell.innerHTML = "Year";\n')
        f.write('cell.className = "small";\n')
        f.write('var cell = row.insertCell(1);\n')
        f.write('cell.innerHTML = "Detections";\n')
        f.write('cell.className = "small";\n')
        f.write('var cell = row.insertCell(2);\n')
        f.write('cell.innerHTML = "Matches";\n')
        f.write('cell.className = "small";\n')
        f.write('var cell = row.insertCell(3);\n')
        f.write('cell.innerHTML = "Fireballs";\n')
        f.write('cell.className = "small";\n')

        f.write('var outer_div = document.getElementById("summarytable");\n')
        f.write('outer_div.appendChild(table);\n')
        f.write('})\n')
