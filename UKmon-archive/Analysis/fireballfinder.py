import sys
import os
import shutil
import glob
import numpy
import UAData

def main():
    dummy =1
    yr = sys.argv[1]
    if len(sys.argv) > 2 :
        dummy = sys.argv[2]
    fnam = 'c:/users/mark/videos/astro/meteorcam/archive/m_' + yr + '-unified.csv'
    print(fnam)
    mydata = numpy.loadtxt(fnam, delimiter=',',skiprows=1, dtype=UAData.UAData)

    for myrow in mydata:
        m =myrow['Mag']
        stn =myrow['Loc_Cam'].strip().decode('utf-8')
        datstr=myrow['LocalTime'].strip().decode('utf-8')
        if m < -3.999  and stn[:4] == 'TACK':
            print (m, stn, datstr)
            recf='c:/users/mark/videos/astro/meteorcam/fireballs/fireballs.txt'
            if dummy == 0 : 
                fout = open(recf,'a+')            
                ostr=('%s %s %s\n' % (datstr, stn, m))
                fout.write (ostr)
                fout.close()

            dirnam='c:/users/mark/videos/astro/meteorcam/fireballs/M'+datstr
            try: 
                os.mkdir(dirnam)
            except:
                pass
            cnam = stn[8:10]
            yr = myrow['Yr']
            mth = myrow['Mth']
            day = myrow['Day']
            hr = myrow['Hr']

            if yr > 2018:
                src = 'c:/users/mark/videos/astro/meteorcam/'
            else:
                src = 'g:/astrovideo/meteorcam/'
            src = src +cnam+'/'+('%4.4d' %yr) 
            src = src +'/'+('%4.4d' % yr)+('%2.2d' % mth) 
            src = src + '/' +('%4.4d' % yr)+('%2.2d' % mth)+('%2.2d' % day) 
            src = src + '/M' + datstr + '*'
            #print(src)
            flist = glob.glob(src)
            for f in flist:
                if dummy == 0 : 
                    shutil.copy(f, dirnam)
                else: 
                    print ('would have copied ' + f + ' to ' +dirnam)
            if flist.count == 0 :
                print ('no files found in %s\n' % src )

            if hr < 13 :
                 day = day-1
            if day < 1 :
                mth = mth-1
                day = 30
                if mth in (1,3,5,7,8,10,12) :
                    day=31
                if mth == 2 :
                    day = 28
            if yr > 2018:
                src = 'c:/users/mark/videos/astro/meteorcam/'
            else:
                src = 'g:/astrovideo/meteorcam/'
            src = src +cnam+'/'+('%4.4d' %yr) 
            src = src +'/'+('%4.4d' % yr)+('%2.2d' % mth) 
            src = src + '/' +('%4.4d' % yr)+('%2.2d' % mth)+('%2.2d' % day) 
            src = src + '/M' + datstr + '*'
            #print(src)
            flist = glob.glob(src)
            for f in flist:
                shutil.copy(f, dirnam)
            if flist.count == 0 :
                print ('no files found in %s\n' % src )

if __name__ == '__main__':
    main()
