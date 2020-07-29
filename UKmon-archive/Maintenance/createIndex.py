import sys, os, shutil, glob, datetime, csv
import numpy, math
from operator import itemgetter, attrgetter
sys.path.append('..')
import Formats.CameraDetails as fcd
import Formats.RMSFormats
import Formats.UAFormats

vers='V1.0' # version of this index
header='Shower,Y,M,D,h,m,s,mag,dur,az1,ev1,az2,ev2,site,lati,longi,alti,tz,jpgloc\n'

def main():
    if sys.argv.count == 1:
        yr='2020'
    else:
        yr = sys.argv[1]

    print ('Creating index of Meteor data')
    fnam = 'c:/users/mark/videos/astro/meteorcam/archive/camera-details.csv'
    camdets = numpy.loadtxt(fnam, delimiter=',',skiprows=1, dtype=Formats.CameraDetails.CameraDetails)
    fnam = 'c:/users/mark/videos/astro/meteorcam/archive/p_'+yr+'-unified.csv'
    pidata = numpy.loadtxt(fnam, delimiter=',',skiprows=1, dtype=Formats.RMSFormats.R90CSV)
    fnam = 'c:/users/mark/videos/astro/meteorcam/archive/m_'+yr+'-unified.csv'
    ufodata = numpy.loadtxt(fnam, delimiter=',',skiprows=1, dtype=Formats.UAFormats.UFOCSV, comments=None)

    print('read in '+ str(len(pidata))+' RMS records and ' +str(len(ufodata))+' UFO records')

    # create file if needed
    indexfile='c:/temp/ukmon-index.csv'
    if os.path.exists(indexfile):
        print('appending to index')
        f=open (indexfile, 'a', newline='')
    else:
        print('Creating index')
        f=open (indexfile, 'w', newline='')
        f.write(header)

    jpgbase='s3://ukmon-shared/archive/'
    print('Processing UFO file')
    csvw= csv.writer(f, delimiter=',')
    for p in ufodata:
        sidlid=p['Loc_Cam']
        lati, longi, alti, tz, site = fcd.GetCamDetails(sidlid, camdets)
        shwr=p['Group'].decode('utf-8').strip()
        if shwr[0] != '_':
            yyyy=str(p['Yr']).zfill(4)
            yymm=yyyy+str(p['Mth']).zfill(2)
            yymmdd=yymm+str(p['Day']).zfill(2)
            jpgpth=jpgbase+site+'/'+yyyy+'/'+yymm+'/'+yymmdd+'/'

            csvw.writerow([shwr,p['Yr'],p['Mth'],p['Day'],
                p['Hr'],p['Min'],p['Sec'],
                p['Mag'],p['Dur'],p['Dir1'],p['Alt1'], 0,0,
                p['Loc_Cam'].decode('utf-8').strip() ,longi, lati, alti, tz, jpgpth])

    print('Processing RMS file')
    shwr='nc'
    for p in pidata:
        sidlid=p['Loc_Cam']
        if p['Lati']==0:
            lati, longi, alti, tz, site = fcd.GetCamDetails(sidlid, camdets)
        else:
            _, _, _, _, site = fcd.GetCamDetails(sidlid, camdets)
            lati=p['Lati']
            longi=p['Longi']
            alti=p['Alti']
            tz=0
        yyyy=str(p['Yr'])
        yymm=yyyy+str(p['Mth'])
        yymmdd=yymm+str(p['Day'])
        jpgpth=jpgbase+site+'/'+yyyy+'/'+yymm+'/'+yymmdd+'/'
        csvw.writerow([shwr,p['Yr'],p['Mth'],p['Day'],
            p['Hr'],p['Min'],p['Sec'],
            p['Mag'],p['Dur'],p['Dir1'],p['Alt1'], p['Dir2'],p['Alt2'],
            p['Loc_Cam'].decode('utf-8').strip() ,longi, lati, alti, tz, jpgpth])
    
    f.close()

    print('making sure the data is unique')
    linelist = [line.rstrip('\n') for line in open(indexfile,'r')]
    newlist = sorted(set(linelist[1:]), key=itemgetter(1,2,3,4,5,6))
    fout=open (indexfile, 'w')
    fout.write(header)
    fout.write('\n'.join(newlist))
    fout.close()
    print("done")

if __name__ == '__main__':
    main()


