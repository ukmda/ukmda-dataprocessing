#
#  Various summary analyses
#  
# Copyright (C) 2018-2023 Mark McIntyre

import pandas as pd
from traj import pickleAnalyser as pa
import os
import sys
import shutil
import datetime 


def showerSummaryByPeriod(dtstr):
    yr = int(dtstr[:4])
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    cols = ['_stream','_M_ut']
    filt = None
    matchfile = os.path.join(datadir, 'matched', 'matches-full-{}.parquet.snap'.format(yr))
    mtch = pd.read_parquet(matchfile, columns=cols, filters=filt)
    if len(dtstr) > 4:
        mth = int(dtstr[4:6])
        mtch = mtch[mtch._M_ut == mth]
    grpdata = mtch.groupby(by=['_stream']).count()
    grpdata = grpdata.sort_values(by=['_M_ut'], ascending=False)
    grpdata['stream'] = grpdata.index
    shwrdata=[(shwr, pa.getShowerDets(shwr),ct)  for shwr, ct in zip(grpdata.stream,grpdata._M_ut)]
#    for sh in shwrdata:
#        print(sh[0], sh[1][1], sh[1][3], sh[2])

    return shwrdata


def createSummWebpage(dtstr, outdir=None):
    yr = dtstr[:4]
    mth = None
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    if len(dtstr) > 4:
        mth = dtstr[4:6]
        if outdir is None:
            outdir = os.path.join(datadir, 'reports', yr, 'showers', mth)
    else:
        if outdir is None:
            outdir = os.path.join(datadir, 'reports', yr, 'showers')
    os.makedirs(outdir, exist_ok=True)
    templatedir=os.getenv('TEMPLATES', default='/home/ec2-user/prod/website/templates')
    idxfile = os.path.join(outdir, 'index.html')
    shutil.copyfile(os.path.join(templatedir, 'header.html'), idxfile)
    with open(idxfile, 'a+') as outf:
        if mth is not None:
            outf.write(f'<a href=../index.html>back to index for {yr}</a><br>\n')
            mthno = int(mth)    
            if mthno > 1:
                outf.write(f'<a href=../{mthno-1:02d}/index.html>Previous Month</a><br>\n') 
            if mthno < 12:
                outf.write(f'<a href=../{mthno+1:02d}/index.html>Next Month</a><br>\n') 
        else:
            outf.write('<a href=../index.html>back to Index</a>\n')
        outf.write(f'<h2>Shower Summary report for {dtstr}</h2>\n')
        outf.write('<p>This report shows the number of matches per shower for the period. Where a detailed ')
        outf.write('shower report is available, it is linked</p><br>')
        outf.write('Last updated: {}<br>'.format(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        outf.write('<div id="shwrtable"></div>\n')
        outf.write('<script src="./showersummary.js"></script><hr>\n')
        with open(os.path.join(templatedir, 'footer.html'), 'r') as inf:
            lis = inf.readlines()
        outf.writelines(lis)
        outf.close()

    return 


def createSummJS(dtstr, shwrdata, maxlines=None):
    yr = dtstr[:4]
    mth = None
    datadir = os.getenv('DATADIR', default='/home/ec2-user/prod/data')
    if len(dtstr) > 4:
        mth = dtstr[4:6]
        outdir = os.path.join(datadir, 'reports', yr, 'showers', mth)
    else:
        outdir = os.path.join(datadir, 'reports', yr, 'showers')
    os.makedirs(outdir, exist_ok=True)
    if maxlines is None:
        maxlines=999999 
    with open(os.path.join(outdir, 'showersummary.js'), 'w') as shwrf:
        shwrf.write('$(function() {\n')
        shwrf.write('var table = document.createElement(\"table\");\n')
        shwrf.write('table.className = \"table table-striped table-bordered table-hover table-condensed w-100\";\n')
        shwrf.write('table.setAttribute("id", "showertableid");')
        lc = 1
        for shwr in shwrdata:
            if shwr[0] == 'spo':
                continue # skip sporadics
            if lc > maxlines:
                break # limit the number of rows in the report
            lc = lc + 1
            shwrf.write('var row = table.insertRow(-1);\n')
            shwrf.write('var cell = row.insertCell(-1);\n')
            if os.path.isdir(os.path.join(outdir, '..', shwr[0])):
                #shwrf.write(f'cell.innerHTML = "<a href=./{m:02d}/index.html>{m:02d}</a>";\n')
                shwrf.write(f'cell.innerHTML = "<a href=../{shwr[0]}/index.html>{shwr[0]}</a>";\n')
            else:
                shwrf.write(f'cell.innerHTML = "{shwr[0]}";\n')
            shwrf.write('var cell = row.insertCell(-1);\n')
            shwrf.write(f'cell.innerHTML = "{shwr[1][1]}";\n')
            shwrf.write('var cell = row.insertCell(-1);\n')
            shwrf.write(f'cell.innerHTML = "{shwr[1][3]}";\n')
            shwrf.write('var cell = row.insertCell(-1);\n')
            shwrf.write(f'cell.innerHTML = "{shwr[2]}";\n')
        shwrf.write('var header = table.createTHead();\n')
        shwrf.write('var row = header.insertRow(0);\n')
        shwrf.write('var cell = row.insertCell(-1);\n')
        shwrf.write(f'cell.innerHTML = "Code";\n')
        shwrf.write('var cell = row.insertCell(-1);\n')
        shwrf.write(f'cell.innerHTML = "Name";\n')
        shwrf.write('var cell = row.insertCell(-1);\n')
        shwrf.write(f'cell.innerHTML = "Peak Date";\n')
        shwrf.write('var cell = row.insertCell(-1);\n')
        shwrf.write(f'cell.innerHTML = "Matches";\n')
        shwrf.write('var outer_div = document.getElementById(\"shwrtable\");\n')
        shwrf.write('outer_div.appendChild(table);\n')
        shwrf.write('})\n')
        shwrf.write('$(document).ready(function() {\n')
        shwrf.write('$("#showertableid").DataTable({\n')
        shwrf.write('columnDefs : [\n')
        shwrf.write('{ Type : "date", targets : [2],\n')
        shwrf.write('Type : "numeric", targets : [3]}\n')
        shwrf.write('	],\n')
        shwrf.write('order : [[ 3, "desc"],[2,"asc"]],\n')
        shwrf.write('paging: false\n')
        shwrf.write('});\n});\n')
    return 

if __name__ == '__main__':
    dtstr = sys.argv[1]
    maxrows = None
    if len(sys.argv) >2:
        maxrows = int(sys.argv[2])
    shwrdata = showerSummaryByPeriod(dtstr)
    createSummJS(dtstr, shwrdata, maxlines=maxrows)
    createSummWebpage(dtstr)

