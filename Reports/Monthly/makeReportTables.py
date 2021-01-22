#
# create HTML report and tables from UKMON analysis routines
#
import csv
import os
import sys
import configparser


def makeOrbitList(root, yr, shwr):
    of = open('listoforbits.html', 'w')

    of.write('<br><table id="tablestyle">\n')
    of.write('</table>\n')
    of.close()


def makeFBGraphs(root, yr, shwr, fbcount):
    of = open('fireballgraphs.html', 'w')
    if fbcount > 0:
        of.write('<p>A breakdown is shown below. </p>')
        of.write('<a href="fireball_by_month.jpg"><img src="fireball_by_month.jpg" width="30%"></a>')
        of.write('<a href="fireball_by_stream.jpg"><img src="fireball_by_stream.jpg" width="30%"></a>')
        s = '<p>The brightest fireballs observed during ' + yr + ' were:</p>'
        of.write(s)
    else:
        of.write('')
    of.close()


def makeFBTable(root, yr, shwr, fbcount):
    of = open('fireballtable.html', 'w')
    if fbcount > 0:
        of.write('<br><table id="tablestyle">\n')
        of.write('<tr><td><b>DateTime</td><td><b>Magnitude</td><td><b>Stream</td><td><b>Station Matches</td></tr>\n')
        fname = os.path.join(root, yr, shwr, 'TABLE_Fireballs.csv')
        with open(fname, 'r') as inf:
            data = csv.reader(inf, delimiter=',')
            _ = next(data)  # skip the header row
            i = 0
            for r in data:
                dt = r[0]
                mag = '{:.2f}'.format(float(r[1]))
                shwr = r[2]
                cnt = r[3]
                of.write('<tr><td>{:s}</td><td>{:s}</td><td>{:s}</td><td>{:s}</td></tr>\n'.format(dt, mag, shwr, cnt))
                i = i + 1
                if i == 10:
                    break
        of.write('</table>\n')
    else:
        of.write('')
    of.close()


def createTables(root, yr, shwr, fbcount):
    makeFBGraphs(root, yr, shwr, fbcount)
    makeFBTable(root, yr, shwr, fbcount)
    makeOrbitList(root, yr, shwr)


if __name__ == '__main__':

    if len(sys.argv) < 3:
        print('usage: makeReportIndex.py shower|all year ')
    else:
        shwr = sys.argv[1]
        yr = sys.argv[2]
        fbcount = int(sys.argv[3])
        config = configparser.ConfigParser()
        config.read("/home/ec2-user/src/config/config.ini")
        root = config['config']['REPORTDIR']

        createTables(root, yr, shwr, fbcount)
