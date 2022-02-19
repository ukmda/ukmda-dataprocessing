#
# Python code to create an index page for a single solution
#

import sys
import os
import shutil
import glob 


def createOrbitPageIndex(fldr):
    templatedir = os.getenv('TEMPLATES')
    if templatedir is None:
        templatedir ='~/pylibs/templates'
    templatedir = os.path.expanduser(templatedir)
    idxname = os.path.join(fldr, 'index.html')
    hdrname = os.path.join(templatedir, 'header.html')
    shutil.copy(hdrname, idxname)
    _, orbitname = os.path.split(fldr)
    pref = orbitname[:15] + '_'
    with open(idxname, 'a') as idxf:
        idxf.write(f"<h2>Orbital Analysis for matched events on {orbitname}</h2>\n")
        idxf.write("<a href=\"../index.html\">Back to daily index</a><hr>\n")

        idxf.write("<pre>\n")
        with open(os.path.join(fldr, 'summary.html')) as sumf:
            lis = sumf.readlines()
        idxf.writelines(lis)

        zipfs=glob.glob1(fldr, '*.zip')
        if len(zipfs) >0:
            idxf.write(f"Click <a href=\"./{zipfs[0]}\">here</a> to download a zip of the raw and processed data.\n")
        idxf.write("</pre>\n")
        idxf.write("<p><b>Detailed report below graphs</b></p>\n")
        idxf.write("<h3>Click on an image to see a larger view</h3>\n")

        idxf.write('<div class="top-img-container">\n')
        idxf.write(f'<a href="{pref}orbit_top.png"><img src="{pref}orbit_top.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}orbit_side.png"><img src="{pref}orbit_side.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}ground_track.png"><img src="{pref}ground_track.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}velocities.png"><img src="{pref}velocities.png" width="20%"></a>\n')
        idxf.write('<br>\n')

        with open(os.path.join(fldr, 'jpgs.html')) as sumf:
            lis = sumf.readlines()
        idxf.writelines(lis)

        idxf.write(f'<a href="{pref}lengths.png"><img src="{pref}lengths.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}lags_all.png"><img src="{pref}lags_all.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}abs_mag.png"><img src="{pref}abs_mag.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}abs_mag_ht.png"><img src="{pref}abs_mag_ht.png" width="20%\"></a>\n')
        idxf.write(f'<a href="{pref}all_angular_residuals.png"><img src="{pref}all_angular_residuals.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}all_spatial_total_residuals_height.png"><img src="{pref}all_spatial_total_residuals_height.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}3dtrack.png"><img src="{pref}3dtrack.png" width="20%"></a>\n')
        idxf.write('</div>\n')

        idxf.write("<div>\n")
        with open(os.path.join(fldr, 'mpgs.html')) as sumf:
            lis = sumf.readlines()
        idxf.writelines(lis)
        idxf.write("</div>\n")

        idxf.write("<pre>\n")
        #cat $repf >>$idxfile
        repfs=glob.glob1(fldr, '*report.txt')
        if len(repfs) > 0:
            with open(os.path.join(fldr, repfs[0])) as sumf:
                lis = sumf.readlines()
            idxf.writelines(lis)
        idxf.write("</pre>\n")
        idxf.write("<br>\n")

        idxf.write("<script> $('.top-img-container').magnificPopup({ \n")
        idxf.write("delegate: 'a', type: 'image', image:{")
        idxf.write("verticalFit:false}, gallery:{")
        idxf.write("enabled:true} }); \n")
        idxf.write("</script>\n")


        with open(os.path.join(templatedir, 'footer.html'), 'r') as footf:
            lis = footf.readlines()
        idxf.writelines(lis)
    return


if __name__ == '__main__':
    createOrbitPageIndex(sys.argv[1])
