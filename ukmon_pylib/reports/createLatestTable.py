import sys
import os
import datetime
import fileformats.CameraDetails as cd


def createLatestTable(jpglist, outdir):
    csvf = open(os.path.join(outdir, 'uploadtimes.csv'), 'w')
    csvf.write('StationID,DateTime\n')

    cinfo = cd.SiteInfo()

    with open(os.path.join(outdir, 'reportindex.js'), 'w') as outf:
        outf.write('$(function() {\n')
        outf.write('var table = document.createElement("table");\n')
        outf.write('table.className = "table table-striped table-bordered table-hover table-condensed";\n')
        outf.write('var header = table.createTHead();\n')
        outf.write('header.className = \"h4\";\n')

        for jpg in jpglist:
            jpg = ' '.join(jpg.split())
            if len(jpg) < 10:
                continue
            spls = jpg.split(' ')
            #print(spls)
            fn=spls[3]
            dt=spls[0]
            tm=spls[1]
            fname, _=os.path.splitext(fn)
            csvf.write(f'{fname},{dt}T{tm}.000Z\n')
            loc = cinfo.getCameraLocAndDir(fname)
            if loc != '':
                dtval = datetime.datetime.strptime(dt, '%Y-%m-%d')
                if (datetime.datetime.now() - dtval).days > 10:
                    print(f'{fname} late {dt}')
                    colidx = 'lightcoral'
                elif (datetime.datetime.now() - dtval).days > 3:
                    print(f'{fname} late {dt}')
                    colidx = 'darkorange'
                else:
                    colidx = 'white'
                
                outf.write('var row = table.insertRow(-1);\n')
                outf.write(f'row.style.backgroundColor="{colidx}";\n') 
                outf.write('var cell = row.insertCell(0);\n')
                cellstr=f'{fname}<br>{loc}<br>{dt}<br>{tm}'
                outf.write(f'cell.innerHTML = "{cellstr}";\n')
                outf.write('var cell = row.insertCell(1);\n')
                outf.write(f'cell.innerHTML = "<a href=./{fname}.jpg><img src=./{fname}.jpg width=100%></a>";\n')
                outf.write('var cell = row.insertCell(2);\n')
                outf.write(f'cell.innerHTML = "<a href=./{fname}.png><img src=./{fname}.png width=100%></a>";\n')
                outf.write('var cell = row.insertCell(3);\n')
                outf.write(f'cell.innerHTML = "<a href=./{fname}_cal.jpg><img src=./{fname}_cal.jpg width=100%></a>";\n')
            else:
                print(f'camera {fname} inactive')

        outf.write('var outer_div = document.getElementById("summary");\n')
        outf.write('outer_div.appendChild(table);\n')
        outf.write('})\n')

    csvf.close()
    return


if __name__ == '__main__':
    with open(sys.argv[1], 'r') as inf:
        jpglist = inf.readlines()
    createLatestTable(jpglist, sys.argv[2])
