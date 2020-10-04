# engine that curates an xmil/jpg pair
#

import os
import numpy as np
from UFOHandler import ReadUFOCapXML
Polynomial = np.polynomial.Polynomial

badfilepath = ''
logname = 'LiveMon: '
MAXRMS = 1
MINLEN = 4  # very short trails are statistically unreliable
MAXLEN = 100  # 50 frames is one second
MAXBRI = 1500
MAXOBJS = 20
MAXGAP = 75  # corresponds to 1.5 seconds gap in the meteor trail
debug = False


def monotonic(x):
    dx = np.diff(x)
    adx = abs(np.diff(x))
    # if the differences are less than a few pixels, allow it
    if np.all(adx <= 5):
        return True
    # if the differences are all positive or all negative then its monotonic
    if np.all(dx >= 0) or np.all(dx <= 0):
        return True
    # else its not monotonic
    return False


def CheckifValidMeteor(xmlname):
    if(os.path.isfile(xmlname) is False):
        msg = 'noxml, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(0, 0, 0, 0, 0, 0, 0, 0)
        return False, msg, 0, 0, 0

    dd = ReadUFOCapXML.UCXml(xmlname)
    dd.setMaxGap(25)

    fps, cx, cy = dd.getCameraDetails()
    nobjs, objlist = dd.getNumObjs()
    isgood = 0
    if nobjs == 0:
        msg = 'nopaths, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(0, 0, 0, 0, 0, 0, 0, 0)
        return False, msg, 0, 0, 0
    goodmsg = ''
    gtp = 0
    tottotpx = 0
    totbri = 0
    totpx = 0

    _, fn = os.path.split(xmlname)
    for i in range(nobjs):
        pathx, pathy, bri, pxls, fnos = dd.getPathv2(objlist[i])
        totpx = sum(pxls)
        totbri = totbri + sum(bri)
        tottotpx = tottotpx + totpx
        res, msg = CheckALine(pathx, pathy, xmlname, fps, cx, cy, fnos)
        if nobjs > 1:
            print('{:s}, {:d}'.format(msg, int(totpx)))
        if res == 1:
            goodmsg = msg
            gtp = totpx
        isgood = isgood + res

    print('totbri is ', totbri)
    # we want to hang on to bright events even if there are issues with the path
    # except if its too slow or
    errtyp = goodmsg.split(',')[0]
    stillbad = False
    if errtyp in ['tooslow', 'flash']:
        stillbad = True
        isgood = 0
    if totbri > MAXBRI and isgood == 0 and stillbad is False:
        goodmsg = msg

    if isgood == 0:
        return False, msg, nobjs, int(max(bri)), int(gtp), int(tottotpx)
    else:
        return True, goodmsg, nobjs, int(max(bri)), int(gtp), int(tottotpx)


def leastsq1(x, y):
    a = np.vstack([x, np.ones(len(x))]).T
    return np.dot(np.linalg.inv(np.dot(a.T, a)), np.dot(a.T, y))


def CheckALine(pathx, pathy, xmlname, fps, cx, cy, fnos):
    dist = 0
    app_m = 0
    m = 0
    ym = 0
    xm = 0
    vel = 0
    rms = 0

    # we expect meteor paths to be monotonic in X or Y or both
    # A path that darts about is unlikely to be analysable
    badline = False
    gappy = False
    if monotonic(pathx) is False and monotonic(pathy) is False:
        if debug is True:
            print(pathx, pathy)
            print(np.diff(pathx), np.diff(pathy))
        badline = True
    plen = len(pathx)
    maxg = 0
    if plen > 1:
        maxg = int(max(np.diff(fnos)))
        if maxg > MAXGAP:
            gappy = True

    # very short paths are stasticially unreliable
    # very long paths are unrealistic as meteors are pretty quick events
    if plen >= MINLEN and plen <= MAXLEN:
        try:
            cmin, cmax = min(pathx), max(pathx)
            pfit, stats = Polynomial.fit(pathx, pathy, 1, full=True, window=(cmin, cmax),
                    domain=(cmin, cmax))
            _, m = pfit
            if (pathx[-1] - pathx[0]) != 0:
                app_m = (pathy[-1] - pathy[0]) / (pathx[-1] - pathx[0])
            resid, _, _, _ = stats
            rms = np.sqrt(resid[0] / len(pathx))

            # if the line is nearly vertical, a fit of y wil be a poor estimate
            # so before discarding the data, try swapping the axes
            if rms > MAXRMS:
                cmin, cmax = min(pathy), max(pathy)
                pfit, stats = Polynomial.fit(pathy, pathx, 1, full=True, window=(cmin, cmax),
                        domain=(cmin, cmax))
                _, m = pfit
                resid, _, _, _ = stats
                rms2 = np.sqrt(resid[0] / len(pathy))
                if (pathy[-1] - pathy[0]) != 0:
                    app_m = (pathx[-1] - pathx[0]) / (pathy[-1] - pathy[0])
                rms2 = min(rms2, rms)
                rms = min(rms2, rms)
        except:
            msg = 'fitfail, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
            return 0, msg

        # work out the length of the line; very short lines are statistically unreliable
        p1 = np.c_[pathx[0], pathy[0]]
        p2 = np.c_[pathx[-1], pathy[-1]]
        try:
            dist = np.linalg.norm(p2 - p1)
        except:
            msg = 'parallel, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
            return 0, msg
        # very low RMS is improbable
        if rms > MAXRMS:
            msg = 'rmshigh, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
            return 0, msg
        elif rms < 0.0001:
            msg = 'rmslow, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
            return 0, msg
        else:
            vel = dist * 2 * fps / plen
            xm = int(max(pathx))
            if xm > cx / 2:
                xm = int(min(pathx))
            ym = int(min(pathy))
            if ym > cy / 2:
                ym = int(min(pathy))
            if dist < 10 and vel < 100:
                msg = 'flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                return 0, msg
            elif vel < 85:
                msg = 'tooslow, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                return 0, msg
            else:
                if badline is True:
                    msg = 'nonmono, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                    return 0, msg
                elif gappy is True:
                    msg = 'gappy, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                    return 0, msg
                else:
                    msg = 'meteor, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                    return 1, msg
    else:
        if badline is True:
            msg = 'badline, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, int(xm), int(ym), m, app_m, dist, vel, maxg)
        else:
            if plen < MINLEN:
                msg = 'flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, int(xm), int(ym), m, app_m, dist, vel, maxg)
            else:
                msg = 'toolong, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, int(xm), int(ym), m, app_m, dist, vel, maxg)
        return 0, msg
    msg = 'unknown, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), 0, 0, 0, 0, 0, 0, 0, maxg)
    return 0, msg
