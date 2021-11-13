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

            if yr > 2020:
                srchfile = os.path.join(datadir, 'single', 'singles-{}.csv'.format(yr))
                cmd = ['wc', '-l', srchfile]
                dets = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
                detections = dets.split(' ')[0]

                srchfile = os.path.join(datadir, 'matched', 'matches-{}.csv'.format(yr))
                cmd = ['wc', '-l', srchfile]
                dets = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
                matches = dets.split(' ')[0]

                srchfile = os.path.join(datadir, 'reports', '{}'.format(yr), 'ALL','fblist.txt')
                cmd = ['wc', '-l', srchfile]
                fbdets = subprocess.run(cmd, stdout=subprocess.PIPE).stdout.decode('utf-8')
                fireballs = 0
                if len(fbdets) > 0:
                    fireballs = fbdets.split(' ')[0]
            else:
                srchfile = os.path.join(datadir, 'single', 'ALL{}.log'.format(yr))
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


if __name__ == '__main__':
    createSummaryTable(sys.argv[1], sys.argv[2])
