#
# Python code to create an index page for a single solution
# Copyright (C) 2018-2023 Mark McIntyre
#

import sys
import os
import shutil


def createOrbitPageIndex(fldr, websitebucket, s3):
    hdrname = '/tmp/header.txt'
    ftrname = '/tmp/footer.txt'
    if not os.path.isfile(hdrname):
        key='templates/header.html'
        s3.meta.client.download_file(websitebucket, key, hdrname)
        key='templates/footer.html'
        s3.meta.client.download_file(websitebucket, key, ftrname)

    idxname = os.path.join(fldr, 'index.html')
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

        zipf = orbitname + '.zip'
        if os.path.isfile(os.path.join(fldr, zipf)):
            idxf.write(f"Click <a href=\"./{zipf}\">here</a> to download a zip of the raw and processed data.\n")
        idxf.write("</pre>\n")
        idxf.write("<p><b>Detailed report below graphs</b></p>\n")
        idxf.write("<h3>Click on an image to see a larger view</h3>\n")

        idxf.write('<div class="top-img-container">\n')
        idxf.write(f'<a href="{pref}orbit_top.png"><img src="{pref}orbit_top.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}orbit_side.png"><img src="{pref}orbit_side.png" width="20%"></a>\n')
        if os.path.isfile(os.path.join(fldr, f'{pref}OSM_ground_track.png')):
            idxf.write(f'<a href="{pref}OSM_ground_track.png"><img src="{pref}OSM_ground_track.png" width="20%"></a>\n')
        else:
            idxf.write(f'<a href="{pref}ground_track.png"><img src="{pref}ground_track.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}velocities.png"><img src="{pref}velocities.png" width="20%"></a>\n')
        idxf.write('<br>\n')

        with open(os.path.join(fldr, 'jpgs.html')) as sumf:
            lis = sumf.readlines()            
        if os.path.isfile(os.path.join(fldr, 'extrajpgs.html')):
            print('reading extrajpgs.html')
            with open(os.path.join(fldr, 'extrajpgs.html')) as sumf:
                lis2 = sumf.readlines()
            for li in lis2:
                lis.append(li)
        lis = list(dict.fromkeys(lis))
        idxf.writelines(lis)

        idxf.write(f'<a href="{pref}lengths.png"><img src="{pref}lengths.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}lags_all.png"><img src="{pref}lags_all.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}abs_mag.png"><img src="{pref}abs_mag.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}abs_mag_ht.png"><img src="{pref}abs_mag_ht.png" width="20%\"></a>\n')
        idxf.write(f'<a href="{pref}all_angular_residuals.png"><img src="{pref}all_angular_residuals.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}all_spatial_total_residuals_height.png"><img src="{pref}all_spatial_total_residuals_height.png" width="20%"></a>\n')
        idxf.write(f'<a href="{pref}2dtrack.png"><img src="{pref}2dtrack.png" width="20%"></a>\n')
        idxf.write('</div>\n')

        idxf.write("<div>\n")
        with open(os.path.join(fldr, 'mpgs.html')) as sumf:
            lis = sumf.readlines()
        if os.path.isfile(os.path.join(fldr, 'extrampgs.html')):
            with open(os.path.join(fldr, 'extrampgs.html')) as sumf:
                lis2 = sumf.readlines()
            for li in lis2:
                lis.append(li)
        lis = list(dict.fromkeys(lis))
        idxf.writelines(lis)
        idxf.write("</div>\n")

        idxf.write("<pre>\n")
        repf = os.path.join(fldr, pref + 'report.txt')
        #print(repf)
        if os.path.isfile(repf):
            with open(repf) as sumf:
                lis = sumf.readlines()
            idxf.writelines(lis)
        idxf.write("</pre>\n")
        idxf.write("<br>\n")

        idxf.write("<script> $('.top-img-container').magnificPopup({ \n")
        idxf.write("delegate: 'a', type: 'image', image:{")
        idxf.write("verticalFit:false}, gallery:{")
        idxf.write("enabled:true} }); \n")
        idxf.write("</script>\n")


        with open(ftrname, 'r') as footf:
            lis = footf.readlines()
        idxf.writelines(lis)
    return


if __name__ == '__main__':
    createOrbitPageIndex(sys.argv[1])
