#
# Python script to report on active showers
#

import sys
import datetime
import os
import glob
import shutil

from utils.getActiveShowers import getActiveShowers
from analysis.showerAnalysis import showerAnalysis
from reports.findFireballs import findFireballs


def createShowerIndexPage(dtstr, shwr, shwrname, outdir, datadir):
    templdir = os.getenv('TEMPLATES', default='/home/ec2-user/prod/website/templates')
    idxfile = os.path.join(outdir, 'index.html')
    shutil.copyfile(os.path.join(templdir,'header.html'), idxfile)

    thismth = None
    if len(dtstr) > 4:
        thismth = dtstr[4:6]
        
    with open(idxfile, 'a') as outf:
        # header info
        if shwrname == 'All Showers':
            shwrname = f'Summary Statistics for All Showers for {dtstr}'
        outf.write(f'<h2>{shwrname}</h2>\n')
        outf.write('<a href="/reports/index.html">Back to report index</a><br>\n')
        #outf.write('</tr></table>')

        # add the shower information file, if present
        shwrinfofile = os.path.join(datadir, 'shwrinfo', f'{shwr}.txt')
        if os.path.isfile(shwrinfofile):
            outf.write('<pre>\n')
            with open(shwrinfofile, 'r') as inf:
                for line in inf:
                    outf.write(f'{line}')
            outf.write('</pre>\n')

        # shower stats
        shwrinfofile = os.path.join(outdir, 'statistics.txt')
        if os.path.isfile(shwrinfofile):
            outf.write('<pre>\n')
            with open(shwrinfofile, 'r') as inf:
                for line in inf:
                    outf.write(f'{line}')
            if shwr == 'ALL':
                outf.write(f'Click <a href="/browse/annual/matches-{dtstr}.csv">here</a> to download the matched data.\n')
            else:
                outf.write(f'Click <a href="/browse/showers/{dtstr}-{shwr}-matches.csv">here</a> to download the matched data.\n')
            outf.write('</pre>\n')
        outf.write('<br>\n')
        # brightest event list
        fbinfofile = os.path.join(outdir, 'fblist.txt')
        if os.path.isfile(fbinfofile):
            with open(os.path.join(outdir, 'reportindex.js'), 'w') as jsout:
                jsout.write('$(function() {\n')
                jsout.write('var table = document.createElement("table");\n')
                jsout.write('table.className = "table table-striped table-bordered table-hover table-condensed";\n')
                jsout.write('var header = table.createTHead();\n')
                jsout.write('header.className = "h4";\n')
                jsout.write('var row = table.insertRow(-1);\n')
                jsout.write('var cell = row.insertCell(0);\n')
                jsout.write('cell.innerHTML = "Brightest Ten Events";\n')
                with open(fbinfofile, 'r') as fbf:
                    fblis = fbf.readlines()
                for li in fblis:
                    jsout.write('var row = table.insertRow(-1);\n')
                    jsout.write('var cell = row.insertCell(0);\n')
                    fldr, mag, fbshwr, bn = li.strip().split(',')
                    jsout.write(f'cell.innerHTML = "<a href={fldr}>{bn}</a>";\n')
                    jsout.write('var cell = row.insertCell(1);\n')
                    jsout.write(f'cell.innerHTML = "{mag}";\n')
                    jsout.write('var cell = row.insertCell(2);\n')
                    jsout.write(f'cell.innerHTML = "{fbshwr}";\n')

                jsout.write('var outer_div = document.getElementById("summary");\n')
                jsout.write('outer_div.appendChild(table);\n')
                jsout.write('})\n')

            outf.write('<div class="row">\n')
            outf.write('<div class="col-lg-12">\n')
            outf.write('    <div id="summary" class="table-responsive"></div>\n')
            outf.write('    <div id="reportindex"></div>\n')
            outf.write('</div>\n')
            outf.write('</div>\n')
            outf.write('<script src="./reportindex.js"></script>\n')

        # additional information
        outf.write('<h3>Additional Information</h3>\n')
        outf.write('The graphs and histograms below show more information about the velocity, magnitude \n')
        outf.write('start and end altitude and other parameters. Click for larger view. \n')
        # add the charts and stuff
        jpglist = glob.glob1(outdir, '*.jpg')
        pnglist = glob.glob1(outdir, '*.png')
        outf.write('<div class="top-img-container">\n')
        for j in jpglist:
            outf.write(f'<a href="./{j}"><img src="./{j}" width="20%"></a>\n')
        for j in pnglist:
            outf.write(f'<a href="./{j}"><img src="./{j}" width="20%"></a>\n')
        outf.write('</div>\n')

        outf.write("<script> $('.top-img-container').magnificPopup({ \n")
        outf.write("delegate: 'a', type: 'image', image:{verticalFit:false}, gallery:{enabled:true} }); \n")
        outf.write('</script>\n')

        # links to monthly reports
        if thismth is None and shwr == 'ALL':
            outf.write('<h3>Monthly reports</h3>monthly reports can be found at the links below<br>')
            outf.write('<div id="mthtable" class="table-responsive"></div>\n')
            outf.write('<script src="./mthtable.js"></script><hr>\n')
            mfname = os.path.join(outdir, 'mthtable.js')
            with open(mfname, 'w') as mthf:
                mthf.write('$(function() {\n')
                mthf.write('var table = document.createElement(\"table\");\n')
                mthf.write('table.className = \"table table-striped table-bordered table-hover table-condensed\";\n')

                currmth = datetime.datetime.now().month            
                for m in range(1,currmth+1):
                    if m == 1 or m== 7:
                        mthf.write('var row = table.insertRow(-1);\n')
                    mthf.write('var cell = row.insertCell(-1);\n')
                    mthf.write(f'cell.innerHTML = "<a href=./{m:02d}/index.html>{m:02d}</a>";\n')

                mthf.write('var outer_div = document.getElementById(\"mthtable\");\n')
                mthf.write('outer_div.appendChild(table);\n')
                mthf.write('})\n')

        # page footer
        with open(os.path.join(templdir, 'footer.html')) as ftr:
            lis = ftr.readlines()
            for li in lis:
                outf.write(f'{li}\n')

    return


def findRelevantPngs(shwr, pltdir, outdir):
    pngs = f'{pltdir}/*{shwr}.png'
    plts = glob.glob(pngs)
    if len(plts) > 0:
        _, fnam = os.path.split(plts[0])
        shutil.copyfile(plts[0], os.path.join(outdir, fnam))
    return


def reportActiveShowers(ymd, thisshower=None, thismth=None):
    if thisshower is None:
        shwrlist = getActiveShowers(ymd, retlist=True)
    else:
        shwrlist = [thisshower]

    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    pltdir=os.path.join(datadir, 'showerplots')
    dtstr = ymd.strftime('%Y')
    if thismth is not None:
        dtstr = dtstr + thismth

    for shwr in shwrlist:
        print(f'processing {shwr} for {dtstr}')
        shwrname = showerAnalysis(shwr, int(dtstr))
        findFireballs(int(dtstr), shwr, 999)
        if thismth is None:
            outdir=os.path.join(datadir, 'reports', dtstr, shwr)
        else:
            outdir=os.path.join(datadir, 'reports', dtstr[:4], shwr, thismth)
        findRelevantPngs(shwr, pltdir, outdir)
        createShowerIndexPage(dtstr, shwr, shwrname, outdir, datadir)
    return shwrlist


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ymd = datetime.datetime.strptime(sys.argv[1], '%Y%m%d')
    else:
        ymd = datetime.datetime.now()
    if len(sys.argv) > 2:
        thisshower = sys.argv[2]
    else:
        thisshower = None
    if len(sys.argv) > 3:
        thismth = sys.argv[3]
    else:
        thismth = None

    shwrs = reportActiveShowers(ymd, thisshower, thismth)
