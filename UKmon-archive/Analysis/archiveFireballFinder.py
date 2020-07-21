# check new CSV file for potential fireballs


def archiveFireBallFinder(fn, targ=-4):
    matches=[['group','localtime','mag','cam']]
    f1=open(fn,'r')
    lines=f1.readlines()
    for lin in lines[1:] :
        vals=lin.split(',')
        grp=vals[1]
        localtime=vals[2]
        mag=float(vals[3])
        cam=vals[6]
        if mag < targ:
            matches +=[[grp, localtime, mag, cam]]

    return matches


if __name__ == '__main__':
    targ=-2
    file1='c:/users/mark/videos/astro/meteorcam/tc/2020/202001/M20200104_05_027_TACKLEY_TC.CSV'
    items=archiveFireBallFinder(file1)
    for i in items:
        print(i)
    file2=''