#
# python code to update the FTP and platepars file 
# after manually reducing a fireball
#
import os
import sys
import glob 
import shutil


def updateFTPfile(ftpfile, manftp):
    # read in the manually created FTP file and extract the useful bits
    with open(manftp,'r') as minf:
        lis = minf.readlines()
    reqlines = lis[11:]
    bits = lis[0].split(' ')
    addmets = int(bits[3].strip())  # additional meteors 

    # read in the full FTP file
    with open(ftpfile, 'r') as ftpf:
        fulldata = ftpf.readlines()
    
    # add the extra meteors to the count
    bits = fulldata[0].split(' ')
    metcount = int(bits[3].strip())
    fulldata[0] = 'Meteor Count = {:06d}\n'.format(metcount+addmets)

    # copy the data and add the new lines
    newdata = fulldata
    for i in range(len(reqlines)):
        newdata.append(reqlines[i])
    with open(ftpfile, 'w') as outf:
        outf.writelines(newdata)
    return


def updatePlateparsAll(ppfile, manpp, pth):
    # read in the manual platepar_cmn2020.cal
    with open(manpp,'r') as minf:
        lis = minf.readlines()

    # set auto_recalibrated to true
    autoline = lis.index('    "auto_recalibrated": false,\n')
    lis[autoline] = '    "auto_recalibrated": true,\n'

    # get a list of FF files
    fflist = glob.glob1(pth, 'FF*.fits')

    # create a pseudo-platepars_all file for local solver purposes
    with open(os.path.join(pth, 'platepars_all_recalibrated.json'), 'w') as ppa:
        ppa.write('{\n')
        for fffile in fflist:
            ppa.write('\"{}\":\n'.format(fffile))
            ppa.writelines(lis)
            if fffile != fflist[-1]:
                ppa.write(',')
        ppa.write('\n}\n')

    # read in the original platepars_all file
    with open(ppfile, 'r') as ppa:
        origlis = ppa.readlines()

    # skip the top line, we're going to replace it
    reqlines = origlis[1:] 
    with open(ppfile, 'w') as ppa:
        ppa.write('{\n')
        for fffile in fflist:
            ppa.write('\"{}\":\n'.format(fffile))
            ppa.writelines(lis)
            ppa.write(',')
        ppa.writelines(reqlines)
    
    return


if __name__ == '__main__':
    pth = sys.argv[1]
    outpth = os.path.join(pth, 'upload')

    # find the four files required
    ftp = glob.glob1(pth, 'FTP*manual.txt')
    if len(ftp) < 1:
        print('FTPdetect file not found in {}, cannot continue'.format(pth))
        exit(1)
    else:
        manftp = os.path.join(pth, ftp[0])

    ftp = glob.glob1(outpth, 'FTP*.txt')
    if len(ftp) < 1:
        print('Original FTPdetect file not found in {}, cannot continue'.format(outpth))
        exit(1)
    else:
        ftpfile = os.path.join(outpth, ftp[0])
        bkpfile = os.path.join(outpth, 'bkp_' + ftp[0])
        shutil.copyfile(ftpfile, bkpfile)

    pp = glob.glob1(pth, 'platepar_cmn2010.cal')
    if len(pp) < 1:
        print('Recalibrated platepar file not found in {}, cannot continue'.format(pth))
        exit(1)
    else:
        manpp = os.path.join(pth, pp[0])

    pp = glob.glob1(outpth, 'platepars_all_recalibrated.json')
    if len(pp) < 1:
        print('Original platepars_all file not found in {}, cannot continue'.format(outpth))
        exit(1)
    else:
        ppfile = os.path.join(outpth, pp[0])
        bkpfile = os.path.join(outpth, 'bkp_' + pp[0])
        shutil.copyfile(ppfile, bkpfile)


    updateFTPfile(ftpfile, manftp)
    updatePlateparsAll(ppfile, manpp, pth)
