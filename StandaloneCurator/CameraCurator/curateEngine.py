# engine that curates an xmil/jpg pair
#

import os
import numpy
from UFOHandler import ReadUFOCapXML
Polynomial = numpy.polynomial.Polynomial

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
    dx = numpy.diff(x)
    adx = abs(numpy.diff(x))
    # if the differences are less than a few pixels, allow it
    if numpy.all(adx <= 5):
        return True
    # if the differences are all positive or all negative then its monotonic
    if numpy.all(dx >= 0) or numpy.all(dx <= 0):
        return True
    # else its not monotonic
    return False


def CheckifValidMeteor(xmlname, log=None):
    if os.path.isfile(xmlname) is False:
        msg = 'noxml, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(0, 0, 0, 0, 0, 0, 0, 0)
        return False, msg, 0, 0, 0, 0

    dd = ReadUFOCapXML.UCXml(xmlname)
    dd.setMaxGap(25)

    fps, cx, cy = dd.getCameraDetails()
    nobjs, objlist = dd.getNumObjs()
    isgood = 0
    if nobjs == 0:
        msg = 'nopaths, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(0, 0, 0, 0, 0, 0, 0, 0)
        log.info('objcount is zero')
        return False, msg, 0, 0, 0, 0

    if nobjs > MAXOBJS:
        msg = 'toomany, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}'.format(nobjs, 0, 0, 0, 0, 0, 0, 0)
        log.info('objcount too large')
        return False, msg, 0, 0, 0, 0
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

        res, msg = CheckALine(pathx, pathy, xmlname, fps, cx, cy, fnos, log)
        log.info('result was ' + str(res))
        if nobjs > 1:
            log.info('{:s}, {:d}'.format(msg, int(totpx)))
        if res == 1:
            goodmsg = msg
            gtp = totpx
        isgood = isgood + res

    # we want to hang on to bright events even if there are issues with the path
    # except if its too slow or
    errtyp = goodmsg.split(',')[0]
    stillbad = False
    if errtyp in ['tooslow', 'flash']:
        stillbad = True
        isgood = 0
    if totbri > MAXBRI and isgood == 0 and stillbad is False:
        goodmsg = msg

    log.info('isgood is ' + str(isgood))
    if isgood == 0:
        return False, msg, nobjs, int(max(bri)), int(gtp), int(tottotpx)
    else:
        return True, goodmsg, nobjs, int(max(bri)), int(gtp), int(tottotpx)


def leastsq1(x, y):
    a = numpy.vstack([x, numpy.ones(len(x))]).T
    return numpy.dot(numpy.linalg.inv(numpy.dot(a.T, a)), numpy.dot(a.T, y))


def CheckALine(pathx, pathy, xmlname, fps, cx, cy, fnos, log):
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
        log.info('nonmonotonic')
        badline = True
    plen = len(pathx)
    maxg = 0
    if plen > 1:
        maxg = int(max(numpy.diff(fnos)))
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
            rms = numpy.sqrt(resid[0] / len(pathx))
            log.info('rms is ' + str(rms))
            # if the line is nearly vertical, a fit of y wil be a poor estimate
            # so before discarding the data, try swapping the axes
            if rms > MAXRMS:
                cmin, cmax = min(pathy), max(pathy)
                pfit, stats = Polynomial.fit(pathy, pathx, 1, full=True, window=(cmin, cmax),
                        domain=(cmin, cmax))
                _, m = pfit
                resid, _, _, _ = stats
                rms2 = numpy.sqrt(resid[0] / len(pathy))
                if (pathy[-1] - pathy[0]) != 0:
                    app_m = (pathx[-1] - pathx[0]) / (pathy[-1] - pathy[0])
                rms2 = min(rms2, rms)
                rms = min(rms2, rms)
        except:
            log.info('fit failed')
            msg = 'fitfail, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
            return 0, msg

        # work out the length of the line; very short lines are statistically unreliable
        p1 = numpy.c_[pathx[0], pathy[0]]
        p2 = numpy.c_[pathx[-1], pathy[-1]]
        try:
            dist = numpy.linalg.norm(p2 - p1)
        except:
            log.info('vectors parallel')
            msg = 'parallel, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
            return 0, msg
        # very low RMS is improbable
        if rms > MAXRMS:
            msg = 'rmshigh, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
            log.info('high RMS')
            return 0, msg
        elif rms < 0.0001:
            msg = 'rmslow, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
            log.info('absurdly low RMS')
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
                log.info('flash')
                msg = 'flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                return 0, msg
            elif vel < 85:
                msg = 'tooslow, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                log.info('too slow')
                return 0, msg
            else:
                if badline is True:
                    msg = 'nonmono, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                    log.info('nonmono')
                    return 0, msg
                elif gappy is True:
                    msg = 'gappy, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                    log.info('gappy')
                    return 0, msg
                else:
                    msg = 'meteor, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, xm, ym, m, app_m, dist, vel, maxg)
                    log.info('hooray its a meteor')
                    return 1, msg
    else:
        if badline is True:
            msg = 'badline, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, int(xm), int(ym), m, app_m, dist, vel, maxg)
        else:
            if plen < MINLEN:
                msg = 'flash, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, int(xm), int(ym), m, app_m, dist, vel, maxg)
            else:
                msg = 'toolong, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), rms, int(xm), int(ym), m, app_m, dist, vel, maxg)
        log.info('various errors')
        return 0, msg
    msg = 'unknown, {:d}, {:.2f}, {:d}, {:d}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:d}'.format(len(pathx), 0, 0, 0, 0, 0, 0, 0, maxg)
    log.info('impossible to get here')
    return 0, msg
