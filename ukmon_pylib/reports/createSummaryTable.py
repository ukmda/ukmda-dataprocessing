#
# Python module to create the archive website summary table for the front page
#
import sys
import os
import subprocess
import configparser as cfg


def createSummaryTable(fname, curryr):
    """Creates a summary of all data for the website front page. The table has four columns,
    the year, number of detections, number of matches and number of fireballs. 

    Args:
        fname (str): full path to the output file
        curryr (str): current year

    """
    srcdir = os.getenv('SRC')
    config = cfg.ConfigParser()
    config.read(os.path.join(srcdir, 'config', 'config.ini'))
    datadir = config['config']['datadir']
    with open(fname, 'w') as f:
        f.write('$(function() {\n')
        f.write('var table = document.createElement("table");\n')
        f.write('table.className = "table table-striped table-bordered table-hover table-condensed";\n')
        f.write('var header = table.createTHead();\n')
        f.write('header.className = "h4";\n')

        for yr in range(int(curryr), 2012, -1):

            if yr > 2019:
                srchfile = os.path.join(srcdir, 'logs', 'ALL{}.log'.format(yr))
                cmd = ['grep', 'OTHER Matched', srchfile]
                dets = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
                detections = dets.split(' ')[3]
            else:
                srchfile = os.path.join(datadir, 'consolidated', 'M_{}-unified.csv'.format(yr))
                cmd = ['wc', '-l', srchfile]
                dets = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
                detections = dets.split(' ')[0]

            srchfile = os.path.join(srcdir, 'logs', 'ALL{}.log'.format(yr))
            cmd = ['grep', 'UNIFIED Matched', srchfile]
            dets = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
            matches = dets.split(' ')[3]

            srchfile = os.path.join(datadir, 'reports', '{}'.format(yr), 'ALL','TABLE_Fireballs.csv')
            cmd = ['wc', '-l', srchfile]
            dets = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
            if len(dets) > 0:
                fireballs = dets.split(' ')[0]
                fireballs = int(fireballs)-1
            else:
                fireballs = 0

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


if __name__ == '__main__':
    createSummaryTable(sys.argv[1], sys.argv[2])
