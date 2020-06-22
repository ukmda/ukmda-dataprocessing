import sys, os, shutil, glob, datetime
import numpy, math
sys.path.append('..')
import Formats.UAFormats as UAFormats
import VectorMaths

def compare(row1, row2,i, f):
    cam1=row1['Loc_Cam'].strip().decode('utf-8')
    cam2=row2['Loc_Cam'].strip().decode('utf-8')
    ul=cam1.rfind('_')
    loc1=cam1[:ul]
    if ul+1==len(cam1):
        c1='c1'
    else:
        c1=cam1[ul+1:]
    ul=cam2.rfind('_')
    loc2=cam2[:ul]
    if ul+1==len(cam2):
        c2='c1'
    else:
        c2=cam2[ul+1:]

    sx = row1['Sec']
    s = int(math.floor(sx))
    if s==60:
        s=59
        ms=999999
    else:
        ms = int((sx-s)*1000000)
    t1 = datetime.datetime(row1['Yr'], row1['Mth'], row1['Day'], \
        row1['Hr'], row1['Min'], s, ms)
    sx = row2['Sec']
    s = int(math.floor(sx))
    if s==60:
        s=59
        ms=999999
    else:
        ms = int((sx-s)*1000000)
    t2 = datetime.datetime(row2['Yr'], row2['Mth'], row2['Day'], \
        row2['Hr'], row2['Min'],s,ms )
    if t2 < t1 :
        tdiff = t1-t2
    else:
        tdiff = t2-t1
    sdiff = abs(tdiff.seconds + tdiff.microseconds/1000000)
    
    if loc1[:7] == 'Lockyer':
        loc1='Lockyer'
    if loc2[:7] == 'Lockyer':
        loc2='Lockyer'
    if loc1 != loc2 and  sdiff < 3.001: 
        i=i+1
        ra1=str(row1['Ra1'])
        ra2=str(row2['Ra1'])
        dec1=str(row1['Dec1'])
        dec2=str(row2['Dec1'])
        dir1=str(row1['Dir1'])
        dir2=str(row2['Dir1'])
        dts1=t1.strftime('%Y%m%d_%H%M%S')
        outstr =str(i)+','+loc1+'_'+c1+','+loc2+'_'+c2+','+dts1+','+dir1+','+dir2+','+ra1+','+ra2+','+dec1+','+dec2+'\n'
        f.write(outstr)
        return 1, i
    else:
        return 0, i


def main():
    dummy =1
    yr = sys.argv[1]
    if len(sys.argv) > 2 :
        dummy = sys.argv[2]
    fnam = 'c:/users/mark/videos/astro/meteorcam/archive/m_' + yr + '-unified.csv'
    tmpfnam='c:/temp/m_' + yr + '-unified-fixed.csv'
    print(fnam)
    with open(fnam,'r') as file:
        filedata = file.read()
    filedata = filedata.replace('$','0')
    with open(tmpfnam,'w') as file:
        file.write(filedata)

    outfnam='c:/temp/matches-'+yr+'.csv'
    f=open (outfnam, "w")
    f.write('id,Cam1,Cam2,date_time,dir1,dir2,ra1,ra2,dec1,dec2\n')
    print (outfnam)

    mydata = numpy.loadtxt(tmpfnam, delimiter=',',skiprows=1, dtype=UAFormats.UFOCSV)

    sorteddata=numpy.sort(mydata, order=['LocalTime', 'Mag'])

    numrows = numpy.size(sorteddata, 0)
    j=0
    for i in range(numrows-1):
        row1=sorteddata[i]
        row2=sorteddata[i+1]
        ismatch, j = compare(row1, row2, j, f)
    f.close()

if __name__ == '__main__':
    main()
