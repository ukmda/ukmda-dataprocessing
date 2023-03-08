""" Loading CAMS file products, FTPDetectInfo and CameraSites files, running the
    trajectory solver on loaded data.

"""
# Copyright (C) 2018-2023 Mark McIntyre

from __future__ import print_function, division, absolute_import

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import datetime

from wmpl.Utils.Math import mergeClosePoints, angleBetweenSphericalCoords
from wmpl.Utils.SolarLongitude import date2JD
from wmpl.Utils.TrajConversions import jd2Date    
from wmpl.Utils.Physics import calcMass
from ShowerAssociation import associateShower
from wmpl.Utils.Earth import greatCircleDistance
from wmpl.Config import config


def sollon2jd(Year, Month, Long):

    Long = np.radians(Long)
    N = Year - 2000
    if abs(N) > 100:
        print("Algorithm is not stable for years below 1900 or above 2100")

    JDM0 = 2451182.24736 + 365.25963575 * N
    ApproxJD = date2JD(Year, Month, 15, 12, 0, 0)
    DiffJD = ApproxJD-2451545

    Dt = 1.94330 * np.sin(Long - 1.798135) + 0.01305272 * np.sin(2*Long + 2.634232) + 78.195268 + 58.13165 * Long - 0.0000089408 * DiffJD

    if abs(ApproxJD - (JDM0 + Dt))>50:
        Dt = Dt + 365.2596

    JD1 = JDM0 + Dt

    return JD1


def getShowerDets(shwr):
    sfd = np.load(config.iau_shower_table_npy)
    sfdfltr = sfd[sfd[:,3] == shwr]
    mtch = [sh for sh in sfdfltr if sh[6] != '-2']
    if len(mtch) == 0:
        return 0, 'Unknown', 0, 'Unknown'

    id = int(mtch[-1][1])
    nam = mtch[-1][4].strip()
    pksollong = float(mtch[-1][7])
    dt = datetime.datetime.now()
    yr = dt.year
    mth = dt.month
    jd = sollon2jd(yr, mth, pksollong)
    pkdt = jd2Date(jd, dt_obj=True)
    return id, nam, pksollong, pkdt.strftime('%m-%d')


def createUFOOrbitFile(traj, outdir, amag, mass, shower_obj):
    #print('Creating UFO Orbit style output file')
    orb = traj.orbit
    if shower_obj is None:
        shid = -1
        shcod = 'spo'
        shname = 'Sporadic'
    else:
        shid = shower_obj.IAU_no
        shcod = shower_obj.IAU_code
        shname = shower_obj.IAU_name

    dt = jd2Date(traj.jdt_ref, dt_obj=True)
    dtstr = jd2Date(traj.jdt_ref, dt_obj=True).strftime("%Y%m%d-%H%M%S.%f")
    secs = dt.second + dt.microsecond / 1000000
    nO = len(traj.observations)
    id = '_(UNIFIED_' + str(nO) + ')'
    if orb.L_g is not None:
        lasun = np.degrees(orb.la_sun)
        lg = np.degrees(orb.L_g)
        bg = np.degrees(orb.B_g)
    else:
        lasun = 0
        lg = 0
        bg = 0
    vg = orb.v_g / 1000
    vh = orb.v_h / 1000
    LD21 = 0
    omag = 99  # ludicrous value to ensure convergence
    dur = 0
    totsamp = 0
    d_t = max(abs(traj.time_diffs_final))
    for obs in traj.observations:
        LD21 = max(max(obs.length), LD21)
        omag = min(min(obs.magnitudes), omag)
        dur = max(max(obs.time_data) - min(obs.time_data), dur)
        totsamp += len(obs.magnitudes)
    LD21 /= 1000
    leap = (totsamp - nO) / totsamp * 100.0

    rao = np.degrees(orb.ra)
    dco = np.degrees(orb.dec)
    rat = np.degrees(orb.ra_g)
    dct = np.degrees(orb.dec_g)
    vo = orb.v_init / 1000
    vi = vo
    az1r = np.degrees(orb.azimuth_apparent)
    ev1r = np.degrees(orb.elevation_apparent)

    if shower_obj is None:
        dr = -1
        dvpct = -1
    else:
        dr = angleBetweenSphericalCoords(shower_obj.B_g, shower_obj.L_g, bg, (lg - lasun) % (2 * np.pi))
        dvpct = np.abs(100 * (shower_obj.v_g - vg * 1000) / shower_obj.v_g)

    # the below fields are specific to the way UFOOrbit calculates
    Qo, GPlng, GPlat = 0, 0, 0
    evrt = 0
    ddeg, cdeg = 0, 0
    Qc, dGP, Gmpct, dv12pct = 0, 0, 0, 0
    zmv, QA = 0, 1
    vo_sd = 0
    ZF, OH, ZHR = 0, 0, 0

    # create CSV file in UFOOrbit format
    #print('create orbit csv')
    weburl = os.getenv('WEBURL', default='https://archive.ukmeteornetwork.co.uk')
    urlbase = f'{weburl}/reports/{dtstr[:4]}/orbits/{dtstr[:6]}/{dtstr[:8]}'
    csvname = os.path.join(outdir, dtstr + '_orbit_full.csv')
    with open(csvname, 'w', newline='') as csvf:
        csvf.write('RMS,0,')
        csvf.write('{:s}, {:.10f}, {:.6f}, {:s}, {:s}, {:.6f}, '.format(dt.strftime('_%Y%m%d_%H%M%S'), traj.jdt_ref - 2400000.5, lasun, id, '_', amag))
        csvf.write('{:.6f}, {:.6f}, {:.6f}, {:.6f}, '.format(rao, dco, rat, dct))
        csvf.write('{:.6f}, {:.6f}, {:.6f}, {:.6f}, {:.6f}, {:.6f}, '.format(lg, bg, vo, vi, vg, vh))
        csvf.write('{:.6f}, {:.6f}, {:.6f}, {:.6f}, '.format(orb.a, orb.q, orb.e, orb.T))
        csvf.write('{:.6f}, {:.6f}, {:.6f}, '.format(np.degrees(orb.peri), np.degrees(orb.node), np.degrees(orb.i)))
        csvf.write('{:s}, '.format(shcod))
        csvf.write('{:.6f}, {:.6f}, {:.6f}, {:.6f}, {:.6f}, '.format(dr, dvpct, omag, Qo, dur))
        csvf.write('0, 0, 0, 0, ')  # av Voa Pra Pdc always zero in Unified orbits
        csvf.write('{:.6f}, {:.6f}, '.format(GPlng, GPlat))
        csvf.write('0, 0, 0, 0, ')  # ra1 dc1 az1 ev1 always zero in Unified orbits
        csvf.write('{:.6f}, {:.6f}, {:.6f}, '.format(np.degrees(traj.rbeg_lon), np.degrees(traj.rbeg_lat), traj.rbeg_ele / 1000))
        csvf.write('0, 0, 0, 0, 0, ')  # LD1 Qr1 Qd1 ra2 rc2 always zero in Unified orbits
        csvf.write('{:.6f}, {:.6f}, {:.6f}, '.format(np.degrees(traj.rend_lon), np.degrees(traj.rend_lat), traj.rend_ele / 1000))
        csvf.write('0, 0, 0, ')  # LD2 Qr2 Qd2 always zero in Unified orbits
        csvf.write('{:.6f}, {:.6f}, {:.6f}, 0, {:.6f}, '.format(LD21, az1r, ev1r, evrt))
        csvf.write('{:d}, {:d}, {:.6f}, 0, {:.6f}, {:.6f}, '.format(totsamp, nO, leap, ddeg, cdeg))
        csvf.write('0, 0, 1, ')  # drop, inout, tme always zero in Unified orbits
        csvf.write('{:.6f}, 0, {:.6f}, {:.6f}, {:.6f}, {:.6f}, '.format(d_t, Qc, dGP, Gmpct, dv12pct))  # GD
        csvf.write('{:.6f}, 0, 0, {:.6f}, '.format(zmv, QA))  # Ed Ex always zero in Unified orbits
        csvf.write('{:s}, {:s}, {:s}, {:s}, {:s}, {:.6f}, '.format(dtstr[:4], dtstr[4:6], dtstr[6:8],
            dtstr[9:11], dtstr[11:13], secs))
        csvf.write('{:d}, '.format(nO))
        csvf.write('0, 0, 0, 0, ')  # Qp pole_sd rao_sd dco_sd always zero in UO
        csvf.write('{:.6f}, '.format(vo_sd))
        csvf.write('0, 0, 0, 0, ')  # rat_sd dct_sd vg_sd a_sd always zero in UO
        csvf.write('{:.6f}, '.format(1 / orb.a))
        csvf.write('0, 0, 0, 0, 0, 0, 0, ')  # 1/a_sd q_sd e_sd peri_sd node_sd incl_sd Er_sd always zero in UO
        csvf.write('{:.6f}, {:.6f}, {:.6f}, '.format(ZF, OH, ZHR))
        csvf.write('0, 0, 0,') # three dummy values, not sure why! 

        csvf.write('{:6f},'.format(jd2Date(traj.jdt_ref, dt_obj=True).timestamp()))
        _, orbname =os.path.split(outdir)
        csvf.write('{},'.format(orbname))
        csvf.write('1Matched,')
        csvf.write('{}/{}/index.html,'.format(urlbase, orbname))
        csvf.write('{}/{}/{}_ground_track.png,'.format(urlbase, orbname, orbname[:15]))

        csvf.write('{:s}, {:.10f}, {:s}, '.format(dt.strftime('%Y%m%d_%H%M%S'), traj.jdt_ref-2400000.5, id))
        csvf.write('{:d}, {:s}, {:.6f}, '.format(shid, shname, mass))
        csvf.write('{:.6f}, {:.6f}, {:.6f}, '.format(np.degrees(orb.pi), orb.Q, np.degrees(orb.true_anomaly)))
        csvf.write('{:.6f}, {:.6f}, {:.6f}, '.format(np.degrees(orb.eccentric_anomaly), np.degrees(orb.mean_anomaly), orb.Tj))
        csvf.write('{:.6f}, '.format(orb.T))
        if orb.last_perihelion is not None:
            csvf.write('{:s}, '.format(orb.last_perihelion.strftime('%Y-%m-%d')))
        else:
            csvf.write('9999-99-99, ')
        csvf.write('{:.6f}, {:.6f}, '.format(traj.jacchia_fit[0], traj.jacchia_fit[1]))

        statlist = ''
        for obs in traj.observations:
            statlist = statlist + str(obs.station_id) + ';'
        csvf.write('{:d}, {:s}'.format(nO, statlist))
        if omag < -3.999:
            csvf.write(',True')
        else:
            csvf.write(',False')
        csvf.write('\n')
    return


class MeteorObservation(object):
    """ Container for meteor observations.
        The loaded points are RA and Dec in J2000 epoch, in radians.
    """
    def __init__(self, jdt_ref, station_id, latitude, longitude, height, fps, ff_name=None, isj2000=True):
        self.jdt_ref = jdt_ref
        self.station_id = station_id
        self.latitude = latitude
        self.longitude = longitude
        self.height = height
        self.fps = fps
        self.ff_name = ff_name
        # flag to indicate whether data is as-of-epoch or J2000
        self.isj2000 = isj2000
        self.frames = []
        self.time_data = []
        self.x_data = []
        self.y_data = []
        self.azim_data = []
        self.elev_data = []
        self.ra_data = []
        self.dec_data = []
        self.mag_data = []
        self.abs_mag_data = []

    def addPoint(self, frame_n, x, y, azim, elev, ra, dec, mag):
        """ Adds the measurement point to the meteor.

        Arguments:
            frame_n: [flaot] Frame number from the reference time.
            x: [float] X image coordinate.
            y: [float] X image coordinate.
            azim: [float] Azimuth, J2000 in degrees.
            elev: [float] Elevation angle, J2000 in degrees.
            ra: [float] Right ascension, J2000 in degrees.
            dec: [float] Declination, J2000 in degrees.
            mag: [float] Visual magnitude.

        """

        self.frames.append(frame_n)

        # Calculate the time in seconds w.r.t. to the reference JD
        point_time = float(frame_n) / self.fps

        self.time_data.append(point_time)

        self.x_data.append(x)
        self.y_data.append(y)

        # Angular coordinates converted to radians
        self.azim_data.append(np.radians(azim))
        self.elev_data.append(np.radians(elev))
        self.ra_data.append(np.radians(ra))
        self.dec_data.append(np.radians(dec))
        self.mag_data.append(mag)

    def finish(self):
        """ When the initialization is done, convert data lists to numpy arrays. """

        self.frames = np.array(self.frames)
        self.time_data = np.array(self.time_data)
        self.x_data = np.array(self.x_data)
        self.y_data = np.array(self.y_data)
        self.azim_data = np.array(self.azim_data)
        self.elev_data = np.array(self.elev_data)
        self.ra_data = np.array(self.ra_data)
        self.dec_data = np.array(self.dec_data)
        self.mag_data = np.array(self.mag_data)

        # Sort by frame
        temp_arr = np.c_[self.frames, self.time_data, self.x_data, self.y_data, self.azim_data,
        self.elev_data, self.ra_data, self.dec_data, self.mag_data]
        temp_arr = temp_arr[np.argsort(temp_arr[:, 0])]
        self.frames, self.time_data, self.x_data, self.y_data, self.azim_data, self.elev_data, self.ra_data, \
            self.dec_data, self.mag_data = temp_arr.T

    def __repr__(self):

        out_str = ''

        out_str += 'Station ID = ' + str(self.station_id) + '\n'
        out_str += 'JD ref = {:f}'.format(self.jdt_ref) + '\n'
        out_str += 'DT ref = {:s}'.format(jd2Date(self.jdt_ref,
            dt_obj=True).strftime("%Y/%m/%d-%H%M%S.%f")) + '\n'
        out_str += 'Lat = {:f}, Lon = {:f}, Ht = {:f} m'.format(np.degrees(self.latitude),
            np.degrees(self.longitude), self.height) + '\n'
        out_str += 'FPS = {:f}'.format(self.fps) + '\n'
        out_str += 'J2000 {:s}\n'.format(str(self.isj2000))

        out_str += 'Points:\n'
        out_str += 'Time, X, Y, azimuth, elevation, RA, Dec, Mag:\n'

        for point_time, x, y, azim, elev, ra, dec, mag in zip(self.time_data, self.x_data, self.y_data,
                self.azim_data, self.elev_data, self.ra_data, self.dec_data, self.mag_data):

            if mag is None:
                mag = 0

            out_str += '{:.4f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:.2f}, {:+.2f}, {:.2f}\n'.format(point_time,
                x, y, np.degrees(azim), np.degrees(elev), np.degrees(ra), np.degrees(dec), mag)

        return out_str


def computeAbsoluteMagnitudes(traj, meteor_list):
    """ Given the trajectory, compute the absolute mangitude (visual mangitude @100km). """

    # Go though every observation of the meteor
    for i, meteor_obs in enumerate(meteor_list):

        # Go through all magnitudes and compute absolute mangitudes
        if traj is not None:
            for dist, mag in zip(traj.observations[i].model_range, meteor_obs.mag_data):

                # Skip nonexistent magnitudes
                if mag is not None:

                    # Compute the range-corrected magnitude
                    abs_mag = mag + 5 * np.log10((10**5) / dist)

                else:
                    abs_mag = None
                # print(mag, abs_mag, dist)
                meteor_obs.abs_mag_data.append(abs_mag)
        else:
            meteor_obs.abs_mag_data.append(6)


def draw3Dmap(traj, outdir):
    #print('creating 3d image')
    lats = []
    lons = []
    alts = []
    lens = []
    # Go through observation from all stations
    for obs in traj.observations:
        # Go through all observed points
        for i in range(obs.kmeas):
            lats.append(round(np.degrees(obs.model_lat[i]),4))
            lons.append(round(np.degrees(obs.model_lon[i]),4))
            alts.append(obs.model_ht[i])
            lens.append(obs.time_data[i])
    df = pd.DataFrame({"lats": lats, "lons": lons, "alts": alts, "times": lens})
    df = df.sort_values(by=['times', 'lats'])
    dtstr = jd2Date(traj.jdt_ref, dt_obj=True).strftime("%Y%m%d-%H%M%S.%f")
    csvname = os.path.join(outdir, dtstr + '_track.csv')
    df.to_csv(csvname, index=False)
    #print('plotting ')
    df = df.drop(columns=['times'])
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(df.lats, df.lons, df.alts, linewidth=2)
    ax.set_xlabel('Latitude')
    ax.set_ylabel('Longitude')
    ax.set_zlabel('Altitude')
    f3dname = os.path.join(outdir, dtstr[:15].replace('-','_') + '_3dtrack.png')
    plt.savefig(f3dname, dpi=200)
    plt.close()
    return


def loadMagData(traj):
    magdata=[]
    stations = []
    vmags = []
    for obs in traj.observations:
        thisobs = MeteorObservation(0,'',0,0,0,0,'')
        thisobs.mag_data = obs.magnitudes
        magdata.append(thisobs)
        vmags.append(min(obs.magnitudes))
        stations.append(obs.station_id)
    return magdata, stations, vmags


def calcAdditionalValues(traj):
    # # Compute  mangitudes
    magdata, stations, vmags = loadMagData(traj)
    computeAbsoluteMagnitudes(traj, magdata)
    bestvmag = min(vmags)

    # # List of photometric uncertainties per station
    photometry_stddevs = [0.3] * len(magdata)

    time_data_all = []
    abs_mag_data_all = []
    bestamag = 6
    # # Plot absolute magnitudes for every station
    for i, (meteor_obs, photometry_stddev) in enumerate(zip(magdata, photometry_stddevs)):

        # Take only magnitudes that are not None
        good_mag_indices = [j for j, abs_mag in enumerate(meteor_obs.abs_mag_data) if abs_mag is not None]
        time_data = traj.observations[i].time_data[good_mag_indices]
        abs_mag_data = np.array(meteor_obs.abs_mag_data)[good_mag_indices]
        tmpamag= min(abs_mag_data)
        bestamag = min(tmpamag, bestamag)
        time_data_all += time_data.tolist()
        abs_mag_data_all += abs_mag_data.tolist()

    # Sort by time
        temp_arr = np.c_[time_data, abs_mag_data]
        temp_arr = temp_arr[np.argsort(temp_arr[:, 0])]
        time_data, abs_mag_data = temp_arr.T

    # # Sort by time
    temp_arr = np.c_[time_data_all, abs_mag_data_all]
    temp_arr = temp_arr[np.argsort(temp_arr[:, 0])]
    time_data_all, abs_mag_data_all = temp_arr.T

    # # Average the close points
    time_data_all, abs_mag_data_all = mergeClosePoints(time_data_all, abs_mag_data_all, 1 / (2 * 25))

    time_data_all = np.array(time_data_all)
    abs_mag_data_all = np.array(abs_mag_data_all)

    # print('about to calc mass')
    # # Compute the mass
    mass = calcMass(time_data_all, abs_mag_data_all, traj.v_avg, P_0m=1210)

    shower_obj = None  # initialise this
    orb = traj.orbit
    if orb.L_g is not None:
        lg = np.degrees(orb.L_g)
        bg = np.degrees(orb.B_g)
        vg = orb.v_g
        shower_obj = associateShower(orb.la_sun, orb.L_g, orb.B_g, orb.v_g)
        if shower_obj is None:
            id = -1
            cod = 'spo'
            shwrname='Sporadic'
        else:
            id = shower_obj.IAU_no
            cod = shower_obj.IAU_code
            _, shwrname, _, _ = getShowerDets(cod)
    else:
        # no orbit was calculated
        lg = 0
        bg = 0
        vg = 0
        shower_obj = None
        id = -1
        cod = 'spo'
        shwrname='Sporadic'

    return bestamag, bestvmag, mass, id, cod, shwrname, orb, shower_obj, lg, bg, vg, stations


def createAdditionalOutput(traj, outdir):
    # calculate the values
    amag, vmag, mass, id, cod, shwrname, orb, shower_obj, lg, bg, vg, _ = calcAdditionalValues(traj)

    if id != -1:
        iau_link= f'https://www.ta3.sk/IAUC22DB/MDC2007/Roje/pojedynczy_obiekt.php?kodstrumienia={id:05d}'

    # create Summary report for webpage
    #print('creating summary report')
    summrpt = os.path.join(outdir, 'summary.html')

    if traj.save_results:
        #print('saving results to file')
        with open(summrpt, 'w', newline='') as f:
            f.write('Summary for Event\n')
            f.write('-----------------\n')
            dt = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            f.write(f'Updated: {dt}\n\n')
            if orb is not None:
                if id == -1:
                    f.write('shower ID {:d} {:s} ({:s})\n'.format(id, cod, shwrname))
                else:
                    f.write('shower ID {:d} {:s} '.format(id, cod))
                    f.write('<a href={:s}>({:s})</a>\n'.format(iau_link, shwrname))

                if orb.L_g is not None:
                    f.write('Lg {:.2f}&deg; Bg {:.2f}&deg; Vg {:.2f}km/s\n'.format(lg, bg, vg / 1000))

                if mass*1000 < 10:
                    f.write('mass {:.2}g, abs. mag {:.1f}\nbest visual mag {:.1f}\n'.format(mass * 1000, amag, vmag))
                else:
                    f.write('mass {:.0f}g, abs. mag {:.1f}\nbest visual mag {:.1f}\n'.format(mass * 1000, amag, vmag))
                f.write('Mass is a lower estimate based on the measured emitted energy and will significantly underestimate the mass of bright events.\n')
            else:
                f.write('unable to calculate realistic shower details\n')
            f.write('\nPath Details\n')
            f.write('------------\n')
            f.write('start {:.2f}&deg; {:.2f}&deg; {:.2f}km\n'.format(np.degrees(traj.rbeg_lon), np.degrees(traj.rbeg_lat), traj.rbeg_ele / 1000))
            f.write('end   {:.2f}&deg; {:.2f}&deg; {:.2f}km\n\n'.format(np.degrees(traj.rend_lon), np.degrees(traj.rend_lat), traj.rend_ele / 1000))
            tracklen = greatCircleDistance(traj.rbeg_lat, traj.rbeg_lon, traj.rend_lat, traj.rend_lon)*1000
            vertdist = traj.rbeg_ele - traj.rend_ele
            if abs(tracklen) < 1:
                aoe = 90
            else:
                aoe = np.degrees(np.arctan(vertdist/tracklen))
            f.write(f'approx track length {tracklen/1000:.1f} km\n')
            f.write(f'approx angle of entry {aoe:.0f}&deg; from horizontal\n\n')
            f.write('Orbit Details\n')
            f.write('-------------\n')
            if orb.L_g is not None:
                f.write('Semimajor axis {:.2f}A.U., eccentricity {:.2f}, inclination {:.2f}&deg;, '.format(orb.a, orb.e, np.degrees(orb.i)))
                f.write('Period {:.2f}Y, LA Sun {:.2f}&deg;, '.format(orb.T, np.degrees(orb.la_sun)))
                if orb.last_perihelion is not None:
                    f.write('last Perihelion {:s}'.format(orb.last_perihelion.strftime('%Y-%m-%d')))
                f.write('\n')
            else:
                f.write('unable to calculate realistic orbit details\n')
            f.write('\nFull details below\n')

        #print('saved')
    if orb is not None:
        #print('create ufo file and 3d image')
        try:
            #print(amag, mass, shower_obj)
            createUFOOrbitFile(traj, outdir, amag, mass, shower_obj)
        except Exception:
            print('problem creating UFO style output')
        #print('drawing 3d')
        draw3Dmap(traj, outdir)
    else:
        print('no orbit object')

    #print('done')
    return 
