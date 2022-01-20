import requests
import sys

def getECSVs(stat, dt, savefiles=False):
    apiurl='https://jpaq0huazc.execute-api.eu-west-1.amazonaws.com/Prod/getecsv?stat={}&dt={}'
    res = requests.get(apiurl.format(stat, dt))
    ecsvlines=''
    if res.status_code == 200:
        rawdata=res.text.strip()
        if len(rawdata) > 10:
            ecsvlines=rawdata.split('\n') # convert the raw data into a python list
            numecsvs = len([e for e in ecsvlines if '# %ECSV' in e]) # find out how many meteors 
            fnamebase = dt.replace(':','_').replace('.','_') # create an output filename
            if savefiles is True:
                if numecsvs == 1:
                    print('saving to ', fnamebase+ '.ecsv')
                    with open(fnamebase + '.ecsv', 'w') as outf:
                        outf.writelines(ecsvlines)
                else:
                    outf = None
                    j=1
                    for i in range(len(ecsvlines)):
                        if '# %ECSV' in ecsvlines[i]:
                            if outf is not None:
                                outf.close()
                                j=j+1
                            outf = open(fnamebase + f'_M{j:03d}.ecsv', 'w')
                            print('saving to ', fnamebase + f'_M{j:03d}.ecsv')
                        outf.write(f'{ecsvlines[i]}\n')
        else:
            print('no error, but no data returned')
    else:
        print(res.status_code)
    return ecsvlines

if __name__ == '__main__':
    sav = True
    if len(sys.argv) < 3:
        stat ='UK0025'
        dt = '2021-07-17T02:41:05.05'
    else:
        stat = sys.argv[1]
        dt = sys.argv[2]
        if len(sys.argv) == 4:
            if int(sys.argv[3]) ==0:
                sav = False

    getECSVs(stat, dt, sav)