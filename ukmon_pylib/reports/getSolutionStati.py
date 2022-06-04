#
# Get list of orbits attempted with their status
#  
import sys


def getSolutionStati(fname):
    with open(fname, 'r') as inf:
        lis = inf.readlines()
    # find start of interesting data
    totnew = 0
    totchk = 0
    gotnew = 0
    gotchk = 0
    chktraj = False
    newtraj = False
    for li in lis:
        # check for new data for existing solns 
        if 'Checking trajectory at ' in li and chktraj is False:
            thistraj = li
            chktraj = True
            totchk += 1
            continue
        if 'Checking trajectory at ' in li and chktraj is True:
            spls = thistraj.strip().split(' ')
            print(f'{spls[3]} {spls[4]} no new data')
            totchk += 1
            thistraj = li
            chktraj = True
            continue
        if "New Trajectory solution failed" in li and chktraj is True:
            spls = thistraj.strip().split(' ')
            print(f'{spls[3]} {spls[4]} no improvement')
            chktraj = False
            continue
        if "Shower:" in li and chktraj is True:
            spls = thistraj.strip().split(' ')
            spl2 = li.strip().split(' ')
            if spl2[3] == '...':
                shwr = 'Spo'
            else:
                shwr = spl2[3]
            print(f'{spls[3]} {spls[4]} updated as {shwr}')
            gotchk += 1
            chktraj = False
            continue

        # check for new groups
        if "Observations:" in li:
            thistraj = None
            newtraj = True
            totnew += 1
            continue
        if "Observations:" not in li and newtraj is True and thistraj is None:
            thistraj = li
            continue
        if "-------" in li and newtraj is True:
            spls = thistraj.strip().split(' ')
            print(f'{spls[3]} {spls[4]} not matched')
            newtraj = False
            thistraj = None
            continue
        if "Shower:" in li and newtraj is True:
            spls = thistraj.strip().split(' ')
            spl2 = li.strip().split(' ')
            if spl2[3] == '...':
                shwr = 'Spo'
            else:
                shwr = spl2[3]
            print(f'{spls[3]} {spls[4]} solved as {shwr}')
            gotnew += 1
            newtraj = False
            thistraj = None
            continue
        if "SOLVING RUN DONE" in li:
            break

    return totnew, totchk, gotnew, gotchk 


if __name__ == '__main__':
    fname = sys.argv[1]
    print(getSolutionStati(fname))
